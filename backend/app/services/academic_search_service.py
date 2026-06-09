from datetime import datetime
from typing import Any

import httpx


KEYWORD_MAP = [
    ("轴承故障", "bearing fault diagnosis"),
    ("故障诊断", "fault diagnosis"),
    ("小样本", "few-shot fault diagnosis"),
    ("迁移学习", "transfer learning fault diagnosis"),
    ("剩余寿命预测", "remaining useful life prediction"),
    ("异常检测", "anomaly detection"),
    ("设备健康管理", "prognostics and health management"),
    ("PHM", "prognostics and health management"),
    ("深度学习", "deep learning"),
]


class AcademicSearchError(RuntimeError):
    pass


def build_search_query(message: str) -> str:
    matched_terms: list[str] = []
    for keyword, term in KEYWORD_MAP:
        if keyword in message and term not in matched_terms:
            matched_terms.append(term)

    if not matched_terms:
        return message.strip()

    # 去重保序，避免 fault diagnosis 重复太多影响检索。
    words: list[str] = []
    for term in matched_terms:
        for word in term.split():
            if word not in words:
                words.append(word)
    return " ".join(words)


def reconstruct_abstract(inverted_index: dict[str, list[int]] | None) -> str:
    if not inverted_index:
        return ""

    words: list[tuple[int, str]] = []
    for word, positions in inverted_index.items():
        for position in positions:
            words.append((position, word))
    words.sort(key=lambda item: item[0])
    return " ".join(word for _, word in words)


async def search_openalex_papers(
    query: str,
    recent_years: int = 3,
    limit: int = 10,
) -> list[dict[str, Any]]:
    current_year = datetime.now().year
    from_year = max(current_year - recent_years, 1900)
    from_publication_date = f"{from_year}-01-01"

    params = {
        "search": query,
        "filter": f"from_publication_date:{from_publication_date}",
        "sort": "publication_date:desc",
        "per-page": limit,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get("https://api.openalex.org/works", params=params)
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPStatusError as exc:
        raise AcademicSearchError(
            f"OpenAlex 检索失败：HTTP {exc.response.status_code} {exc.response.text[:500]}"
        ) from exc
    except (httpx.RequestError, ValueError) as exc:
        raise AcademicSearchError(f"OpenAlex 检索失败：{exc}") from exc

    results = payload.get("results", [])
    if not isinstance(results, list):
        return []

    return [_normalize_openalex_item(item) for item in results]


def _normalize_openalex_item(item: dict[str, Any]) -> dict[str, Any]:
    primary_location = item.get("primary_location") or {}
    source = primary_location.get("source") or {}
    doi = item.get("doi") or ""
    url = primary_location.get("landing_page_url") or doi or item.get("id") or ""

    return {
        "title": item.get("title") or "未命名论文",
        "authors": _extract_authors(item),
        "year": item.get("publication_year"),
        "publication_date": item.get("publication_date") or "",
        "venue": source.get("display_name") or "",
        "doi": doi,
        "url": url,
        "abstract": reconstruct_abstract(item.get("abstract_inverted_index")),
        "cited_by_count": item.get("cited_by_count") or 0,
        "source": "openalex",
        "raw_data": item,
    }


def _extract_authors(item: dict[str, Any]) -> list[str]:
    authors: list[str] = []
    for authorship in item.get("authorships") or []:
        author = authorship.get("author") or {}
        name = author.get("display_name")
        if name:
            authors.append(name)
    return authors
