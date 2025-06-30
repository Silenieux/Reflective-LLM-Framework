from duckduckgo_search import DDGS

def web_search(query, max_results=3):
    """
    Perform a DuckDuckGo search and return top result summaries.
    """
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            if results:
                return "\n".join([f"- {r['title']} — {r['href']}" for r in results])
            else:
                return "No relevant results found."
    except Exception as e:
        return f"Search failed: {str(e)}"

def detect_web_query(prompt):
    """
    Detects if the prompt likely intends to perform a web search.
    """
    keywords = [
        "search online", "look this up", "real info", "news on", "what is", "check online",
        "google", "duckduckgo", "find out about", "lookup", "what happened with", "latest on"
    ]
    lowered = prompt.lower()
    return any(k in lowered for k in keywords)
