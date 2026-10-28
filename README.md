# 📈 Real-Time US Stock Market Analytics Dashboard

> An end-to-end automated stock market analytics pipeline that fetches live US stock data, processes it through a Python pipeline, and visualizes it on a professional Power BI dashboard — updating every 60 seconds.

---

## 🔴 Live Dashboard
👉 [**View Live Dashboard**](https://app.powerbi.com/view?r=eyJrIjoiM2EyODU1ZWEtNTBiMi00YTQyLTgyZTgtOTFiYjEyOGQxNmEyIiwidCI6ImFjYWM2YjRlLWQ4MDItNDZlOS1hYzYzLWY3NzI0YmRmZGI4MyJ9)  


---

## 📸 Screenshots

### Page 1 — Live Market Overview
![Page 1](screenshots/page1.png)

### Page 2 — Weekly Analysis
![Page 2](screenshots/page2.png)

### Python Pipeline Running
![Terminal](screenshots/terminal.png)

---

## 🏗️ Project Architecture

```
Yahoo Finance API (yfinance)
         ↓
   Python Pipeline (unified_stock.py)
         ↓
   ┌─────────────────────────────┐
   │                             │
stock_data.csv    metrics_data.csv    index_data.csv    live_index.csv
(Historical +     (Latest snapshot    (Index history)   (Live indices)
  Live prices)     per stock)
   │                             │
   └─────────────────────────────┘
         ↓
   Power BI Desktop
   ├── Page 1: Live Market Overview
   └── Page 2: Weekly Analysis
         ↓
   Published to Power BI Service (Public)
```

---

## 📊 Dashboard Features

### Page 1 — Live Market Overview
| Feature | Description |
|---------|-------------|
| 🏦 Market Indices | S&P 500, NASDAQ, DOW JONES — live values |
| 💰 Stock Price Cards | AAPL, MSFT, GOOGL, AMZN, TSLA — individual live prices |
| 📈 Price Timeline Chart | Historical + live unified price chart |
| 📊 Volume Bar Chart | Trading volume comparison across stocks |
| 🏆 Top Performer | Best performing stock today |
| 💀 Worst Performer | Worst performing stock today |
| 📅 Top Weekly Gainer | Best stock this week |
| 📉 Worst Weekly Loser | Worst stock this week |

### Page 2 — Weekly Analysis
| Feature | Description |
|---------|-------------|
| 🗺️ Volume Treemap | Volume breakdown by stock |
| 📊 Volume + Price Combo | Total volume movement with avg price overlay |
| 📅 Weekly % Change | Bar chart showing weekly gains/losses |
| ⚡ Volatility Index | Average daily price swing per stock |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.11 | Data ingestion + pipeline automation |
| yfinance | Real US stock price fetching |
| pandas | Data processing + CSV management |
| requests | REST API calls to Power BI |
| Power BI Desktop | Dashboard development |
| Power BI Service | Cloud publishing + sharing |
| DAX | Custom KPI measures |

---

## 📁 Project Structure

```
RealTime-US-Stock-Dashboard/
│
├── unified_stock.py        # Main pipeline script
├── stock_stream.py         # Original streaming script
├── Real_Time_Dashboard.pbix # Power BI dashboard file
│
├── stock_data.csv          # Historical + live price data
├── metrics_data.csv        # Latest metrics per stock
├── index_data.csv          # Historical index data
├── live_index.csv          # Live index values
│
└── README.md
```

---

## ⚙️ How It Works

### Python Pipeline (`unified_stock.py`)

**On startup:**
1. Fetches 1 year of historical daily data for all 5 stocks
2. Fetches 1 year of historical data for S&P 500, NASDAQ, DOW
3. Saves to CSV files

**Every 60 seconds:**
1. Fetches latest stock prices via yfinance
2. Calculates metrics:
   - Day % change (vs today's open)
   - Week % change (vs Monday open)
   - 52-week high/low
   - Volatility (avg daily range %)
3. Appends new row to `stock_data.csv` (unified timeline)
4. Overwrites `metrics_data.csv` (always latest 5 rows)
5. Fetches live S&P 500, NASDAQ, DOW values
6. Overwrites `live_index.csv`
7. Pushes data to Power BI streaming dataset via REST API

### Power BI Dashboard

**4 data sources:**
- `stock_data.csv` → unified timeline chart (historical + live)
- `metrics_data.csv` → KPI cards + performer analysis
- `index_data.csv` → historical index chart
- `live_index.csv` → index KPI cards

**12 DAX Measures:**
- 5 individual stock price measures (AAPL, MSFT, GOOGL, AMZN, TSLA)
- Top/Worst daily performer
- Top/Worst weekly gainer/loser
- S&P 500, NASDAQ, DOW live values

---

## 🚀 How to Run

### Prerequisites
```bash
python -m pip install yfinance pandas requests
```

### Setup
1. Clone this repo
```bash
git clone https://github.com/NilakanthTalawar/RealTime-US-Stock-Dashboard.git
cd RealTime-US-Stock-Dashboard
```

2. Get Power BI Push URL:
   - Go to app.powerbi.com → My Workspace
   - Create new Streaming Dataset → API
   - Add fields: Symbol (Text), Price (Number), High (Number), Low (Number), Volume (Number), EventTime (DateTime)
   - Copy Push URL

3. Paste Push URL in script:
```python
# unified_stock.py line 8
PUSH_URL = "YOUR_POWER_BI_PUSH_URL_HERE"
```

4. Run pipeline:
```bash
python unified_stock.py
```

5. Open `Real_Time_Dashboard.pbix` in Power BI Desktop → Refresh

---

## 📈 Stocks Tracked
| Symbol | Company |
|--------|---------|
| AAPL | Apple Inc. |
| MSFT | Microsoft Corporation |
| GOOGL | Alphabet Inc. |
| AMZN | Amazon.com Inc. |
| TSLA | Tesla Inc. |

## 🏦 Indices Tracked
| Index | What it represents |
|-------|-------------------|
| S&P 500 | Top 500 US companies |
| NASDAQ | US tech-heavy index |
| DOW JONES | Top 30 US blue-chip companies |

---

## 💡 Key Learnings
- Built automated real-time data pipeline from scratch
- Integrated Python REST API with Power BI streaming dataset
- Designed multi-source data architecture (4 CSVs, different refresh strategies)
- Created 12 DAX measures for financial KPIs
- Implemented unified historical + live timeline visualization

---

## 👤 Author
**Neelakanth Talawar**  
Data Analytics Intern | Besant Technologies  
[LinkedIn](https://www.linkedin.com/in/nilakanth-talawar-820616246/) | [GitHub](https://github.com/NilakanthTalawar)

---

## ⭐ If you found this useful, please star the repo!
