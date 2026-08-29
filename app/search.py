from __future__ import annotations

from typing import Any
from urllib.parse import parse_qs, quote_plus, urlparse

import requests
from bs4 import BeautifulSoup

USER_AGENT = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )
}


def build_queries(
    keywords: list[str] | str | None,
    location: str | None = None,
    max_results: int = 10,
) -> list[str]:
    if isinstance(keywords, str):
        keyword_list = [keywords]
    else:
        keyword_list = list(keywords or [])

    keyword_list = [item.strip() for item in keyword_list if item and item.strip()]
    if not keyword_list:
        keyword_list = ["estagio suporte ti", "help desk", "suporte tecnico"]

    queries: list[str] = []
    for keyword in keyword_list[:5]:
        parts = [keyword]
        if location:
            parts.append(location)
        parts.extend(["vagas", "estagio"])
        query = " ".join(part for part in parts if part).strip()
        if query not in queries:
            queries.append(query)

    return queries[: max(1, max_results)]


def normalize_result(result: dict[str, Any], source: str) -> dict[str, Any]:
    title = (result.get("title") or "Sem título").strip()
    url = (result.get("href") or result.get("url") or "").strip()
    if url.startswith("/l/?"):
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if "uddg" in params:
            url = params["uddg"][0]

    summary = (result.get("body") or result.get("snippet") or "").strip()
    return {
        "title": title,
        "url": url,
        "summary": summary,
        "source": source,
    }


def _fetch_duckduckgo(query: str) -> str:
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    response = requests.get(url, headers=USER_AGENT, timeout=15)
    response.raise_for_status()
    return response.text


def _extract_duckduckgo_results(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    results: list[dict[str, str]] = []

    for item in soup.select(".result"):
        anchor = item.select_one(".result__title a")
        if not anchor:
            continue

        snippet = item.select_one(".result__snippet")
        results.append(
            {
                "title": anchor.get_text(" ", strip=True),
                "href": anchor.get("href", ""),
                "body": snippet.get_text(" ", strip=True) if snippet else "",
            }
        )

    return results


def search_jobs(
    keywords: list[str] | str | None,
    location: str | None = None,
    max_results: int = 10,
) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    for query in build_queries(keywords=keywords, location=location, max_results=max_results):
        try:
            html = _fetch_duckduckgo(query)
            results = _extract_duckduckgo_results(html)
        except requests.RequestException:
            continue

        for result in results:
            normalized = normalize_result(result, source="DuckDuckGo")
            url = normalized.get("url")
            if not url or url in seen_urls:
                continue

            seen_urls.add(url)
            jobs.append(normalized)

            if len(jobs) >= max_results:
                return jobs

    return jobs
