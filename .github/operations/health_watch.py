"""External liveness observation. A durable intent prevents uncertain resends.

Only timestamps and fixed alert codes are public. No credentials, task contents,
host paths, IP addresses or raw exception messages are included in the ledger.
GitHub schedule delivery is best effort; this is not an uptime SLA.
"""
import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from publication_watch import verify as verify_publication, ALERTS as PUBLICATION_ALERTS

ALERTS = {
    'controller_stale', 'storage_reserve_below_warning', 'storage_emergency',
    'filesystem_inodes_low', 'backup-retention_unhealthy', 'backup-retention_unavailable',
    'scratch-retention_unhealthy', 'scratch-retention_unavailable', 'scratch_recovery_pending',
    'maintenance_overdue', 'publication_blocked', 'publication_notification_unverified',
    'publication_state_unverified', 'publication_delayed', 'publication_verification_expired',
    'resource_reservations_unverified', 'inactive_reservation_retained',
    'scheduled_publication_missed', 'content_production_resource_stalled',
    'cost_parser_protection_inactive', 'cost_parser_protection_unverified',
    'backup_restore_capacity_warning', 'backup_restore_capacity_action',
    'unclassified_internal_alert', 'internal_alert_delivery_failed',
}
EXTERNAL = {'heartbeat_missing', 'heartbeat_stale', 'heartbeat_invalid', 'public_site_unavailable'}
EXTERNAL |= PUBLICATION_ALERTS
SHA = re.compile(r'[0-9a-f]{40}')


def date(value):
    at = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if at.tzinfo is None:
        raise ValueError('Timestamp must have a timezone')
    return at


def github(repo, path, method='GET', body=None):
    request = urllib.request.Request('https://api.github.com/repos/' + repo + '/' + path,
        data=json.dumps(body).encode() if body is not None else None, method=method,
        headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'],
                 'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def read_ledger(repo, name, api=github):
    try:
        ref = api(repo, 'git/ref/tags/' + name)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise
    obj = ref.get('object', {})
    if ref.get('ref') != 'refs/tags/' + name or obj.get('type') != 'tag' or not SHA.fullmatch(obj.get('sha', '')):
        raise ValueError('Invalid ledger reference')
    tag = api(repo, 'git/tags/' + obj['sha'])
    target = tag.get('object', {})
    if (tag.get('sha') != obj['sha'] or tag.get('tag') != name or target.get('type') != 'commit'
            or not SHA.fullmatch(target.get('sha', ''))):
        raise ValueError('Invalid ledger identity')
    value = json.loads(tag['message'])
    if value.get('version') != 1 or value.get('repository') != repo:
        raise ValueError('Invalid ledger schema or repository')
    return value


def write_ledger(repo, name, commit, value, exists, api=github):
    if not SHA.fullmatch(commit):
        raise ValueError('Invalid source commit')
    tag = api(repo, 'git/tags', 'POST', {'tag': name, 'message': json.dumps(value, sort_keys=True),
                                     'object': commit, 'type': 'commit'})
    if not SHA.fullmatch(tag.get('sha', '')):
        raise ValueError('Invalid tag creation response')
    if exists:
        api(repo, 'git/refs/tags/' + name, 'PATCH', {'sha': tag['sha'], 'force': True})
    else:
        api(repo, 'git/refs', 'POST', {'ref': 'refs/tags/' + name, 'sha': tag['sha']})


def conditions(heartbeat, site_ok, at):
    alerts = []
    if heartbeat is None:
        alerts.append('heartbeat_missing')
    else:
        try:
            age = (at - date(heartbeat['at'])).total_seconds()
            codes = heartbeat['alerts']
            if heartbeat.get('version') != 1 or not isinstance(codes, list) or any(c not in ALERTS for c in codes):
                raise ValueError('Invalid heartbeat')
            if age < -300:
                alerts.append('heartbeat_invalid')
            else:
                alerts.extend(codes)
                if age > 25 * 60:
                    alerts.append('heartbeat_stale')
        except (KeyError, TypeError, ValueError):
            alerts.append('heartbeat_invalid')
    if not site_ok:
        alerts.append('public_site_unavailable')
    return sorted(set(alerts))


def deliver(previous, alerts, at, repo, save, send, *, drill=False):
    """Serialized workflow is the sole delivery-ledger writer.

    Save intent before sending. A response loss, including after Telegram accepts
    the message, must never produce an automatic resend of the same transition.
    """
    alerts = sorted(set(alerts))
    if any(x not in ALERTS | EXTERNAL for x in alerts):
        raise ValueError('Unrecognized public alert code')
    if previous is not None:
        if (previous.get('version') != 1 or previous.get('repository') != repo
                or previous.get('drill') != drill
                or previous.get('status') not in ('quiet', 'sent', 'delivery_unknown')
                or not isinstance(previous.get('alerts'), list)):
            raise ValueError('Invalid notification ledger')
        if previous['alerts'] == alerts:
            return {'status': previous['status'], 'changed': False,
                    'incident_id': previous.get('incident_id'), 'alerts': alerts}
    event_at = at.isoformat()
    incident = (previous or {}).get('incident_id') if (previous or {}).get('alerts') else None
    incident = incident or hashlib.sha256((repo + event_at + str(drill)).encode()).hexdigest()[:16]
    value = {'version': 1, 'repository': repo, 'drill': drill, 'incident_id': incident,
             'at': event_at, 'alerts': alerts, 'status': 'delivery_unknown'}
    if previous is None and not alerts:
        value['status'] = 'quiet'
        save(value)
        return {**value, 'changed': False}
    save(value)
    label = '[시험 / 실제 장애 아님] ' if drill else ''
    heading = '블로그 운영 상태 변경' if alerts else '블로그 운영 감시: 회복 확인'
    text = label + heading + '\n사건: ' + incident + '\n'
    text += '\n'.join('- ' + a for a in alerts) if alerts else '현재 확인된 장애 신호가 해소되었습니다.'
    text += '\n확인 시각(UTC): ' + event_at + '\nhttps://baeseokjae.github.io/'
    response = send(text)
    if not response.get('ok') or not isinstance(response.get('result', {}).get('message_id'), int):
        raise ValueError('Telegram delivery not confirmed')
    value = {**value, 'status': 'sent', 'telegram_message_id': response['result']['message_id']}
    save(value)
    return {**value, 'changed': True}


def site_alive():
    for _ in range(2):
        try:
            req = urllib.request.Request('https://baeseokjae.github.io/', headers={'User-Agent': 'RockB-Operations-Monitor/1'})
            with urllib.request.urlopen(req, timeout=15) as response:
                body = response.read(512000).lower()
                if response.status == 200 and b'<html' in body and b'rockb' in body:
                    return True
        except (OSError, ValueError):
            pass
    return False


def telegram(text):
    body = urllib.parse.urlencode({'chat_id': os.environ['TELEGRAM_CHAT_ID'], 'text': text}).encode()
    req = urllib.request.Request('https://api.telegram.org/bot' + os.environ['TELEGRAM_BOT_TOKEN'] + '/sendMessage', data=body)
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)


def main():
    at = datetime.now(timezone.utc)
    repo = os.environ['GITHUB_REPOSITORY']
    drill = os.environ.get('WATCH_DRILL', 'none') or 'none'
    if drill not in ('none', 'stale', 'recovery'):
        raise ValueError('Unsupported drill')
    if drill != 'none' and os.environ.get('GITHUB_EVENT_NAME') != 'workflow_dispatch':
        raise ValueError('Drills require manual dispatch')
    heartbeat = read_ledger(repo, 'rockb-ops-heartbeat')
    site_ok = site_alive()
    if drill != 'none':
        heartbeat = {'version': 1, 'at': (at - timedelta(minutes=30) if drill == 'stale' else at).isoformat(), 'alerts': []}
        site_ok = True  # A separate synthetic incident; never alters the live heartbeat.
    alerts = conditions(heartbeat, site_ok, at)
    publication=verify_publication(heartbeat.get('publication') if heartbeat and drill=='none' else None,repo,at,github)
    alerts=sorted(set(alerts+publication['alerts']))
    name = 'rockb-ops-delivery-test' if drill != 'none' else 'rockb-ops-delivery'
    previous = read_ledger(repo, name)
    exists = previous is not None
    def save(value):
        nonlocal exists
        write_ledger(repo, name, os.environ['GITHUB_SHA'], value, exists)
        exists = True
    result = deliver(previous, alerts, at, repo, save, telegram, drill=drill != 'none')
    Path('operations-receipt.json').write_text(json.dumps({'observed_at': at.isoformat(), 'publication':publication, **result}, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'changed': result['changed'], 'alerts': alerts}))
    if result['status'] == 'delivery_unknown':
        raise SystemExit('Delivery remains uncertain; no automatic resend')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        # HTTP error URLs can contain Telegram credentials; never print them.
        Path('operations-receipt.json').write_text(json.dumps({'status': 'unverified', 'error_type': type(exc).__name__}) + '\n')
        raise SystemExit('Operations monitor needs investigation: ' + type(exc).__name__)
