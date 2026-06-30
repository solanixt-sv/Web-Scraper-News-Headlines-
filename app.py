from flask import Flask, request, render_template_string
from scraper import scrape_all, search_headlines, SOURCES

app = Flask(__name__)

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>News Headlines Scraper</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; background: #f7f7f7; color: #111; }
    h1 { margin-bottom: 8px; }
    form { display: flex; gap: 8px; flex-wrap: wrap; margin: 16px 0 20px; }
    input, select, button { padding: 8px 10px; border: 1px solid #ccc; border-radius: 8px; }
    button { background: #0b5ed7; color: white; border: none; cursor: pointer; }
    .meta { margin: 10px 0; color: #444; }
    .card { background: white; border: 1px solid #e7e7e7; border-radius: 10px; padding: 12px; margin-bottom: 10px; }
    .source { font-weight: bold; color: #0b5ed7; }
    .title { margin: 6px 0; }
    a { color: #0a58ca; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <h1>News Headlines Scraper</h1>
  <div class="meta">Running on localhost with live scrape results.</div>

  <form method="get" action="/">
    <input type="text" name="q" placeholder="Search keyword..." value="{{ q }}" />
    <select name="source">
      <option value="">All Sources</option>
      {% for src in sources %}
        <option value="{{ src }}" {% if src == selected_source %}selected{% endif %}>{{ src }}</option>
      {% endfor %}
    </select>
    <button type="submit">Refresh</button>
  </form>

  <div class="meta">Total headlines shown: {{ headlines|length }}</div>

  {% for h in headlines %}
    <div class="card">
      <div class="source">{{ h.source }}</div>
      <div class="title">{{ h.title }}</div>
      <div><small>{{ h.published }}</small></div>
      <div><a href="{{ h.link }}" target="_blank" rel="noreferrer">Open article</a></div>
    </div>
  {% endfor %}
</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    q = request.args.get("q", "").strip()
    source = request.args.get("source", "").strip()

    headlines = scrape_all(verbose=False)

    if source:
        headlines = [h for h in headlines if h["source"] == source]
    if q:
        headlines = search_headlines(headlines, q)

    return render_template_string(
        HTML,
        headlines=headlines,
        q=q,
        selected_source=source,
        sources=list(SOURCES.keys()),
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
