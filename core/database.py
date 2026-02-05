import sqlite3
import json
from pathlib import Path
from typing import Optional
from core.models import PostResult, ComplianceConfig, AnalysisResult
from config.settings import DATABASE_PATH


def _get_connection() -> sqlite3.Connection:
    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                post_id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                platform TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pendiente',
                extracted_text TEXT DEFAULT '',
                screenshot_path TEXT DEFAULT '',
                thumbnail_path TEXT DEFAULT '',
                analysis_json TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                error_message TEXT DEFAULT '',
                batch_id TEXT DEFAULT ''
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value_json TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def save_post(post: PostResult):
    conn = _get_connection()
    try:
        analysis_json = ""
        if post.analysis:
            analysis_json = post.analysis.model_dump_json()

        conn.execute("""
            INSERT OR REPLACE INTO posts
            (post_id, url, platform, status, extracted_text, screenshot_path,
             thumbnail_path, analysis_json, created_at, error_message, batch_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            post.post_id, post.url, post.platform.value, post.status.value,
            post.extracted_text, post.screenshot_path, post.thumbnail_path,
            analysis_json, post.created_at.isoformat(), post.error_message,
            post.batch_id,
        ))
        conn.commit()
    finally:
        conn.close()


def get_all_posts(batch_id: Optional[str] = None) -> list[PostResult]:
    conn = _get_connection()
    try:
        if batch_id:
            rows = conn.execute(
                "SELECT * FROM posts WHERE batch_id = ? ORDER BY created_at DESC", (batch_id,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM posts ORDER BY created_at DESC"
            ).fetchall()
        return [_row_to_post(row) for row in rows]
    finally:
        conn.close()


def get_post(post_id: str) -> Optional[PostResult]:
    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM posts WHERE post_id = ?", (post_id,)
        ).fetchone()
        if row:
            return _row_to_post(row)
        return None
    finally:
        conn.close()


def delete_post(post_id: str):
    conn = _get_connection()
    try:
        conn.execute("DELETE FROM posts WHERE post_id = ?", (post_id,))
        conn.commit()
    finally:
        conn.close()


def delete_all_posts():
    conn = _get_connection()
    try:
        conn.execute("DELETE FROM posts")
        conn.commit()
    finally:
        conn.close()


def save_config(config: ComplianceConfig):
    conn = _get_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO config (key, value_json) VALUES (?, ?)",
            ("compliance_config", config.model_dump_json()),
        )
        conn.commit()
    finally:
        conn.close()


def load_config() -> ComplianceConfig:
    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT value_json FROM config WHERE key = ?", ("compliance_config",)
        ).fetchone()
        if row:
            return ComplianceConfig.model_validate_json(row["value_json"])
        return ComplianceConfig()
    finally:
        conn.close()


def _row_to_post(row: sqlite3.Row) -> PostResult:
    analysis = None
    if row["analysis_json"]:
        try:
            analysis = AnalysisResult.model_validate_json(row["analysis_json"])
        except Exception:
            analysis = None

    return PostResult(
        post_id=row["post_id"],
        url=row["url"],
        platform=row["platform"],
        status=row["status"],
        extracted_text=row["extracted_text"],
        screenshot_path=row["screenshot_path"],
        thumbnail_path=row["thumbnail_path"],
        analysis=analysis,
        created_at=row["created_at"],
        error_message=row["error_message"],
        batch_id=row["batch_id"],
    )
