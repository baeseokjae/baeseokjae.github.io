#!/usr/bin/env python3
from __future__ import annotations

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

KEY_FILE = "/home/ubuntu/.secrets/gsc-service-account.json"
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
SITE_URL = "https://baeseokjae.github.io/"
SITEMAPS = [
    "https://baeseokjae.github.io/sitemap.xml",
    "https://baeseokjae.github.io/sitemap-pages.xml",
    "https://baeseokjae.github.io/sitemap-posts.xml",
]
SAMPLE_URLS = [
    "https://baeseokjae.github.io/",
    "https://baeseokjae.github.io/posts/",
    "https://baeseokjae.github.io/posts/best-ai-coding-assistants-2026/",
    "https://baeseokjae.github.io/posts/agentic-ai-explained-2026/",
    "https://baeseokjae.github.io/posts/openai-responses-api-tutorial-2026/",
]


def get_service():
    creds = service_account.Credentials.from_service_account_file(
        KEY_FILE,
        scopes=SCOPES,
    )
    return build("searchconsole", "v1", credentials=creds)


def print_sitemap_status(service):
    print("== Sitemaps ==")
    for sitemap in SITEMAPS:
        try:
            response = service.sitemaps().get(
                siteUrl=SITE_URL,
                feedpath=sitemap,
            ).execute()
        except HttpError as error:
            print(f"{sitemap}: ERROR {error.status_code} {error.reason}")
            continue

        print(
            "{path} | pending={pending} | lastSubmitted={submitted} | "
            "lastDownloaded={downloaded} | warnings={warnings} | errors={errors} | "
            "contents={contents}".format(
                path=response.get("path"),
                pending=response.get("isPending"),
                submitted=response.get("lastSubmitted"),
                downloaded=response.get("lastDownloaded"),
                warnings=response.get("warnings"),
                errors=response.get("errors"),
                contents=response.get("contents"),
            ),
        )


def print_inspection_status(service):
    print("\n== URL Inspection Samples ==")
    for url in SAMPLE_URLS:
        try:
            response = service.urlInspection().index().inspect(
                body={
                    "inspectionUrl": url,
                    "siteUrl": SITE_URL,
                },
            ).execute()
        except HttpError as error:
            print(f"{url}: ERROR {error.status_code} {error.reason}")
            continue

        result = response.get("inspectionResult", {}).get("indexStatusResult", {})
        print(
            "{url} | coverage={coverage} | verdict={verdict} | fetch={fetch} | "
            "robots={robots} | indexing={indexing} | lastCrawl={last_crawl}".format(
                url=url,
                coverage=result.get("coverageState"),
                verdict=result.get("verdict"),
                fetch=result.get("pageFetchState"),
                robots=result.get("robotsTxtState"),
                indexing=result.get("indexingState"),
                last_crawl=result.get("lastCrawlTime"),
            ),
        )


def main():
    service = get_service()
    print_sitemap_status(service)
    print_inspection_status(service)


if __name__ == "__main__":
    main()
