import re
from typing import List, Dict, Any, Optional
from backend.app.core.logging import logger


class QueryRewriter:
    @staticmethod
    def extract_recent_entities(history: List[Dict[str, Any]]) -> List[str]:
        entities = []
        known_keywords = [
            "W Residences", "Tierra Viva", "DaVinci Tower", "AIDA", "Urban Oasis",
            "Trump Tower", "Astera", "Les Vagues", "DG1", "Marriott Residences",
            "Fendi Casa", "Fairway Villas", "Painite", "Pagani", "Missoni", "Lamborghini",
            "Dubai", "Riyadh", "Jeddah", "Muscat", "Benahavis", "Marbella", "Doha",
            "Al-Mahdiyah", "Villa", "Apartment", "Penthouse"
        ]
        for msg in reversed(history[-4:]):
            content = msg.get("content", "")
            for kw in known_keywords:
                if kw.lower() in content.lower() and kw not in entities:
                    entities.append(kw)
        return entities

    @classmethod
    def rewrite_query(cls, query: str, history: List[Dict[str, Any]]) -> str:
        if not history:
            return query

        query_clean = query.strip()
        pronouns = [r"\bit\b", r"\bthis\b", r"\bthat\b", r"\bthese\b", r"\bthe project\b", r"\bthe property\b", r"\bthere\b", r"\bits\b"]
        has_pronoun = any(re.search(p, query_clean, re.IGNORECASE) for p in pronouns)
        is_short_followup = len(query_clean.split()) <= 6

        if has_pronoun or is_short_followup:
            entities = cls.extract_recent_entities(history)
            if entities:
                main_entity = entities[0]
                # Replace pronouns or append context
                rewritten = query_clean
                for p in pronouns:
                    rewritten = re.sub(p, main_entity, rewritten, count=1, flags=re.IGNORECASE)
                
                if rewritten == query_clean:
                    rewritten = f"{query_clean} regarding {main_entity}"
                
                logger.info("[QueryRewriter] Rewrote query '%s' -> '%s'", query, rewritten)
                return rewritten

        return query
