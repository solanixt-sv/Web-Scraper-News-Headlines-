"""
News Headlines Scraper
======================
Real-world Python project for portfolio
Scrapes headlines from BBC, Dawn, and Reuters
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import json
import os
import sys
import numpy as np
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from textblob import TextBlob
import nltk
from collections import Counter
import re

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('brown', quiet=True)
except:
    pass

def build_console() -> Console:
    """Create a Windows-safe Rich console."""
    if os.name == "nt":
        for stream_name in ("stdout", "stderr"):
            stream = getattr(sys, stream_name, None)
            if hasattr(stream, "reconfigure"):
                try:
                    stream.reconfigure(encoding="utf-8", errors="replace")
                except Exception:
                    pass
    return Console()


console = build_console()

# ─────────────────────────────────────────
#  SOURCES CONFIG
# ─────────────────────────────────────────
SOURCES = {
    "BBC News": {
        "url": "https://feeds.bbci.co.uk/news/rss.xml",
        "type": "rss",
    },
    "Dawn (Pakistan)": {
        "url": "https://www.dawn.com/feeds/home",
        "type": "rss",
    },
    "The Guardian": {
        "url": "https://www.theguardian.com/world/rss",
        "type": "rss",
    },
    "Al Jazeera": {
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
        "type": "rss",
    },
    "CNN": {
        "url": "http://rss.cnn.com/rss/edition.rss",
        "type": "rss",
    },
    "New York Times": {
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "type": "rss",
    },
    "NDTV (India)": {
        "url": "https://feeds.feedburner.com/ndtvnews-top-stories",
        "type": "rss",
    },
    "Sky News": {
        "url": "https://news.sky.com/feeds/rss/home.xml",
        "type": "rss",
    },
    "ABC News": {
        "url": "https://abcnews.go.com/abcnews/topstories",
        "type": "rss",
    }
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


# ─────────────────────────────────────────
#  SCRAPER FUNCTIONS
# ─────────────────────────────────────────

def scrape_rss(name: str, url: str, verbose: bool = True) -> list[dict]:
    """Scrape headlines from an RSS feed."""
    headlines = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "lxml-xml")
        items = soup.find_all("item")

        for item in items[:15]:  # top 15 headlines
            title = item.find("title")
            link  = item.find("link")
            pub   = item.find("pubDate")
            desc  = item.find("description")

            # AI Intelligence: Sentiment & Summary
            full_text = f"{title.text if title else ''} {desc.text if desc else ''}"
            sentiment = "Neutral"
            polarity = 0.0
            entities = []
            
            try:
                blob = TextBlob(full_text)
                if blob.sentiment.polarity > 0.1: sentiment = "Positive"
                elif blob.sentiment.polarity < -0.1: sentiment = "Negative"
                polarity = round(blob.sentiment.polarity, 2)
                entities = [word for word, tag in blob.tags if tag in ('NNP', 'NNPS')][:5]
            except Exception:
                # Fallback for simple keyword-based sentiment if TextBlob fails
                if any(w in full_text.lower() for w in ['success', 'good', 'growth', 'positive']): sentiment = "Positive"
                elif any(w in full_text.lower() for w in ['attack', 'crisis', 'death', 'negative']): sentiment = "Negative"

            # Better Date Parsing
            import email.utils
            timestamp = datetime.now().isoformat()
            try:
                if pub:
                    dt = email.utils.parsedate_to_datetime(pub.text.strip())
                    timestamp = dt.isoformat()
            except:
                pass

            headlines.append({
                "source":      name,
                "title":       title.text.strip()   if title else "N/A",
                "link":        link.text.strip()     if link  else "N/A",
                "published":   pub.text.strip()[:25] if pub   else "N/A",
                "timestamp":   timestamp,
                "description": desc.text.strip()     if desc  else "N/A",
                "sentiment":   sentiment,
                "polarity":    polarity,
                "entities":    entities,
                "scraped_at":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })

        if verbose:
            console.print(f"  [green]✓[/green] {name} — {len(headlines)} headlines")
    except Exception as e:
        if verbose:
            console.print(f"  [red]✗[/red] {name} — Error: {e}")

    return headlines


def scrape_all(verbose: bool = True) -> list[dict]:
    """Scrape all configured sources."""
    all_headlines = []
    if verbose:
        console.print("\n[bold yellow]📡 Scraping news sources...[/bold yellow]\n")

    for name, config in SOURCES.items():
        if config["type"] == "rss":
            data = scrape_rss(name, config["url"], verbose=verbose)
            all_headlines.extend(data)

    return all_headlines


# ─────────────────────────────────────────
#  DISPLAY
# ─────────────────────────────────────────

def display_table(headlines: list[dict], source_filter: str = None):
    """Display headlines in a rich table."""
    filtered = headlines
    if source_filter:
        filtered = [h for h in headlines if source_filter.lower() in h["source"].lower()]

    table = Table(
        title=f"📰 News Headlines — {datetime.now().strftime('%d %b %Y, %H:%M')}",
        show_header=True,
        header_style="bold cyan",
        border_style="bright_black",
        show_lines=True,
    )

    table.add_column("#",       style="dim",    width=4)
    table.add_column("Source",  style="magenta", width=16)
    table.add_column("Headline",style="white",   width=55)
    table.add_column("Published",style="yellow", width=22)

    for i, h in enumerate(filtered[:30], 1):
        table.add_row(
            str(i),
            h["source"],
            h["title"],
            h["published"],
        )

    console.print(table)


# ─────────────────────────────────────────
#  SAVE FUNCTIONS
# ─────────────────────────────────────────

def save_csv(headlines: list[dict], filename: str = "headlines.csv"):
    """Save headlines to CSV."""
    if not headlines:
        return
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headlines[0].keys())
        writer.writeheader()
        writer.writerows(headlines)
    console.print(f"\n[green]💾 Saved to {filename}[/green]")


def save_json(headlines: list[dict], filename: str = "headlines.json"):
    """Save headlines to JSON."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(headlines, f, indent=2, ensure_ascii=False)
    console.print(f"[green]💾 Saved to {filename}[/green]")


# ─────────────────────────────────────────
#  SEARCH / FILTER
# ─────────────────────────────────────────

# ─────────────────────────────────────────
#  STORY CLUSTERING & ANALYSIS
# ─────────────────────────────────────────

def cluster_headlines(headlines: list[dict], threshold: float = 0.35) -> list[dict]:
    """Group similar headlines into clusters (Stories)."""
    if not headlines: return []
    
    if HAS_SKLEARN:
        titles = [h["title"] for h in headlines]
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(titles)
        
        # Calculate Similarity
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    else:
        # Fallback to Jaccard similarity using pure Python
        import re
        n = len(headlines)
        cosine_sim = np.zeros((n, n))
        stop_words = {'the', 'a', 'an', 'in', 'on', 'at', 'for', 'to', 'of', 'and', 'or', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'has', 'have', 'had', 'that', 'this', 'it'}
        word_sets = []
        for h in headlines:
            words = set(w.lower() for w in re.findall(r'\b\w{2,}\b', h["title"]) if w.lower() not in stop_words)
            word_sets.append(words)
            
        for i in range(n):
            for j in range(i, n):
                if i == j:
                    cosine_sim[i][j] = 1.0
                    continue
                s1 = word_sets[i]
                s2 = word_sets[j]
                if not s1 or not s2:
                    sim = 0.0
                else:
                    intersection = s1.intersection(s2)
                    union = s1.union(s2)
                    sim = len(intersection) / len(union) if union else 0.0
                cosine_sim[i][j] = sim
                cosine_sim[j][i] = sim
        # Adjust threshold for Jaccard (usually lower threshold represents similarity, e.g. 0.12)
        threshold = 0.12
    
    clusters = []
    visited = set()
    
    for i in range(len(headlines)):
        if i in visited: continue
        
        # Find similar headlines
        similar_indices = np.where(cosine_sim[i] > threshold)[0]
        cluster_items = [headlines[idx] for idx in similar_indices]
        
        for idx in similar_indices:
            visited.add(idx)
            
        # Create Story Object
        if cluster_items:
            # Confidence Score: 0-100 based on source count and diversity
            source_count = len(set(h["source"] for h in cluster_items))
            confidence = min(100, (source_count * 20) + (len(cluster_items) * 5))
            
            clusters.append({
                "main_title": cluster_items[0]["title"],
                "coverage_count": len(cluster_items),
                "source_count": source_count,
                "confidence_score": confidence,
                "sources": list(set(h["source"] for h in cluster_items)),
                "articles": cluster_items,
                "sentiment_avg": np.mean([h.get("polarity", 0) for h in cluster_items]),
                "latest_update": max([h["published"] for h in cluster_items])
            })
            
    return sorted(clusters, key=lambda x: x["coverage_count"], reverse=True)


def search_headlines(headlines: list[dict], query: str) -> list[dict]:
    """Advanced Search: Supports Regex and Boolean Logic."""
    import re
    query = query.strip()
    
    # Regex check
    is_regex = query.startswith("/") and query.endswith("/")
    
    results = []
    for h in headlines:
        text = f"{h['title']} {h['description']}".lower()
        
        if is_regex:
            try:
                pattern = query[1:-1]
                if re.search(pattern, text, re.I):
                    results.append(h)
            except:
                continue
        elif " and " in query.lower():
            parts = [p.strip().lower() for p in query.lower().split(" and ")]
            if all(p in text for p in parts):
                results.append(h)
        elif " or " in query.lower():
            parts = [p.strip().lower() for p in query.lower().split(" or ")]
            if any(p in text for p in parts):
                results.append(h)
        else:
            if query.lower() in text:
                results.append(h)
                
    return results


# ─────────────────────────────────────────
#  MAIN MENU
# ─────────────────────────────────────────

def main():
    console.print(Panel.fit(
        "[bold cyan]🗞️  NEWS HEADLINES SCRAPER[/bold cyan]\n"
        "[dim]Portfolio Project — Python + BeautifulSoup[/dim]",
        border_style="cyan"
    ))

    headlines = scrape_all()

    if not headlines:
        console.print("[red]No headlines fetched. Check your internet connection.[/red]")
        return

    console.print(f"\n[bold green]✅ Total headlines fetched: {len(headlines)}[/bold green]")

    while True:
        console.print("\n[bold]What do you want to do?[/bold]")
        console.print("  [cyan]1[/cyan] — View all headlines")
        console.print("  [cyan]2[/cyan] — Filter by source")
        console.print("  [cyan]3[/cyan] — Search by keyword")
        console.print("  [cyan]4[/cyan] — Save to CSV")
        console.print("  [cyan]5[/cyan] — Save to JSON")
        console.print("  [cyan]6[/cyan] — Re-scrape latest")
        console.print("  [cyan]0[/cyan] — Exit")

        choice = input("\n➤ Enter choice: ").strip()

        if choice == "1":
            display_table(headlines)

        elif choice == "2":
            sources = list(SOURCES.keys())
            for i, s in enumerate(sources, 1):
                console.print(f"  [cyan]{i}[/cyan] — {s}")
            sel = input("➤ Enter source number: ").strip()
            try:
                src = sources[int(sel) - 1]
                display_table(headlines, source_filter=src)
            except (ValueError, IndexError):
                console.print("[red]Invalid choice[/red]")

        elif choice == "3":
            kw = input("➤ Enter keyword to search: ").strip()
            results = search_headlines(headlines, kw)
            if results:
                display_table(results)
                console.print(f"[yellow]Found {len(results)} matching headlines[/yellow]")
            else:
                console.print(f"[red]No headlines found for '{kw}'[/red]")

        elif choice == "4":
            save_csv(headlines)

        elif choice == "5":
            save_json(headlines)

        elif choice == "6":
            headlines = scrape_all()
            console.print(f"[green]✅ Re-scraped! Total: {len(headlines)}[/green]")

        elif choice == "0":
            console.print("\n[bold cyan]👋 Bye bhai![/bold cyan]")
            break

        else:
            console.print("[red]Invalid option, try again[/red]")


if __name__ == "__main__":
    main()
