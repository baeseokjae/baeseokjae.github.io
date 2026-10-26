import json
from pathlib import Path
import sys,tempfile,unittest,urllib.error
from unittest.mock import Mock,patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import indexnow_notify as mod
from publication_gate import SITE

class IndexNowTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.key='a'*32;self.commit='b'*40
        (self.root/'static').mkdir();(self.root/'static'/f'{self.key}.txt').write_text(self.key)
        p=self.root/'public/posts/example/index.html';p.parent.mkdir(parents=True)
        p.write_text(f'<head><link rel="canonical" href="{SITE}/posts/example/"><meta name="robots" content="index, follow"></head>')
        self.config={'version':1,'enabled':True,'key':self.key}
        self.verification={'status':'verified','source_commit':self.commit,'pages_commit':'c'*40,'slugs':['example']}
        self.changes=['content/posts/example.md'];self.tags={};self.refs={};self.counter=0;self.calls=[]
    def gh(self,repo,path,method='GET',body=None):
        self.calls.append((path,method))
        if path.startswith('git/ref/'):
            name=path.removeprefix('git/ref/')
            if name not in self.refs:raise urllib.error.HTTPError('https://api.github.com',404,'not found',{},None)
            return {'object':{'sha':self.refs[name]}}
        if path.startswith('git/tags/'):return {'message':self.tags[path.removeprefix('git/tags/')]}
        if path=='git/tags':
            self.counter+=1;key=str(self.counter);self.tags[key]=body['message'];return {'sha':key}
        if path=='git/refs':
            name=body['ref'].removeprefix('refs/')
            if name in self.refs:raise RuntimeError('ref exists')
            self.refs[name]=body['sha'];return {}
        if path.startswith('git/refs/'):
            self.refs[path.removeprefix('git/refs/')]=body['sha'];return {}
        raise AssertionError(path)
    def run_notify(self,send=None,check=None,config=None,verification=None,changes=None,sleep=None):
        with patch.object(mod,'github',side_effect=self.gh):
            return mod.notify('owner/repo',self.commit,config or self.config,verification or self.verification,
                 self.changes if changes is None else changes,self.root,check or Mock(),send or Mock(return_value=(200,{})),sleep or Mock())
    def test_off_has_no_network_or_ledger(self):
        send=Mock();check=Mock();r=self.run_notify(send,check,config={'enabled':False})
        self.assertEqual(r['status'],'off');send.assert_not_called();check.assert_not_called();self.assertEqual(self.calls,[])
    def test_no_content_edit_has_no_notification(self):
        send=Mock();self.assertEqual(self.run_notify(send,changes=['tools/a.py'])['status'],'not_required');send.assert_not_called()
    def test_statuses_and_reruns_never_duplicate(self):
        for code,status in [(200,'submitted'),(202,'validation_pending'),(400,'rejected'),(403,'rejected'),(422,'rejected'),(429,'rate_limited'),(500,'unknown')]:
            with self.subTest(code=code):
                self.refs={};send=Mock(return_value=(code,{}))
                self.assertEqual(self.run_notify(send)['status'],status)
                self.assertTrue(self.run_notify(send)['reused']);self.assertEqual(send.call_count,1)
    def test_timeout_is_durable_unknown_and_not_retried(self):
        send=Mock(side_effect=TimeoutError('credential-bearing exception must not leak'))
        r=self.run_notify(send);self.assertEqual(r['status'],'unknown');self.assertNotIn('credential',json.dumps(r))
        self.run_notify(send);self.assertEqual(send.call_count,1)
    def test_only_bounded_429_retry(self):
        send=Mock(side_effect=[(429,{'Retry-After':'2'}),(200,{})]);sleep=Mock()
        self.assertEqual(self.run_notify(send,sleep=sleep)['status'],'submitted');sleep.assert_called_once_with(2)
        self.refs={};send=Mock(return_value=(429,{'Retry-After':'60'}));sleep=Mock()
        self.run_notify(send,sleep=sleep);sleep.assert_not_called();self.assertEqual(send.call_count,1)
    def test_intent_persisted_before_request(self):
        def send(payload):
            self.assertEqual(len(self.refs),1)
            self.assertEqual(json.loads(self.tags[next(iter(self.refs.values()))])['status'],'unknown')
            self.assertEqual(payload['urlList'],[SITE+'/posts/example/']);return 200,{}
        self.run_notify(send)
    def test_preconditions_fail_without_submission(self):
        cases=[{'status':'unverified','source_commit':self.commit,'pages_commit':'c'*40},
               {**self.verification,'source_commit':'d'*40},{**self.verification,'slugs':[]}]
        for proof in cases:
            send=Mock()
            with self.assertRaises(ValueError):self.run_notify(send,verification=proof)
            send.assert_not_called()
    def test_key_missing_or_mismatch_prevents_submission(self):
        send=Mock()
        with self.assertRaises(ValueError):self.run_notify(send,config={**self.config,'key':'invalid'})
        with self.assertRaises(ValueError):self.run_notify(send,check=Mock(side_effect=ValueError('public key mismatch')))
        send.assert_not_called();self.assertFalse(self.refs)
    def test_external_canonical_and_noindex_prevent_submission(self):
        p=self.root/'public/posts/example/index.html'
        for html in ['<link rel="canonical" href="https://evil.test/">',f'<link rel="canonical" href="{SITE}/posts/example/"><meta name="robots" content="noindex">']:
            p.write_text(html)
            with self.assertRaises(ValueError):self.run_notify()
    def test_cli_failure_preserves_publication_success_and_redacts(self):
        with patch.object(mod.Path,'read_text',side_effect=RuntimeError('private-url')),patch.object(mod.Path,'write_text') as write,patch('builtins.print'):
            self.assertIsNone(mod.main());result=json.loads(write.call_args.args[0]);self.assertEqual(result['status'],'needs_reconciliation');self.assertNotIn('private-url',json.dumps(result))
    def test_failure_creating_durable_intent_does_not_send(self):
        send=Mock()
        with patch.object(mod,'github',side_effect=RuntimeError('unavailable')),self.assertRaises(RuntimeError):
            mod.notify('x/y',self.commit,self.config,self.verification,self.changes,self.root,Mock(),send)
        send.assert_not_called()
    def test_mixed_unverified_batch_is_not_partially_sent(self):
        with self.assertRaises(ValueError):self.run_notify(changes=['content/posts/example.md','content/posts/other.md'])

if __name__=='__main__':unittest.main()
