# 📊 Financial Risk Predictor — Project Explanation

## Overview

The **Financial Risk Predictor** is an AI-driven stock screening and risk classification tool built for academic research at PDEU. It analyzes ~1000 companies using 19 fundamental financial ratios, computes a proprietary **M-Score** (0–100), and classifies each stock into **Low**, **Medium**, or **High Risk** categories.

The project combines two approaches:
1. **Rule-based scoring** — A custom M-Score derived from percentile-ranked financial metrics
2. **Machine Learning** — Multiple classifiers (Random Forest, XGBoost, CatBoost, etc.) trained on the same financial data

---

## Problem Statement

Traditional financial risk assessment relies on manual thresholds and isolated metrics. Investors often evaluate growth OR value in isolation, missing the full picture. This project bridges that gap by:

- Integrating **19 key financial ratios** into a single composite score
- Using **market-relative percentile ranking** instead of static thresholds
- Comparing **5 ML algorithms** to validate the scoring methodology
- Providing an **interactive screener** for stock filtering

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3** | Core language for all scripts |
| **pandas** | Data loading, manipulation, ranking |
| **scikit-learn** | ML models (SVM, Random Forest, GBM), metrics, train-test split |
| **XGBoost** | Gradient boosting classifier |
| **CatBoost** | Gradient boosting with categorical feature support |
| **matplotlib** | Chart generation (scatter, bar, confusion matrix) |
| **seaborn** | Statistical visualization (heatmaps, styled scatter plots) |
| **openpyxl** | Excel file I/O |
| **HTML/CSS** | Academic poster presentation |

---

## Dataset

**Source**: `data/norm-data.xlsx` (Sheet: `Train_Normalized`)

- **~1000 companies** with pre-normalized financial data
- **21 columns**: 2 identifiers (`Company_Name`, `Sector`), 19 financial ratios, and 1 target label (`Total_Label_Score`)

### Financial Ratios Used

| Category | Ratios |
|---|---|
| **Valuation** | P/E Ratio, P/S Ratio, EV/EBITDA, P/B Ratio |
| **Profitability** | ROE, ROCE, Profit Margin, EBITDA Margin |
| **Quality / Solvency** | Debt-to-Equity, Interest Coverage, Current Ratio, Quick Ratio, Net Debt/EBITDA, Cash Ratio |
| **Growth** | Revenue CAGR (3Y), YoY Revenue Growth, Stock Return (3Y) |
| **Efficiency** | Asset Turnover, Inventory Turnover |

---

## Core Methodology: The M-Score

The M-Score is a **weighted composite percentile-rank score** from 0 to 100.

### Step 1: Percentile Ranking

Each company is ranked against all others for each metric. Metrics where higher values indicate better performance (e.g., ROE) get direct percentile ranks. Metrics where lower values are better (e.g., Debt-to-Equity) get **inverted** ranks.

```
Higher-is-better:  Rank = percentile_rank(value) × 100
Lower-is-better:   Rank = (1 − percentile_rank(value)) × 100
```

### Step 2: Four-Pillar Aggregation

The ranks are grouped into four investment pillars:

| Pillar | Weight | Metrics Included |
|---|---|---|
| **Quality (Q)** | 30% | Interest Coverage, Current Ratio, Debt-to-Equity (inverted) |
| **Growth (G)** | 30% | Revenue CAGR 3Y, YoY Revenue Growth, ROE, ROCE |
| **Value (V)** | 20% | P/E Ratio (inverted), P/B Ratio (inverted) |
| **Efficiency (E)** | 20% | Asset Turnover, Inventory Turnover |

### Step 3: Final Score

```
M_Score = (Q × 0.30) + (G × 0.30) + (V × 0.20) + (E × 0.20)
```

### Step 4: Risk Classification

| M-Score | Risk Category | Interpretation |
|---|---|---|
| **≥ 70** | ✅ Low Risk (Elite) | Strong financial performer |
| **45 – 69** | ⚖️ Medium Risk (Neutral) | Hold / watchlist |
| **< 45** | 🚨 High Risk (Avoid) | Financial weakness detected |

---

## Project Scripts

### 1. `scoring-engine.py` — M-Score Calculator

The core scoring engine that:
- Loads normalized data from Excel
- Computes percentile ranks for all 11 relevant metrics
- Calculates the weighted M-Score for each company
- Assigns a risk verdict (Low / Medium / High)
- Saves results to `data/final_stock_rankings.xlsx`
- Includes a CLI lookup to verify individual company scores

**Input**: `data/norm-data.xlsx`
**Output**: `data/final_stock_rankings.xlsx`

---

### 2. `model_comparison.py` — ML Model Benchmark

Benchmarks 5 classification algorithms on the same dataset:

| Model | Config |
|---|---|
| SVM | `SVC(probability=True)` |
| Random Forest | 100 estimators |
| Gradient Boosting | 100 estimators |
| XGBoost | `eval_metric='mlogloss'` |
| CatBoost | 100 iterations, silent |

- Uses all 19 financial ratios as features
- Target: `Total_Label_Score` (multi-class)
- 80/20 train-test split (`random_state=42`)
- Outputs formatted accuracy comparison table

**Input**: `data/norm-data.xlsx`
**Output**: Console table with train/test accuracy per model

---

### 3. `model_evaluation.py` — Champion Model Deep Evaluation

Deep evaluation of Random Forest (selected as "champion model"):

- Trains with **200 estimators** (vs 100 in comparison)
- Reports: Accuracy, Log Loss, full Classification Report
- Generates two visualizations:
  - **Confusion Matrix** — Heatmap of predicted vs actual labels
  - **Feature Importance** — Bar chart showing which ratios matter most

**Input**: `data/norm-data.xlsx`
**Output**: `confusion_matrix.png`, `feature_importance.png`

---

### 4. `market-visualization.py` — Dashboard Generator

Creates a 2-panel visual dashboard:

- **Panel 1 — Scatter Plot**: Growth Score vs Value Score, color-coded by risk category, with top 5 stocks labeled
- **Panel 2 — Pie Chart**: Market-wide risk distribution (% of companies in each risk category)

Uses the green/orange/red color palette: `#2ecc71`, `#f39c12`, `#e74c3c`

**Input**: `data/norm-data.xlsx`
**Output**: `market_dashboard.png`

---

### 5. `stock-screener.py` — Interactive CLI Screener

An interactive command-line tool for filtering stocks:

- Prompts for a minimum M-Score threshold
- Displays all matching companies sorted by score (descending)
- Shows Company Name, Sector, and Score
- Loops for multiple searches until user exits

**Prerequisite**: Must run `scoring-engine.py` first to generate rankings.

**Input**: `data/final_stock_rankings.xlsx`
**Output**: Console-formatted filtered results

---

### 6. `poster.html` — Academic Poster

A 1200×1696px HTML/CSS poster presentation with:
- University header (SoT / PDEU branding)
- Sections: Introduction & Objectives, Research Gaps, Methodology, Results, Conclusion, References
- Embedded `market_dashboard.png` visualization
- Model comparison accuracy table
- Green (#8CC63F) theme throughout

---

## Execution Flow

```
┌─────────────────────┐
│  norm-data.xlsx     │ (primary dataset)
└────┬───┬───┬───┬────┘
     │   │   │   │
     ▼   │   │   │
┌────────────────┐ │   │   │
│ scoring-engine │ │   │   │
│    .py         │ │   │   │
└───────┬────────┘ │   │   │
        │          │   │   │
        ▼          │   │   │
┌──────────────┐   │   │   │
│ final_stock_ │   │   │   │
│ rankings.xlsx│   │   │   │
└───────┬──────┘   │   │   │
        │          │   │   │
        ▼          ▼   ▼   ▼
┌────────────┐ ┌─────┐┌─────┐┌──────────┐
│  stock-    │ │model││model││ market-  │
│  screener  │ │comp.││eval.││ visual.  │
│  .py       │ │ .py ││ .py ││  .py     │
└────────────┘ └─────┘└──┬──┘└────┬─────┘
                         │        │
                    ┌────┴───┐ ┌──┴──────────┐
                    │confus. │ │market_      │
                    │matrix  │ │dashboard.png│
                    │.png    │ └─────────────┘
                    │feature │
                    │_imp.png│
                    └────────┘
```

---

## Key Results (from poster)

| Model | Test Accuracy |
|---|---|
| Random Forest | 99.5% |
| Gradient Boosting | 99.0% |
| CatBoost | 99.5% |

**Champion**: Random Forest Classifier with 200 estimators, validated at **99.5% accuracy** with low log loss.

---

## How to Run

```bash
# 1. Install dependencies
pip install pandas openpyxl matplotlib seaborn scikit-learn xgboost catboost

# 2. Run scoring engine (generates rankings)
python scoring-engine.py

# 3. Run model comparison
python model_comparison.py

# 4. Run champion model evaluation
python model_evaluation.py

# 5. Generate market dashboard
python market-visualization.py

# 6. Run interactive stock screener
python stock-screener.py
```

---

## Future Work

- **Real-time API integration** — Replace static Excel data with live stock quotes (e.g., via Yahoo Finance API)
- **Web dashboard** — Convert CLI tools into a Streamlit or Flask web app
- **Model persistence** — Save trained models with `joblib` for instant inference
- **Cross-validation** — Implement k-fold CV for statistically robust evaluation
- **Feature engineering** — Add momentum indicators, sector-relative metrics
