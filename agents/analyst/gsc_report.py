#!/usr/bin/env python3
import sys
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

KEY_FILE = '/home/ubuntu/.secrets/gsc-service-account.json'
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
SITE_URL = 'https://baeseokjae.github.io/'

def get_service():
    creds = service_account.Credentials.from_service_account_file(KEY_FILE, scopes=SCOPES)
    return build('searchconsole', 'v1', credentials=creds)

def get_data(service, days=7, dimensions=['query'], row_limit=50):
    end = datetime.today() - timedelta(days=3)
    start = end - timedelta(days=days)
    resp = service.searchanalytics().query(
        siteUrl=SITE_URL,
        body={
            'startDate': start.strftime('%Y-%m-%d'),
            'endDate': end.strftime('%Y-%m-%d'),
            'dimensions': dimensions,
            'rowLimit': row_limit,
            'orderBy': [{'fieldName': 'clicks', 'sortOrder': 'DESCENDING'}]
        }
    ).execute()
    return resp.get('rows', []), start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')

def daily_report(svc):
    rows, start, end = get_data(svc, days=7)
    print(f'=== DAILY GSC REPORT ({start} ~ {end}) ===')
    if not rows:
        print('No data yet. Site indexing in progress.')
        return
    total_c = sum(r['clicks'] for r in rows)
    total_i = sum(r['impressions'] for r in rows)
    avg_ctr = f"{total_c/total_i*100:.2f}%" if total_i else "N/A"
    print(f'Clicks: {total_c} | Impressions: {total_i} | CTR: {avg_ctr}')
    print('\nTop Queries:')
    for r in rows[:10]:
        print(f'  [{r["clicks"]}c/{r["impressions"]}i pos:{r["position"]:.1f}] {r["keys"][0]}')

def striking(svc):
    rows, _, _ = get_data(svc, days=28, row_limit=200)
    hits = [r for r in rows if 10 < r['position'] <= 20 and r['impressions'] >= 5]
    hits.sort(key=lambda x: x['impressions'], reverse=True)
    print('=== STRIKING DISTANCE (pos 11-20, near page 1) ===')
    if not hits:
        print('None found yet.')
        return
    for r in hits[:15]:
        print(f'  pos:{r["position"]:.1f} | {r["impressions"]}imp | {r["clicks"]}c -> "{r["keys"][0]}"')

def pages(svc):
    rows, start, end = get_data(svc, days=7, dimensions=['page'], row_limit=20)
    print(f'=== PAGE PERFORMANCE ({start} ~ {end}) ===')
    if not rows:
        print('No data yet.')
        return
    for r in rows[:10]:
        url = r['keys'][0].replace(SITE_URL, '/')
        print(f'  [{r["clicks"]}c/{r["impressions"]}i] {url}')

def weekly_report(svc):
    daily_report(svc)
    print()
    striking(svc)
    print()
    pages(svc)

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'daily'
    svc = get_service()
    {'daily': daily_report, 'weekly': weekly_report, 'striking': striking, 'pages': pages}.get(mode, weekly_report)(svc)
