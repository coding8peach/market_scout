import os
import requests
from crewai.tools import tool


@tool("Web Search")
def serper_search(query: str) -> str:
    """
    Search the web for current information.

    Args:
        query: The web search query.

    Returns:
        Recent search results including titles,
        snippets, and source URLs.
    """

    api_key = os.getenv("SERPER_API_KEY")

    url = "https://google.serper.dev/search"

    payload = {
        "q": query,
        "num": 10
    }

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()
    data = response.json()

    results = []

    for item in data.get("organic", [])[:5]:
        results.append({
            "title": item.get("title", ""),
            "snippet": item.get("snippet", ""),
            "link": item.get("link", "")
        })

    return str(results)