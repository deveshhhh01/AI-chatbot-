import re
from bs4 import BeautifulSoup


class DataCleaner:
    @staticmethod
    def clean_html(raw_html: str) -> str:
        if not raw_html:
            return ""
        soup = BeautifulSoup(raw_html, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "iframe"]):
            tag.decompose()
        text = soup.get_text(separator=" ")
        return DataCleaner.clean_whitespace(text)

    @staticmethod
    def clean_whitespace(text: str) -> str:
        if not text:
            return ""
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def normalize_text(text: str) -> str:
        if not text:
            return ""
        text = DataCleaner.clean_whitespace(text)
        # Remove non-printable characters
        text = "".join(ch for ch in text if ch.isprintable() or ch in "\n\t")
        return text
