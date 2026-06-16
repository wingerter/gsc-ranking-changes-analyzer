# 📉 GSC Ranking Changes Analyzer

A fast, local SEO dashboard for analyzing ranking and traffic changes from Google Search Console. Drop in the raw **date-comparison export** (`Queries.csv`), and instantly get topic clusters, prioritized ranking-drop analysis, and quick-win opportunities — no spreadsheets, no API keys, no data leaving your machine.

[![Live Demo](https://img.shields.io/badge/Live_Demo-Open_App-FF4B4B?logo=streamlit&logoColor=white)](https://gsc-ranking-changes-analyzer.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Built with Streamlit](https://img.shields.io/badge/Built_with-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)

> 🌍 *Read this in [German / Deutsch](README.de.md).*

**👉 Try it now — no install needed: [gsc-ranking-changes-analyzer.streamlit.app](https://gsc-ranking-changes-analyzer.streamlit.app/)**

![GSC Ranking Changes Analyzer dashboard](dasbhoard-20260613.png)

---

## 🌟 Key Features

- **🌐 Language- & format-independent (positional parsing):** It doesn't matter whether your GSC exports in German (`Häufigste Suchanfragen`) or English (`Top queries`), or whether decimals use a comma or a dot. The app detects encoding and separator automatically and reads each column by its fixed GSC position — never by header name.
- **🇬🇧🇩🇪 Bilingual UI:** Switch the entire dashboard between English and German with one click in the sidebar.
- **🧩 Local, dependency-light keyword clustering:** Groups thousands of keywords into topic clusters in milliseconds using frequency-based head-term matching (word counts minus stopwords). **No ML model, no external API, no cost** — and it runs entirely on your machine. Includes a best/worst-cluster heatmap.
- **🧠 Multi-dimensional Search Intent classification:** Detects user search intent (`KNOW`, `DO`, `regional:CITY`, `regional:COUNTRY`) separately from topic clusters, fully optimized for both English and German keywords. Includes visual intent distribution charts.
- **🎯 Precise change tagging:** Beyond simple differences, every keyword is tagged against hard ranking thresholds — `New`, `OoTop3`, `OoTop10`, `OoSERP2`, `OoTop100`, `IntoTop10`. Micro-movements (< 1.0 position) are cleanly separated as `None`, everything else as `Changed`.
- **🍎 Low Hanging Fruits:** Surfaces "threshold" keywords ranking on the top of page 2 (positions 11–15) that already generate real impressions — the fastest quick wins in SEO.
- **📊 Interactive dashboard:** An at-a-glance KPI matrix (total losses, net change, Top 3 & Top 10 drops, per-cluster performance) plus six interactive analysis tabs.

---

## 📑 The Six Analysis Tabs

Once you upload your `Queries.csv`, the app generates six interactive tabs:

1. **Topic Clusters** — Bundles click losses by head term, so you can instantly see if a whole topic (e.g. "winter tires" or "credit card") dropped collectively. Filter out brand keywords into a dedicated cluster.
2. **Ranking Drops** — Sorts drops into prioritized buckets:
   - **Top 3 Drops** — fell out of positions 1–3 (the painful ones).
   - **Top 10 Drops** — dropped off page 1.
   - **Page 2 Drops** — slid further back from page 2.
   - **Complete Losses** — fell out of the Top 100 entirely.
3. **Click Losses (Detail)** — The raw, hard list of every keyword that lost traffic, sorted by clicks lost.
4. **Low Hanging Fruits** — Threshold keywords on positions 11–15, sorted by current impressions. A few internal links or small content tweaks can push these onto page 1.
5. **Winners** — Keywords that gained clicks, with a bubble chart to visualize the wins.
6. **All Data** — The full export with every computed KPI (combined gain/loss metrics, position change, etc.) and interactive filters (cluster, change type, keyword search).

---

## ⚙️ How to Get the Data from GSC

The tool needs exactly **one** file:

1. Open **Google Search Console** for your domain.
2. Go to **Performance → Search results**.
3. Click the **date filter** at the top and choose the **Compare** tab (e.g. "Compare last 28 days to previous period").
4. Click **Apply**.
5. Click **Export** (top right) and choose **Download CSV**.
6. Unzip the downloaded file — inside you'll find `Queries.csv`.
7. Upload exactly that `Queries.csv` into the app.

---

## 🚀 Run It Locally

The app uses `streamlit` for the UI, `pandas` for data processing, and `plotly` for the charts. The quickest way to run it is with [`uv`](https://github.com/astral-sh/uv):

```bash
uv run --python 3.12 --with-requirements requirements.txt streamlit run app.py
```

`uv` installs the requirements on the fly in an isolated environment — no manual virtualenv needed. The terminal will print a local URL (usually `http://localhost:8501`); open it in your browser.

<details>
<summary>Prefer pip / a manual virtualenv?</summary>

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
</details>

---

## ☁️ Deploy to Streamlit Community Cloud

The project is cloud-ready and can be hosted for free in a few clicks:

1. Push this repo (`app.py` and `requirements.txt`) to GitHub.
2. Sign in at [share.streamlit.io](https://share.streamlit.io) with your GitHub account.
3. Click **New app**, select this repo, and set `app.py` as the main file.
4. Click **Deploy**. Done.

---

## 🔒 Privacy

All processing happens locally (or in your own Streamlit instance). Your `Queries.csv` is never sent to a third-party API — there are no external calls in the analysis pipeline.

---

## 📝 License & Credits

MIT License © 2026 Benjamin "SEOux Indianer" Wingerter
Made with ❤️ in Munich & Bangkok — [seouxindianer.de](https://seouxindianer.de)
