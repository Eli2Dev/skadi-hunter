from app.search import build_queries, is_recent_job, normalize_result


def test_build_queries():
    queries = build_queries(
        keywords=["python", "analista de dados"],
        location="remoto",
        max_results=5,
    )

    assert queries
    assert any("python" in q.lower() for q in queries)
    assert any("remoto" in q.lower() for q in queries)


def test_normalize_result():
    result = {
        "title": "Python Developer",
        "href": "https://example.com/job/123",
        "body": "Trabalho remoto e híbrido em Python",
    }

    job = normalize_result(result, source="DuckDuckGo")

    assert job["title"] == "Python Developer"
    assert job["url"] == "https://example.com/job/123"
    assert job["source"] == "DuckDuckGo"


def test_default_keywords_for_suporte_ti_salvador():
    queries = build_queries(
        keywords=["estagio suporte ti", "help desk", "suporte tecnico"],
        location="Salvador",
        max_results=5,
    )

    assert queries
    assert any("salvador" in q.lower() for q in queries)
    assert any("suporte" in q.lower() for q in queries)


def test_is_recent_job_accepts_recent_results():
    job = {
        "title": "Estágio em suporte de TI",
        "summary": "Vaga publicada hoje em Salvador",
        "url": "https://example.com/job/recent",
    }

    assert is_recent_job(job) is True


def test_is_recent_job_rejects_stale_results():
    job = {
        "title": "Estágio em suporte de TI",
        "summary": "Vaga antiga, publicada há mais de 30 dias",
        "url": "https://example.com/job/old",
    }

    assert is_recent_job(job) is False
