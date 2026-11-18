import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from backend.app.database.db import get_db
from backend.app.core.logging import logger


class ConversationRepository:
    @staticmethod
    def get_or_create_conversation(session_id: str, title: Optional[str] = None) -> Dict[str, Any]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM conversations WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            
            conv_title = title or "New Real Estate Chat"
            now = datetime.utcnow().isoformat()
            cursor.execute(
                "INSERT INTO conversations (session_id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (session_id, conv_title, now, now)
            )
            return {"session_id": session_id, "title": conv_title, "created_at": now, "updated_at": now}

    @staticmethod
    def list_conversations(limit: int = 50) -> List[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM conversations ORDER BY updated_at DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def update_conversation_title(session_id: str, title: str):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE conversations SET title = ?, updated_at = ? WHERE session_id = ?",
                (title, datetime.utcnow().isoformat(), session_id)
            )

    @staticmethod
    def add_message(session_id: str, role: str, content: str, sources: Optional[List[Dict[str, Any]]] = None):
        ConversationRepository.get_or_create_conversation(session_id)
        with get_db() as conn:
            cursor = conn.cursor()
            sources_json = json.dumps(sources or [])
            now = datetime.utcnow().isoformat()
            cursor.execute(
                "INSERT INTO messages (session_id, role, content, sources_json, created_at) VALUES (?, ?, ?, ?, ?)",
                (session_id, role, content, sources_json, now)
            )
            cursor.execute(
                "UPDATE conversations SET updated_at = ? WHERE session_id = ?",
                (now, session_id)
            )

    @staticmethod
    def get_recent_messages(session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content, sources_json, created_at FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, limit)
            )
            rows = cursor.fetchall()
            messages = []
            for r in reversed(rows):
                messages.append({
                    "role": r["role"],
                    "content": r["content"],
                    "sources": json.loads(r["sources_json"] or "[]"),
                    "created_at": r["created_at"]
                })
            return messages


class ProjectRepository:
    @staticmethod
    def upsert_project(project_data: Dict[str, Any]):
        with get_db() as conn:
            cursor = conn.cursor()
            pid = project_data.get("id")
            source = project_data.get("source", "")
            name = project_data.get("project_name", "")
            loc = project_data.get("location", {})
            country = loc.get("country", "")
            city = loc.get("city", "")
            prop_type = project_data.get("property_type", "")
            price = project_data.get("price", {})
            price_amount = price.get("amount") if isinstance(price, dict) else None
            currency = price.get("currency") if isinstance(price, dict) else None
            source_url = project_data.get("source_url", "")
            data_json = json.dumps(project_data, ensure_ascii=False)
            now = datetime.utcnow().isoformat()

            cursor.execute("""
            INSERT INTO scraped_projects (
                id, source, project_name, country, city, property_type,
                price_amount, currency, source_url, data_json, scraped_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                source=excluded.source,
                project_name=excluded.project_name,
                country=excluded.country,
                city=excluded.city,
                property_type=excluded.property_type,
                price_amount=excluded.price_amount,
                currency=excluded.currency,
                source_url=excluded.source_url,
                data_json=excluded.data_json,
                updated_at=excluded.updated_at
            """, (
                pid, source, name, country, city, prop_type,
                price_amount, currency, source_url, data_json, now, now
            ))

    @staticmethod
    def get_project_by_id(project_id: str) -> Optional[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data_json FROM scraped_projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            if row:
                return json.loads(row["data_json"])
            return None

    @staticmethod
    def list_projects(
        source: Optional[str] = None,
        country: Optional[str] = None,
        city: Optional[str] = None,
        property_type: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            conditions = []
            params = []

            if source and source.lower() != "all":
                conditions.append("LOWER(source) = LOWER(?)")
                params.append(source)
            if country:
                conditions.append("LOWER(country) = LOWER(?)")
                params.append(country)
            if city:
                conditions.append("LOWER(city) = LOWER(?)")
                params.append(city)
            if property_type:
                conditions.append("LOWER(property_type) LIKE LOWER(?)")
                params.append(f"%{property_type}%")
            if search_query:
                conditions.append("(LOWER(project_name) LIKE LOWER(?) OR LOWER(city) LIKE LOWER(?) OR LOWER(country) LIKE LOWER(?))")
                q = f"%{search_query}%"
                params.extend([q, q, q])

            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            sql = f"SELECT data_json FROM scraped_projects{where_clause} ORDER BY updated_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(sql, tuple(params))
            return [json.loads(row["data_json"]) for row in cursor.fetchall()]

    @staticmethod
    def count_projects(source: Optional[str] = None) -> int:
        with get_db() as conn:
            cursor = conn.cursor()
            if source and source.lower() != "all":
                cursor.execute("SELECT COUNT(*) FROM scraped_projects WHERE LOWER(source) = LOWER(?)", (source,))
            else:
                cursor.execute("SELECT COUNT(*) FROM scraped_projects")
            return cursor.fetchone()[0]


class IngestionRepository:
    @staticmethod
    def record_run_start(run_id: str) -> None:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO ingestion_runs (run_id, status, started_at) VALUES (?, 'running', ?)",
                (run_id, datetime.utcnow().isoformat())
            )

    @staticmethod
    def record_run_complete(
        run_id: str,
        darglobal_count: int,
        wasalt_count: int,
        total_chunks: int,
        status: str = "completed",
        error_message: Optional[str] = None
    ) -> None:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE ingestion_runs
                SET status = ?, finished_at = ?, darglobal_count = ?, wasalt_count = ?, total_chunks = ?, error_message = ?
                WHERE run_id = ?
                """,
                (status, datetime.utcnow().isoformat(), darglobal_count, wasalt_count, total_chunks, error_message, run_id)
            )

    @staticmethod
    def get_latest_run() -> Optional[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ingestion_runs ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            return dict(row) if row else None
