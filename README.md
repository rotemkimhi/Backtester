# 🏦 Backtester – Robust Strategy Backtesting App

> **Modern, fullstack, no-login strategy backtester. Upload OHLCV CSVs, select a machine-learning or classic strategy, get instant analytics and interactive equity curve charts.**

---

## ✨ Features

- **Upload any OHLCV CSV** – no account needed
- **Select from multiple strategies** (MLP, Decision Tree, XGBoost, Classic Backtest, etc.)
- **Interactive equity curve chart** with:
  - Custom zoom control (top left, draggable)
  - Pan by dragging the chart, just like TradingView
- **Modern UI** (TailwindCSS, Framer Motion, Radix Icons)
- **Python backend** for robust, extendable strategy logic

## 🚀 Getting Started

### 1. **Clone the repo**
```sh
git clone https://github.com/rotemkimhi/Backtester.git
cd Backtester
```
### 2. Start the backend
```sh
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
### 3. Start the frontend
```sh
cd ../frontend
npm install
npm run dev
```


🧠 ***How it works***

-**Upload CSV:** Drag-and-drop or use the upload button.

-**Load Strategy:** Pick any ML or classic strategy from the backend.

-**Backtest:** One click, instantly see performance metrics and animated charts.

-**Zoom and Pan:** Use the top-left zoom slider, or drag to pan the equity curve.



📦 ***Technologies Used***

-**Frontend:** React, TypeScript, Vite, TailwindCSS, Framer Motion, Recharts

-**Backend:** Python, Flask, Pandas, CORS

