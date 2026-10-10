
import os
import psycopg
from fastapi import FastAPI, HTTPException

app = FastAPI(title="VulnCentral API")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/vulncentral"
)


def connect_db():
    return psycopg.connect(DATABASE_URL)


@app.get("/")
def home():
    return {
        "project": "VulnCentral",
        "message": "Vulnerability Registry API is running"
    }


@app.get("/health")
def health():
    try:
        with connect_db() as conn:
            conn.execute("SELECT 1")
        return {"status": "ok", "database": "connected"}
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )


@app.get("/vulnerabilities")
def get_vulnerabilities(
    q: str = "",
    severity: str = ""
):
    sql = """
        SELECT cve_id, title, description, severity,
               cvss_score, affected_product, remediation
        FROM vulnerabilities
        WHERE (%s = '' OR
               cve_id ILIKE %s OR
               title ILIKE %s OR
               description ILIKE %s)
          AND (%s = '' OR severity = %s)
        ORDER BY cvss_score DESC NULLS LAST
        LIMIT 100
    """

    keyword = f"%{q}%"

    try:
        with connect_db() as conn:
            rows = conn.execute(
                sql,
                (
                    q, keyword, keyword, keyword,
                    severity.upper(), severity.upper()
                )
            ).fetchall()

        return {
            "count": len(rows),
            "vulnerabilities": [
                {
                    "cve_id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "severity": row[3],
                    "cvss_score": float(row[4])
                        if row[4] is not None else None,
                    "affected_product": row[5],
                    "remediation": row[6]
                }
                for row in rows
            ]
        }
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve vulnerabilities"
        )


@app.get("/dashboard")
def dashboard():
    try:
        with connect_db() as conn:
            total = conn.execute(
                "SELECT COUNT(*) FROM vulnerabilities"
            ).fetchone()[0]

            rows = conn.execute("""
                SELECT severity, COUNT(*)
                FROM vulnerabilities
                GROUP BY severity
            """).fetchall()

        return {
            "total_vulnerabilities": total,
            "severity_summary": {
                severity: count for severity, count in rows
            }
        }
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to load dashboard statistics"
        )


@app.get("/query")
def security_query(q: str):
    if len(q.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Enter at least two characters"
        )

    result = get_vulnerabilities(q=q)

    return {
        "question": q,
        "matches_found": result["count"],
        "results": result["vulnerabilities"],
        "note": (
            "Keyword-based search. Verify findings using "
            "official NVD, CISA, or vendor advisories."
        )
    }
