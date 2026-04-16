# Financial Risk Predictor — Complete Codebase Reference

> **CONTEXT FOR CLAUDE**: This file contains the ENTIRE codebase of a Financial Risk Predictor project. Use this as your ground truth for all source code. The project is a Python-based academic fintech tool that classifies stocks into Low/Medium/High risk categories using a custom "M-Score" and compares several ML classifiers.

---

## Project Structure

```
Financial-risk-predictor/
├── data/
│   ├── norm-data.xlsx              # Primary dataset (sheet: Train_Normalized, ~1000 companies, 21 columns)
│   ├── final_stock_rankings.xlsx   # Output of scoring-engine.py
│   └── ~$norm-data.xlsx            # Excel lock file (ignore)
├── scoring-engine.py               # M-Score calculator + CLI company lookup
├── model_comparison.py             # 5-model ML accuracy benchmark
├── model_evaluation.py             # Deep eval of champion model (Random Forest)
├── market-visualization.py         # Scatter + pie chart dashboard
├── stock-screener.py               # Interactive CLI stock filter
├── model-preprocess-code.py        # ⚠️ EMPTY (placeholder, never implemented)
├── poster.html                     # Academic poster (HTML/CSS, 294 lines)
├── market_dashboard.png            # Generated scatter+pie visualization
├── market_map.png                  # Another generated visualization
├── synthetic_train_test(1) (1).xlsx # Raw/backup dataset
├── execution_results.txt           # Partial log (just 1 line of output)
├── requirements.txt                # ⚠️ EMPTY (never populated)
├── .gitignore                      # Python/CatBoost ignores; also ignores README.md (bug)
└── .venv/                          # Local virtual environment
```

---

## Data Schema: `data/norm-data.xlsx` → Sheet `Train_Normalized`

~1000 rows (companies). Each row has:

| Column | Category | Used in M-Score? | Used in ML? | Direction for Ranking |
|---|---|---|---|---|
| `Company_Name` | ID | — | — | — |
| `Sector` | ID | — | — | — |
| `P_E_Ratio` | Valuation | ✅ (inverted) | ✅ | Lower = better |
| `P_S_Ratio` | Valuation | ❌ | ✅ | — |
| `EV_EBITDA` | Valuation | ❌ | ✅ | — |
| `P_B_Ratio` | Valuation | ✅ (inverted) | ✅ | Lower = better |
| `ROE` | Growth | ✅ | ✅ | Higher = better |
| `ROCE` | Growth | ✅ | ✅ | Higher = better |
| `Profit_Margin` | Profitability | ❌ | ✅ | — |
| `EBITDA_Margin` | Profitability | ❌ | ✅ | — |
| `Debt_to_Equity` | Quality | ✅ (inverted) | ✅ | Lower = better |
| `Interest_Coverage` | Quality | ✅ | ✅ | Higher = better |
| `Current_Ratio` | Liquidity | ✅ | ✅ | Higher = better |
| `Quick_Ratio` | Liquidity | ❌ | ✅ | — |
| `Net_Debt_to_EBITDA` | Leverage | ❌ | ✅ | — |
| `Cash_Ratio` | Liquidity | ❌ | ✅ | — |
| `Revenue_CAGR_3Y` | Growth | ✅ | ✅ | Higher = better |
| `Stock_Return_3Y` | Performance | ❌ | ✅ | — |
| `YoY_Revenue_Growth` | Growth | ✅ | ✅ | Higher = better |
| `Asset_Turnover` | Efficiency | ✅ | ✅ | Higher = better |
| `Inventory_Turnover` | Efficiency | ✅ | ✅ | Higher = better |
| `Total_Label_Score` | **TARGET** | — | ✅ (target) | Multi-class label |

---

## M-Score Methodology

### Percentile Ranking
```
Higher-is-better:  rank = percentile_rank(column) × 100
Lower-is-better:   rank = (1 − percentile_rank(column)) × 100
```

### Four Pillars → Weighted Composite

| Pillar | Weight | Metrics |
|---|---|---|
| Quality (Q) | 30% | Interest_Coverage, Current_Ratio, Debt_to_Equity (inv) |
| Growth (G) | 30% | Revenue_CAGR_3Y, YoY_Revenue_Growth, ROE, ROCE |
| Value (V) | 20% | P_E_Ratio (inv), P_B_Ratio (inv) |
| Efficiency (E) | 20% | Asset_Turnover, Inventory_Turnover |

**Formula**: `M_Score = Q×0.3 + G×0.3 + V×0.2 + E×0.2`

### Risk Thresholds

| Score | Category |
|---|---|
| ≥ 70 | Low Risk (Elite) |
| 45–69 | Medium Risk (Neutral) |
| < 45 | High Risk (Avoid) |

---

## Pipeline Execution Order

```
1. scoring-engine.py     → reads norm-data.xlsx → writes final_stock_rankings.xlsx
2. model_comparison.py   → reads norm-data.xlsx → prints accuracy table
3. model_evaluation.py   → reads norm-data.xlsx → saves confusion_matrix.png, feature_importance.png
4. market-visualization.py → reads norm-data.xlsx → saves market_dashboard.png
5. stock-screener.py     → reads final_stock_rankings.xlsx (needs step 1 first)
```

---

## SOURCE CODE

### File 1: `scoring-engine.py` (48 lines)

```python
import pandas as pd
import os

# 1. Load Data
file_path = os.path.join('data', 'norm-data.xlsx')
df = pd.read_excel(file_path, sheet_name='Train_Normalized')

# 2. Recalibrate logic using Percentile Ranks (Market Relative)
print("Recalibrating M-Scores for all companies...")
ranked_df = pd.DataFrame(index=df.index)

# Higher is better
for col in ['Interest_Coverage', 'Current_Ratio', 'ROE', 'ROCE', 
            'Revenue_CAGR_3Y', 'YoY_Revenue_Growth', 'Asset_Turnover', 'Inventory_Turnover']:
    ranked_df[col + '_Rank'] = df[col].rank(pct=True) * 100

# Lower is better (Invert Rank)
ranked_df['DE_Rank'] = (1 - df['Debt_to_Equity'].rank(pct=True)) * 100
ranked_df['PE_Rank'] = (1 - df['P_E_Ratio'].rank(pct=True)) * 100
ranked_df['PB_Rank'] = (1 - df['P_B_Ratio'].rank(pct=True)) * 100

def calculate_m_score(row):
    q = (row['Interest_Coverage_Rank'] + row['Current_Ratio_Rank'] + row['DE_Rank']) / 3
    g = (row['Revenue_CAGR_3Y_Rank'] + row['YoY_Revenue_Growth_Rank'] + row['ROE_Rank'] + row['ROCE_Rank']) / 4
    v = (row['PE_Rank'] + row['PB_Rank']) / 2
    e = (row['Asset_Turnover_Rank'] + row['Inventory_Turnover_Rank']) / 2
    return round((q * 0.3) + (g * 0.3) + (v * 0.2) + (e * 0.2), 2)

# 3. Save the NEW Scores
df['M_Score'] = ranked_df.apply(calculate_m_score, axis=1)

def get_verdict(score):
    if score >= 70: return "✅ LOW RISK (Strong Performer)"
    elif score >= 45: return "⚖️ MEDIUM RISK (Neutral/Hold)"
    else: return "🚨 HIGH RISK (Financial Weakness)"

df['Risk_Verdict'] = df['M_Score'].apply(get_verdict)

# OVERWRITE the Excel file with corrected scores
output_path = os.path.join('data', 'final_stock_rankings.xlsx')
df.to_excel(output_path, index=False)
print(f"✅ Success! Updated scores for {len(df)} companies saved to {output_path}")

# 4. Search Check
query = input("\nEnter a company name to verify (e.g. Anant Raj): ")
res = df[df['Company_Name'].str.contains(query, case=False, na=False)]
if not res.empty:
    print(f"M-Score: {res.iloc[0]['M_Score']} | Verdict: {res.iloc[0]['Risk_Verdict']}")
```

---

### File 2: `model_comparison.py` (62 lines)

```python
import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from catboost import CatBoostClassifier
from sklearn.metrics import accuracy_score

# 1. Setup File Path (Looking inside the 'data' folder)
file_path = os.path.join('data', 'norm-data.xlsx')
sheet_name = 'Train_Normalized'

if not os.path.exists(file_path):
    print(f"Error: {file_path} not found. Ensure 'norm-data.xlsx' is inside the 'data' folder.")
    exit()

# 2. Load Data
print(f"Reading {sheet_name} from {file_path}...")
df = pd.read_excel(file_path, sheet_name=sheet_name)

# 3. Define Features and Target
features = [
    'P_E_Ratio', 'P_S_Ratio', 'EV_EBITDA', 'P_B_Ratio', 'ROE', 'ROCE',
    'Profit_Margin', 'EBITDA_Margin', 'Debt_to_Equity', 'Interest_Coverage',
    'Current_Ratio', 'Quick_Ratio', 'Net_Debt_to_EBITDA', 'Cash_Ratio',
    'Revenue_CAGR_3Y', 'Stock_Return_3Y', 'YoY_Revenue_Growth', 'Asset_Turnover',
    'Inventory_Turnover'
]
target = 'Total_Label_Score'

# 4. 80/20 Split
X = df[features]
y = df[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Initialize Models
models = {
    "SVM": SVC(probability=True, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "GBM": GradientBoostingClassifier(n_estimators=100, random_state=42),
    "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42),
    "CatBoost": CatBoostClassifier(
        iterations=100, 
        verbose=0, 
        random_state=42, 
        allow_writing_files=False # Prevents catboost_info folder
    )
}

# 6. Run Comparison
print("\n" + "="*55)
print(f"{'Model':<20} | {'Train Accuracy':<15} | {'Test Accuracy':<15}")
print("-" * 55)

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    train_acc = accuracy_score(y_train, y_pred_train)
    test_acc = accuracy_score(y_test, y_pred_test)
    print(f"{name:<20} | {train_acc:.4f}          | {test_acc:.4f}")
```

---

### File 3: `model_evaluation.py` (71 lines)

```python
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier # Change this if CatBoost was your winner
from sklearn.metrics import log_loss, classification_report, confusion_matrix, accuracy_score

# 1. Setup File Path
file_path = os.path.join('data', 'norm-data.xlsx')
sheet_name = 'Train_Normalized'

if not os.path.exists(file_path):
    print(f"Error: {file_path} not found.")
    exit()

# 2. Load Data
print(f"Loading {sheet_name} for deep evaluation...")
df = pd.read_excel(file_path, sheet_name=sheet_name)

features = [
    'P_E_Ratio', 'P_S_Ratio', 'EV_EBITDA', 'P_B_Ratio', 'ROE', 'ROCE',
    'Profit_Margin', 'EBITDA_Margin', 'Debt_to_Equity', 'Interest_Coverage',
    'Current_Ratio', 'Quick_Ratio', 'Net_Debt_to_EBITDA', 'Cash_Ratio',
    'Revenue_CAGR_3Y', 'Stock_Return_3Y', 'YoY_Revenue_Growth', 'Asset_Turnover',
    'Inventory_Turnover'
]
target = 'Total_Label_Score'

# 80/20 Split
X = df[features]
y = df[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Train the Champion (Random Forest)
model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# 4. Metrics
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)

print("\n" + "="*40)
print("       CHAMPION MODEL EVALUATION")
print("="*40)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"Log Loss: {log_loss(y_test, y_prob, labels=model.classes_):.4f}")

print("\n--- Detailed Classification Report ---")
print(classification_report(y_test, y_pred, zero_division=0))

# 5. Visualizations
# A. Confusion Matrix
plt.figure(figsize=(12, 8))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='YlGnBu', 
            xticklabels=model.classes_, 
            yticklabels=model.classes_)
plt.title('Confusion Matrix: Predicted vs Actual')
plt.xlabel('Predicted Score')
plt.ylabel('True Score')
plt.savefig('confusion_matrix.png', dpi=300)

# B. Feature Importance
importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
plt.figure(figsize=(10, 6))
importances.plot(kind='bar', color='teal')
plt.title('Feature Importance: Which Ratios Matter Most?')
plt.ylabel('Importance')
plt.tight_layout()
plt.savefig('feature_importance.png', dpi=300)
```

---

### File 4: `market-visualization.py` (75 lines)

```python
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load the data
file_path = os.path.join('data', 'norm-data.xlsx')
df = pd.read_excel(file_path, sheet_name='Train_Normalized')

# 2. Recalculate Ranks & M-Score
print("Calculating market distribution and scores...")
ranked_df = pd.DataFrame(index=df.index)

# Define Pillars (Percentiles)
cols_up = ['Interest_Coverage', 'Current_Ratio', 'ROE', 'ROCE', 
           'Revenue_CAGR_3Y', 'YoY_Revenue_Growth', 'Asset_Turnover', 'Inventory_Turnover']
for col in cols_up:
    ranked_df[col + '_Rank'] = df[col].rank(pct=True) * 100

ranked_df['DE_Rank'] = (1 - df['Debt_to_Equity'].rank(pct=True)) * 100
ranked_df['PE_Rank'] = (1 - df['P_E_Ratio'].rank(pct=True)) * 100
ranked_df['PB_Rank'] = (1 - df['P_B_Ratio'].rank(pct=True)) * 100

# Sub-Scores for Plotting
df['Growth_Score'] = ranked_df[['Revenue_CAGR_3Y_Rank', 'YoY_Revenue_Growth_Rank', 'ROE_Rank', 'ROCE_Rank']].mean(axis=1)
df['Value_Score'] = ranked_df[['PE_Rank', 'PB_Rank']].mean(axis=1)

q_score = ranked_df[['Interest_Coverage_Rank', 'Current_Ratio_Rank', 'DE_Rank']].mean(axis=1)
e_score = ranked_df[['Asset_Turnover_Rank', 'Inventory_Turnover_Rank']].mean(axis=1)

# Final M-Score
df['M_Score'] = (q_score * 0.3) + (df['Growth_Score'] * 0.3) + (df['Value_Score'] * 0.2) + (e_score * 0.2)

# Assign Categories
def get_verdict(score):
    if score >= 70: return "Low Risk (Elite)"
    elif score >= 45: return "Medium Risk (Neutral)"
    else: return "High Risk (Avoid)"

df['Risk_Status'] = df['M_Score'].apply(get_verdict)

# 3. Create the Dashboard (2 Plots)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
palette = {"Low Risk (Elite)": "#2ecc71", "Medium Risk (Neutral)": "#f39c12", "High Risk (Avoid)": "#e74c3c"}

# --- PLOT 1: SCATTER PLOT ---
sns.scatterplot(data=df, x='Value_Score', y='Growth_Score', hue='Risk_Status', 
                palette=palette, alpha=0.6, s=100, ax=ax1, edgecolor='w')

# Annotate some Top stocks
top_5 = df.sort_values(by='M_Score', ascending=False).head(5)
for i, row in top_5.iterrows():
    ax1.text(row['Value_Score']+1, row['Growth_Score']+1, row['Company_Name'], fontsize=9, weight='bold')

ax1.set_title('Market Map: Growth vs Valuation', fontsize=16)
ax1.set_xlabel('Value Score (Higher = "Cheaper")')
ax1.set_ylabel('Growth Score (Higher = Better Performance)')
ax1.grid(True, linestyle='--', alpha=0.5)

# --- PLOT 2: PERCENTAGE PIE CHART ---
counts = df['Risk_Status'].value_counts()
# Ensure the colors match the legend
pie_colors = [palette[category] for category in counts.index]

ax2.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=140, 
        colors=pie_colors, explode=(0.05, 0, 0), shadow=True)
ax2.set_title('Market Risk Distribution (%)', fontsize=16)

# 4. Save and Show
plt.tight_layout()
plt.savefig('market_dashboard.png', dpi=300)
print(f"✅ Success! Dashboard saved as 'market_dashboard.png'")
print("\nMarket Summary:")
print(counts)
# plt.show()
```

---

### File 5: `stock-screener.py` (51 lines)

```python
import pandas as pd
import os

# 1. Load the ranked data created by your scoring engine
# Note: Ensure you have run your scoring-engine.py first to create this file
file_path = os.path.join('data', 'final_stock_rankings.xlsx')

if not os.path.exists(file_path):
    print(f"Error: {file_path} not found. Please run your scoring-engine.py script first.")
    exit()

df = pd.read_excel(file_path)

def run_screener():
    print("\n" + "="*50)
    print("       🚀 AI STOCK SCREENER: FILTER BY SCORE")
    print("="*50)
    
    try:
        min_score = float(input("Enter minimum M-Score (e.g., 70): "))
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    # 2. Filter companies
    results = df[df['M_Score'] >= min_score].copy()
    
    # 3. Sort results by score (highest first)
    results = results.sort_values(by='M_Score', ascending=False)

    # 4. Display Results
    if not results.empty:
        print(f"\n✅ Found {len(results)} companies with a score of {min_score} or higher:")
        print("-" * 75)
        print(f"{'Company Name':<45} | {'Sector':<20} | {'Score':<10}")
        print("-" * 75)
        
        for _, row in results.iterrows():
            print(f"{row['Company_Name'][:43]:<45} | {row['Sector'][:18]:<20} | {row['M_Score']:<10.2f}")
            
        print("-" * 75)
        print(f"End of list. Total: {len(results)} companies.")
    else:
        print(f"\n❌ No companies found with a score of {min_score} or higher.")

if __name__ == "__main__":
    while True:
        run_screener()
        cont = input("\nRun another search? (y/n): ").lower()
        if cont != 'y':
            break
```

---

### File 6: `model-preprocess-code.py`

```python
# ⚠️ THIS FILE IS COMPLETELY EMPTY — placeholder never implemented
```

---

### File 7: `.gitignore`

```gitignore
# Ignore the documentation
README.md

# Ignore Python's temporary cache files
__pycache__/
*.py[cod]
*$py.class

# Ignore ML model metadata (if using CatBoost)
catboost_info/

# Ignore OS-specific system files
.DS_Store
Thumbs.db

# Ignore your Excel data if you don't want it on the cloud (optional)
# data/*.xlsx
```

---

### File 8: `requirements.txt`

```
# ⚠️ COMPLETELY EMPTY — never populated
```

**Actual dependencies (from imports)**:
```
pandas>=1.5.0
openpyxl>=3.0.0
matplotlib>=3.6.0
seaborn>=0.12.0
scikit-learn>=1.2.0
xgboost>=1.7.0
catboost>=1.1.0
```
