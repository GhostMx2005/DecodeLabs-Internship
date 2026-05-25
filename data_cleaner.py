import pandas as pd
import os

# Paths
input_file = "/mnt/user-data/uploads/Dataset_for_Data_Analytics.xlsx"
output_file = "/mnt/user-data/outputs/Dataset_Cleaned.xlsx"
os.makedirs(os.path.dirname(output_file), exist_ok=True)

print("Loading data...")
df = pd.read_excel(input_file)
print(f"Original shape: {df.shape}")

# 1. Check duplicates
duplicates = df.duplicated().sum()
if duplicates:
    print(f"Removing {duplicates} duplicate rows")
    df = df.drop_duplicates()
else:
    print("No duplicate rows found")

# 2. Missing values – fill CouponCode only
missing_before = df.isnull().sum().sum()
if df['CouponCode'].isnull().any():
    n = df['CouponCode'].isnull().sum()
    df['CouponCode'] = df['CouponCode'].fillna("No Coupon")
    print(f"Filled {n} missing CouponCode with 'No Coupon'")
print(f"Total missing after fill: {df.isnull().sum().sum()}")

# 3. Fix date format – to YYYY-MM-DD string
df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")

# 4. Round floats and verify TotalPrice = Quantity * UnitPrice
for col in ['UnitPrice', 'TotalPrice']:
    before = df[col].copy()
    df[col] = df[col].round(2)
    changed = (before != df[col]).sum()
    if changed:
        print(f"Rounded {changed} values in {col}")

df['expected'] = (df['Quantity'] * df['UnitPrice']).round(2)
mismatch = df[abs(df['expected'] - df['TotalPrice']) > 0.01]
if not mismatch.empty:
    print(f"Fixing {len(mismatch)} rows where TotalPrice doesn't match Quantity*UnitPrice")
    df.loc[mismatch.index, 'TotalPrice'] = df.loc[mismatch.index, 'expected']
df = df.drop(columns=['expected'])

# 5. Strip whitespace from text columns
text_cols = ['Product', 'PaymentMethod', 'OrderStatus', 'ReferralSource', 
             'CouponCode', 'OrderID', 'CustomerID', 'ShippingAddress', 'TrackingNumber']
for col in text_cols:
    if col in df.columns:
        df[col] = df[col].str.strip()
print("Stripped whitespace from text columns")

# 6. Enforce correct data types
df['Quantity'] = df['Quantity'].astype(int)
df['ItemsInCart'] = df['ItemsInCart'].astype(int)
df['UnitPrice'] = df['UnitPrice'].astype(float)
df['TotalPrice'] = df['TotalPrice'].astype(float)

# 7. Basic sanity checks
invalid_qty = (df['Quantity'] < 1).sum()
invalid_price = (df['UnitPrice'] <= 0).sum()
invalid_total = (df['TotalPrice'] <= 0).sum()
invalid_cart = (df['ItemsInCart'] < 1).sum()

if invalid_qty:
    print(f"Warning: {invalid_qty} rows with Quantity < 1")
if invalid_price:
    print(f"Warning: {invalid_price} rows with UnitPrice <= 0")
if invalid_total:
    print(f"Warning: {invalid_total} rows with TotalPrice <= 0")
if invalid_cart:
    print(f"Warning: {invalid_cart} rows with ItemsInCart < 1")

# Final summary
print("\nCleaning done!")
print(f"Final shape: {df.shape}")
print(f"Rows removed: {duplicates}")
print(f"Remaining nulls: {df.isnull().sum().sum()}")

# Save
df.to_excel(output_file, index=False)
print(f"Saved to {output_file}")