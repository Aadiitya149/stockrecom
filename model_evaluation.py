import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
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

# 800/200 Split
X_train, y_train = df[features].iloc[:800], df[target].iloc[:800]
X_test, y_test = df[features].iloc[800:1000], df[target].iloc[800:1000]

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
plt.show()

# B. Feature Importance
importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
plt.figure(figsize=(10, 6))
importances.plot(kind='bar', color='teal')
plt.title('Feature Importance: Which Ratios Matter Most?')
plt.ylabel('Importance')
plt.tight_layout()
plt.show()