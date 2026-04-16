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