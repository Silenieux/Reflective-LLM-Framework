import os
import requests
from readability import Document
from bs4 import BeautifulSoup
from core.greg_routes import route_query


def load_local_article(filepath: str, limit_chars: int = 12000) -> str:
    """
    Load a local text/markdown file and return up to `limit_chars` characters.
    """
    if not os.path.exists(filepath):
        return "[ERROR] File does not exist."
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()[:limit_chars].strip()


def fetch_and_clean_article(url: str, limit_chars: int = 12000) -> str:
    """
    Fetch a URL and extract clean readable text using readability + BeautifulSoup.
    """
    try:
        html = requests.get(url, timeout=10).text
        doc = Document(html)
        soup = BeautifulSoup(doc.summary(), "html.parser")
        return soup.get_text()[:limit_chars].strip()
    except Exception as e:
        return f"[ERROR] Failed to retrieve article: {e}"


def build_reflection_prompt(title: str, content: str) -> str:
    """
    Wraps content into a Greg-style reflective prompt.
    """
    return (
        f"You are reviewing a document titled: '{title}'.\n\n"
        f"{content}\n\n"
        f"Greg, reflect deeply. What stands out to you? What new line of thinking does this open?"
    )


def reflect_on_local_file(filepath: str) -> str:
    """
    Load local file → build prompt → route through Greg.
    """
    content = load_local_article(filepath)
    prompt = build_reflection_prompt(os.path.basename(filepath), content)
    return route_query(prompt)


def reflect_on_url_article(url: str) -> str:
    """
    Fetch article from URL → build prompt → route through Greg.
    """
    content = fetch_and_clean_article(url)
    prompt = build_reflection_prompt(url, content)
    return route_query(prompt)
