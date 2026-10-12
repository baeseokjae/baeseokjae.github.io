import copy
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock
from health_watch import conditions, deliver, read_ledger

REPO = 'baeseokjae/baeseokjae.github.io'
AT = datetime(2026, 10, 12, 11, tzinfo=timezone.utc)


class HealthWatchTest(unittest.TestCase):
    def setUp(self):
        self.state = None
        self.send = Mock(return_value={'ok': True, 'result': {'message_id': 42}})
        self.saved = []

    def save(self, value):
        self.state = copy.deepcopy(value)
        self.saved.append(self.state)

    def check(self, alerts, **kwargs):
        return deliver(self.state, alerts, AT, REPO, self.save, self.send, **kwargs)

    def test_healthy_baseline_and_unchanged_state_are_quiet(self):
        self.check([]); self.check([])
        self.send.assert_not_called()

    def test_expiry_future_bad_timestamp_and_site_fail_are_distinct(self):
        h = {'version': 1, 'at': (AT-timedelta(minutes=26)).isoformat(), 'alerts': []}
        self.assertEqual(conditions(h, True, AT), ['heartbeat_stale'])
        self.assertEqual(conditions(None, False, AT), ['heartbeat_missing', 'public_site_unavailable'])
        h['at'] = (AT+timedelta(minutes=6)).isoformat()
        self.assertEqual(conditions(h, True, AT), ['heartbeat_invalid'])
        h['at'] = '2026-10-12T11:00:00'
        self.assertEqual(conditions(h, True, AT), ['heartbeat_invalid'])

    def test_incident_changes_and_recovery_keep_identity_without_repetition(self):
        first = self.check(['heartbeat_stale'])
        self.check(['heartbeat_stale'])
        worse = self.check(['heartbeat_stale', 'public_site_unavailable'])
        recovered = self.check([])
        self.check([])
        self.assertEqual(self.send.call_count, 3)
        self.assertEqual(first['incident_id'], worse['incident_id'])
        self.assertEqual(first['incident_id'], recovered['incident_id'])
        self.assertEqual(self.saved[0]['status'], 'delivery_unknown')

    def test_response_loss_after_send_never_retries(self):
        self.send.side_effect = TimeoutError
        with self.assertRaises(TimeoutError): self.check(['heartbeat_stale'])
        self.assertEqual(self.state['status'], 'delivery_unknown')
        self.check(['heartbeat_stale'])
        self.assertEqual(self.send.call_count, 1)

    def test_lost_intent_write_response_must_not_send(self):
        def save(value):
            self.save(value)
            raise TimeoutError
        with self.assertRaises(TimeoutError):
            deliver(None, ['heartbeat_stale'], AT, REPO, save, self.send)
        self.send.assert_not_called()
        self.check(['heartbeat_stale']); self.send.assert_not_called()

    def test_lost_final_receipt_does_not_duplicate_message(self):
        def save(value):
            if value['status'] == 'sent': raise TimeoutError
            self.save(value)
        with self.assertRaises(TimeoutError):
            deliver(None, ['heartbeat_stale'], AT, REPO, save, self.send)
        self.check(['heartbeat_stale']); self.assertEqual(self.send.call_count, 1)

    def test_arbitrary_strings_cannot_enter_public_message(self):
        with self.assertRaises(ValueError): self.check(['secret/path'])
        self.send.assert_not_called()
        self.assertEqual(conditions({'version': 1, 'at': AT.isoformat(), 'alerts': ['secret/path']}, True, AT), ['heartbeat_invalid'])

    def test_drill_cannot_reuse_live_delivery_ledger(self):
        self.check(['heartbeat_stale'])
        with self.assertRaises(ValueError): self.check([], drill=True)

    def test_wrong_tag_type_identity_and_repository_fail_closed(self):
        ref = {'ref': 'refs/tags/rockb-ops-heartbeat', 'object': {'type': 'commit', 'sha': 'a'*40}}
        api = Mock(return_value=ref)
        with self.assertRaises(ValueError): read_ledger(REPO, 'rockb-ops-heartbeat', api)
        ref['object']['type'] = 'tag'
        tag = {'sha': 'a'*40, 'tag': 'wrong', 'object': {'type': 'commit', 'sha': 'b'*40}, 'message': '{}'}
        api.side_effect = [ref, tag]
        with self.assertRaises(ValueError): read_ledger(REPO, 'rockb-ops-heartbeat', api)


if __name__ == '__main__': unittest.main()
