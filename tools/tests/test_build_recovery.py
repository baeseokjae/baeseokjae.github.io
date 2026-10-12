import importlib.util
import hashlib
import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).parents[1]))
import build_contract
import notify_publication as notifications
import verify_deployed


class BuildContractTests(unittest.TestCase):
    def test_missing_contract_never_builds(self):
        with tempfile.TemporaryDirectory() as root,patch('build_contract.command') as cmd:
            with self.assertRaises(OSError):build_contract.verify(Path(root))
            cmd.assert_not_called()

    def test_binary_mismatch_blocks_before_theme_or_build(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root);binary=p/'hugo';binary.write_bytes(b'untrusted')
            (p/'hugo.toml').write_bytes(b'')
            (p/'.hugo-build.json').write_text(json.dumps({'version':1,'config_sha256':hashlib.sha256(b'').hexdigest(),'flags':['--minify','--buildFuture','--environment','production'],'binary_sha256':{'arm64':'wrong'}}))
            with patch('build_contract.shutil.which',return_value=str(binary)),patch('build_contract.platform.machine',return_value='aarch64'),patch('build_contract.command') as cmd:
                with self.assertRaisesRegex(ValueError,'binary differs'):build_contract.verify(p)
                cmd.assert_not_called()

    def test_version_and_dirty_theme_mismatches_block(self):
        import hashlib
        for bad in ('version','theme','dirty'):
            with self.subTest(bad=bad),tempfile.TemporaryDirectory() as root:
                p=Path(root);binary=p/'hugo';binary.write_bytes(b'official')
                (p/'hugo.toml').write_bytes(b'')
                config={'version':1,'hugo_version':'0.163.3','theme_commit':'theme','config_sha256':hashlib.sha256(b'').hexdigest(),
                        'flags':['--minify','--buildFuture','--environment','production'],
                        'binary_sha256':{'arm64':hashlib.sha256(b'official').hexdigest()}}
                (p/'.hugo-build.json').write_text(json.dumps(config))
                outputs=['hugo v0.146.0+extended' if bad=='version' else 'hugo v0.163.3+extended',
                         '160000 commit theme\tthemes/PaperMod','other' if bad=='theme' else 'theme',' M file' if bad=='dirty' else '']
                with patch('build_contract.shutil.which',return_value=str(binary)),patch('build_contract.platform.machine',return_value='aarch64'),patch('build_contract.command',side_effect=outputs):
                    with self.assertRaises(ValueError):build_contract.verify(p)


class NotificationTests(unittest.TestCase):
    def setUp(self):
        self.commit='a'*40;self.verification={'status':'verified','source_commit':self.commit}
        self.posts=[{'title':'A < B & safe'}];self.tags={};self.ref=None;self.calls=[]
        def api(repo,path,method='GET',body=None):
            self.calls.append((path,method))
            if method=='GET' and path.startswith('git/ref/'):
                if self.ref is None:raise urllib.error.HTTPError('https://example.invalid',404,'missing',{},None)
                return {'object':{'sha':self.ref}}
            if method=='GET' and path.startswith('git/tags/'):return self.tags[path.split('/')[-1]]
            if method=='POST' and path=='git/tags':
                ident=str(len(self.tags)+1);self.tags[ident]={'message':body['message']};return {'sha':ident}
            if method in ('POST','PATCH'):
                self.ref=body['sha'];return {}
            raise AssertionError((path,method))
        self.patch=patch.object(notifications,'github',side_effect=api);self.patch.start();self.addCleanup(self.patch.stop)

    def test_send_only_after_public_verification_and_escape_title(self):
        sent=[]
        def send(text):sent.append(text);return {'ok':True,'result':{'message_id':7}}
        with self.assertRaises(ValueError):notifications.notify('r',self.commit,{},self.posts,send)
        self.assertEqual(self.calls,[])
        result=notifications.notify('r',self.commit,self.verification,self.posts,send)
        self.assertEqual(result['message_id'],7);self.assertIn('A &lt; B &amp; safe',sent[0])
        again=notifications.notify('r',self.commit,self.verification,self.posts,send)
        self.assertEqual(again['status'],'sent');self.assertEqual(len(sent),1)

    def test_response_loss_preserves_intent_and_never_blindly_resends(self):
        calls=[]
        def lost(text):calls.append(text);raise TimeoutError('response lost')
        with self.assertRaises(TimeoutError):notifications.notify('r',self.commit,self.verification,self.posts,lost)
        result=notifications.notify('r',self.commit,self.verification,self.posts,lost)
        self.assertEqual(result['status'],'delivery_unknown');self.assertEqual(len(calls),1)

    def test_correction_without_new_post_does_not_send_or_create_ledger(self):
        result=notifications.notify('r',self.commit,self.verification,[],lambda _:self.fail('unexpected send'))
        self.assertEqual(result['status'],'not_required');self.assertEqual(self.calls,[])

    def test_server_rejection_is_not_a_publication_retry(self):
        with self.assertRaises(ValueError):notifications.notify('r',self.commit,self.verification,self.posts,lambda _: {'ok':False})
        result=notifications.notify('r',self.commit,self.verification,self.posts,lambda _: self.fail('duplicate send'))
        self.assertEqual(result['status'],'delivery_unknown')


class LiveVerificationTests(unittest.TestCase):
    def test_superseded_commit_stops_without_fetching_articles(self):
        with patch('verify_deployed.gh',return_value={'object':{'sha':'other'}}),patch('verify_deployed.urllib.request.urlopen') as http:
            with self.assertRaises(RuntimeError):verify_deployed.verify_once('r','expected',Path('/missing'),[])
            http.assert_not_called()

    def test_unbuilt_or_wrong_pages_never_passes(self):
        for pages in [{'status':'building'},{'status':'built','commit':'old'}]:
            with patch('verify_deployed.gh',side_effect=[{'object':{'sha':'source'}},pages,{'object':{'sha':'new'}}]):
                with self.assertRaises(verify_deployed.GateError):verify_deployed.verify_once('r','source',Path('/missing'),[])


if __name__=='__main__':unittest.main()
