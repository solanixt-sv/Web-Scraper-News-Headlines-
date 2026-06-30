# 🗞️ News Headlines Scraper

A real-world Python web scraper that fetches live news headlines from multiple sources including **BBC News**, **Dawn Pakistan**, **Reuters**, and **Al Jazeera** — all from the command line.

> 💼 Built as a portfolio project to demonstrate web scraping, data handling, and CLI app development skills.

---

## ✨ Features

- 📡 Scrapes **4 major news sources** simultaneously
- 🔍 **Search headlines** by any keyword
- 🗂️ **Filter** by specific news source
- 💾 **Export** data to CSV or JSON
- 🔄 **Re-scrape** for latest news anytime
- 🎨 Beautiful **Rich CLI** interface with colors & tables

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| `requests` | HTTP requests to fetch RSS feeds |
| `BeautifulSoup4` | Parse and extract HTML/XML content |
| `lxml` | Fast XML parser for RSS feeds |
| `rich` | Beautiful terminal UI |
| `csv / json` | Data export |

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/news-scraper.git
cd news-scraper
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the scraper
```bash
python scraper.py
```

---

## 📸 Demo

```
╭──────────────────────────────────────╮
│  🗞️  NEWS HEADLINES SCRAPER          │
│  Portfolio Project — Python + BS4    │
╰──────────────────────────────────────╯

📡 Scraping news sources...

  ✓ BBC News        — 15 headlines
  ✓ Dawn (Pakistan) — 15 headlines
  ✓ Reuters         — 15 headlines
  ✓ Al Jazeera      — 15 headlines

✅ Total headlines fetched: 60

What do you want to do?
  1 — View all headlines
  2 — Filter by source
  3 — Search by keyword
  4 — Save to CSV
  5 — Save to JSON
  6 — Re-scrape latest
  0 — Exit
```

---

## 📁 Project Structure

```
news-scraper/
│
├── scraper.py          # Main scraper script
├── requirements.txt    # Dependencies
├── headlines.csv       # Output (auto-generated)
├── headlines.json      # Output (auto-generated)
└── README.md
```

---

## 🔧 How to Add More Sources

Add any RSS feed to the `SOURCES` dict in `scraper.py`:

```python
SOURCES = {
    "Your Source Name": {
        "url": "https://example.com/rss.xml",
        "type": "rss",
    },
}
```

---

## 📚 What I Learned

- Making HTTP requests with `requests`
- Parsing XML/HTML with `BeautifulSoup`
- Working with RSS feeds
- Building interactive CLI apps with `rich`
- Exporting data to CSV and JSON formats
- Error handling for network requests

---

## 👤 Author

**Your Name**  
[GitHub](https://github.com/YOUR_USERNAME) • [LinkedIn](https://linkedin.com/in/YOUR_USERNAME)

---

## 📄 License

MIT License — free to use and modify.
