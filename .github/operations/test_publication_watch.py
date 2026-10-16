import copy,hashlib,json,unittest
from datetime import datetime,timedelta,timezone
from unittest.mock import Mock
from publication_watch import Article,verify
AT=datetime(2026,10,16,1,tzinfo=timezone.utc);REPO='baeseokjae/baeseokjae.github.io';COMMIT='a'*40;PAGES='b'*40;TAG='c'*40
URL='https://baeseokjae.github.io/posts/example/'
HTML='<html><link rel="canonical" href="'+URL+'"><div class="post-content"><p>One <strong>two</strong></p><p>three &amp; four</p><script>ignored</script></div></html>'
class PublicationWatchTest(unittest.TestCase):
 def setUp(self):
  self.signal={'version':1,'day':'2026-10-16','expected':True,'status':'verified','deadline_at':'2026-10-16T09:20:00+09:00','proof':{'commit':COMMIT,'pages_commit':PAGES,'url':URL,'body_sha256':hashlib.sha256('One two three & four'.encode()).hexdigest()}}
  self.values=[{'workflow_runs':[{'name':'Deploy Hugo','head_sha':COMMIT,'conclusion':'success'}]}, {'sha':PAGES,'commit':{'message':'deploy '+COMMIT}}, {'ref':'refs/tags/rockb-notify-'+COMMIT,'object':{'type':'tag','sha':TAG}}, {'sha':TAG,'tag':'rockb-notify-'+COMMIT,'object':{'type':'commit','sha':COMMIT},'message':json.dumps({'version':1,'source_commit':COMMIT,'status':'sent'})}]
 def check(self,signal=None,html=HTML):return verify(signal or self.signal,REPO,AT,Mock(side_effect=self.values),Mock(return_value=html))
 def test_actual_independent_evidence_passes(self):self.assertEqual(self.check()['status'],'verified')
 def test_http200_wrong_body_or_canonical_cannot_pass(self):
  for html in (HTML.replace('One','Old'),HTML.replace(URL,URL+'wrong')):self.assertEqual(self.check(html=html)['status'],'mismatch')
 def test_false_local_success_without_ci_cannot_pass(self):
  self.values[0]['workflow_runs']=[];self.assertEqual(self.check()['status'],'mismatch')
 def test_wrong_pages_source_or_notification_commit_cannot_pass(self):
  self.values[1]['commit']['message']='other';self.assertEqual(self.check()['status'],'mismatch')
  self.values[1]['commit']['message']=COMMIT;self.values[3]['object']['sha']='d'*40;self.assertEqual(self.check()['status'],'mismatch')
 def test_unknown_notification_is_not_sent(self):
  self.values[3]['message']=self.values[3]['message'].replace('sent','delivery_unknown');self.assertEqual(self.check()['status'],'mismatch')
 def test_api_unavailable_cannot_pass(self):self.assertEqual(verify(self.signal,REPO,AT,Mock(side_effect=TimeoutError))['status'],'unavailable')
 def test_deadline_missing_unknown_and_legacy(self):
  signal={**self.signal,'status':'pending'};signal.pop('proof');self.assertEqual(self.check(signal)['status'],'missed')
  self.assertEqual(verify(signal,REPO,AT-timedelta(hours=2),Mock())['status'],'pending')
  self.assertEqual(self.check({**signal,'status':'unknown'})['status'],'unknown')
  self.assertEqual(verify(None,REPO,AT,Mock())['status'],'legacy_signal')
 def test_stale_or_arbitrary_url_signals_rejected(self):
  self.assertEqual(self.check({**self.signal,'day':'2026-10-15'})['status'],'mismatch')
  self.signal['proof']['url']='http://169.254.169.254/';self.assertEqual(self.check()['status'],'mismatch')
