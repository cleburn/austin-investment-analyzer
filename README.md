# Texas Real Estate Investment Analyzer

**AI-powered tool that helps real estate investors identify the best neighborhoods in Austin based on cash flow potential and appreciation metrics.**

---

## 🎯 The Problem

Real estate investors spend hours manually comparing neighborhoods, calculating ROI, and searching for properties that match their investment strategy. The process is:
- **Time-consuming:** Dozens of neighborhoods to evaluate across multiple data sources
- **Complex:** Requires understanding of cash flow formulas, appreciation trends, and market cycles
- **Overwhelming:** Balancing budget constraints with investment goals (cash flow vs. long-term growth)

**This tool automates the entire research process and delivers ranked recommendations in seconds.**

---

## 💡 What It Does

The analyzer takes three inputs from you:
1. **Budget Range** (e.g., $250K - $400K)
2. **Investment Strategy** (Cash Flow or Appreciation)
3. **Rental Type** (Short-term rental (Airbnb) or Long-term rental)

Then it:
- Filters 185 Austin neighborhoods to match your budget
- Ranks them based on your chosen strategy
- Returns the **top 3 neighborhoods** with detailed metrics:
  - Expected monthly cash flow (STR and LTR)
  - Historical appreciation rates (2015-2019 baseline)
  - Current market position (distance from 2022 peak)
  - Confidence indicators (number of comparable listings)

---

## 🔍 How It Works

### Data Sources
The tool combines three public datasets to create a complete picture:

1. **Zillow Home Value Index (ZHVI)** — Neighborhood-level median home prices from 2000-2025
2. **Zillow Observed Rent Index (ZORI)** — Long-term rental rates by neighborhood
3. **Inside Airbnb** — 15,000+ short-term rental listings with occupancy and income data

### Analysis Engine
For each neighborhood, the tool calculates:

**Cash Flow Strategy Metrics:**
- Monthly short-term rental (STR) income: `nightly rate × 30 days × occupancy rate`
- Monthly long-term rental (LTR) estimate: `STR income ÷ 2.5` (industry standard)
- Monthly costs: Mortgage (20% down, 7% interest) + taxes (1.2%) + insurance (0.5%) + maintenance (1%)
- **Net cash flow:** `Income - Costs`

**Appreciation Strategy Metrics:**
- Pre-pandemic baseline growth rate (2015-2019 CAGR)
- Current recovery trajectory (2023-2025 CAGR)
- Distance from 2022 market peak (shows potential upside)

### Ranking System
Neighborhoods are ranked by the metric that matters most to your strategy:
- **Cash Flow investors:** Sorted by highest monthly profit
- **Appreciation investors:** Sorted by strongest historical growth

Only neighborhoods with **10+ Airbnb listings** are included (ensures reliable data).

---

## 📊 Key Insights from Current Data

**Austin Market Reality (as of October 2025):**
- **Cash Flow via STR is viable** — Top neighborhoods generate $400-$5,000/month positive cash flow
- **Cash Flow via LTR is difficult** — Most neighborhoods show negative cash flow at current interest rates (7%)
- **Appreciation opportunity exists** — Top growth neighborhoods are 25-35% below their 2022 peaks
- **Budget sweet spot:** $250K-$400K properties offer the best risk-adjusted returns

**Top Performers:**
- **Coronado Hills:** $308K, +$5,071/month STR cash flow (28.8% annual return on price)
- **North Lamar:** $292K, +$856/month STR cash flow + 11.4% historical appreciation
- **Georgian Acres:** $291K, +$713/month STR cash flow + 11.8% historical appreciation

---

## 🚀 What's Next

### Current Version (MVP)
This is a **proof-of-concept** demonstrating the analysis pipeline:
- ✅ Data ingestion and cleaning
- ✅ Neighborhood-level metrics calculation
- ✅ Strategy-based ranking system
- ✅ User input processing

### Roadmap (Future Iterations)
**Phase 2 (Weeks 5-6):**
- Add interactive visualizations (neighborhood comparison charts, price trend graphs)
- Manual example listings from Zillow (2-3 properties per recommended neighborhood)
- Streamlit web interface (no coding required to use the tool)

**Phase 3 (Months 2-3):**
- Expand to Houston, Dallas, San Antonio
- Add financing scenario calculator (different down payments, interest rates)
- Include off-market deal sources (wholesalers, foreclosures)
- Property condition assessment (turnkey vs. rehab required)

**Phase 4 (Months 4-6):**
- Real-time MLS integration
- Automated listing alerts when new opportunities match criteria
- Portfolio optimization (suggest best mix of neighborhoods for diversification)

---

## 🛠️ Technical Stack

**Data Processing:**
- Python 3.11
- Pandas (data manipulation)
- NumPy (numerical calculations)

**Analysis:**
- Scikit-learn (future: predictive modeling)
- SciPy (statistical metrics)

**Visualization (coming soon):**
- Matplotlib & Seaborn (charts)
- Plotly (interactive dashboards)

**Deployment (coming soon):**
- Streamlit (web interface)
- GitHub Pages (portfolio hosting)

---

## 📁 Project Structure

```
austin-investment-analyzer/
├── notebooks/
│   └── texas-real-estate-analyzer.ipynb  # Main analysis notebook
├── data/
│   ├── raw/                              # Original datasets (not in Git)
│   └── processed/                        # Cleaned data (not in Git)
├── visuals/                              # Charts and graphs (coming soon)
├── .gitignore
└── README.md
```

---

## 🎓 Background

This project is part of a 9-month AI Engineer roadmap focused on building practical, income-generating tools at the intersection of real estate investment and data science.

**Why Austin?**
- Strong market fundamentals (top 10 US metro for growth)
- Rich public data availability
- High short-term rental demand (tourism + business travel)
- Personal expertise: 5+ years managing investment properties in Texas

**Methodology:**
The analysis approach prioritizes **conservative assumptions** over optimistic projections:
- 7% mortgage rates (current market reality, not historical lows)
- Full operating expense modeling (taxes, insurance, maintenance, vacancies)
- Real occupancy data (not theoretical maximums)
- Pre-pandemic growth baselines (excludes 2020-2022 anomaly spike)

This ensures recommendations remain viable even in less-than-ideal market conditions.

---

## 📬 Contact & Feedback

**Cleburn Walker**  
[LinkedIn](https://linkedin.com/in/cleburnwalker) | [GitHub](https://github.com/cleburn)

**For Investors:**  
Interested in using this tool or exploring collaboration? Let's connect.

**For Developers:**  
Feedback, contributions, and suggestions welcome. This is an active learning project.

---

## 📄 License

This project is open source and available for educational and personal use. Data sources retain their original licensing terms.

---

**Last Updated:** October 21, 2025  
**Status:** MVP Complete — Visualization & UI phases in progress