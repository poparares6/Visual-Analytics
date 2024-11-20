import pandas as pd
import glob
import os
import matplotlib.pyplot as plt

file_paths = glob.glob(os.path.join('Data', 'sales_*.csv'))
sales_dfs = [pd.read_csv(file) for file in file_paths]
sales_df = pd.concat(sales_dfs, ignore_index=True)

sales_df['Transaction Date'] = pd.to_datetime(sales_df['Transaction Date'], errors='coerce')

columns_to_drop = [
    'Base Plan ID', 'Offer ID', 'Order Number', 'Order Charged Date',
    'Order Charged Timestamp', 'Financial Status', 'Device Model',
    'Product ID', 'SKU ID', 'Currency of Sale', 'Item Price',
    'Taxes Collected', 'Charged Amount', 'City of Buyer',
    'State of Buyer', 'Postal Code of Buyer', 'Country of Buyer', 'Tax Type'
]

sales_df = sales_df.drop(columns=columns_to_drop)
# Drop rows where the 'Description' column is empty or NaN
sales_df = sales_df.dropna(subset=['Description'])

# Reset the index to ensure it's clean after row deletion
sales_df.reset_index(drop=True, inplace=True)

#create Month column from Transaction Date
sales_df['Month'] = sales_df['Transaction Date'].dt.to_period('M')
print("Month column created (first few values):")
print(sales_df['Month'].head())

monthly_sales = sales_df.groupby('Month').agg(
    transaction_count=('Transaction Date', 'count'),
    total_amount=('Amount (Merchant Currency)', 'sum')
).reset_index()


fig, ax1 = plt.subplots(figsize=(12, 6))


ax1.bar(monthly_sales['Month'].astype(str), monthly_sales['transaction_count'], color='skyblue', label='Transaction Count', alpha=0.7)
ax1.set_xlabel('Month', fontsize=12)
ax1.set_ylabel('Transaction Count', color='blue', fontsize=12)
ax1.tick_params(axis='y', labelcolor='blue')


ax2 = ax1.twinx()
ax2.plot(monthly_sales['Month'].astype(str), monthly_sales['total_amount'], color='orange', marker='o', label='Total Amount (EUR)')
ax2.set_ylabel('Total Amount (EUR)', color='orange', fontsize=12)
ax2.tick_params(axis='y', labelcolor='orange')


plt.title('Monthly Sales Volume', fontsize=14)
fig.tight_layout()
plt.xticks(rotation=45)
plt.show()

sales_df['Transaction Date'] = pd.to_datetime(sales_df['Transaction Date'])


sales_df['Month'] = sales_df['Transaction Date'].dt.to_period('M')


sku_sales = sales_df.groupby(['Sku Id', 'Month']).agg(
    transaction_count=('Transaction Date', 'count'),
    total_amount=('Amount (Merchant Currency)', 'sum')
).reset_index()

sku_ids = sku_sales['Sku Id'].unique()

plt.figure(figsize=(12, 6))
for sku in sku_ids:
    sku_data = sku_sales[sku_sales['Sku Id'] == sku]
    plt.plot(sku_data['Month'].astype(str), sku_data['transaction_count'], marker='o', label=f'{sku} - Transaction Count')
plt.xlabel('Month')
plt.ylabel('Transaction Count')
plt.title('Monthly Transaction Count by SKU Id')
plt.legend()
plt.xticks(rotation=45)
plt.show()


plt.figure(figsize=(12, 6))
for sku in sku_ids:
    sku_data = sku_sales[sku_sales['Sku Id'] == sku]
    plt.plot(sku_data['Month'].astype(str), sku_data['total_amount'], marker='o', linestyle='--', label=f'{sku} - Total Amount (EUR)')
plt.xlabel('Month')
plt.ylabel('Total Amount (EUR)')
plt.title('Monthly Total Amount by SKU Id')
plt.legend()
plt.xticks(rotation=45)
plt.show()

#prepare data for stacked bar chart
sku_transaction_counts = sales_df.groupby(['Month', 'Sku Id'])['Transaction Date'].count().unstack()

#plot stacked bar chart
sku_transaction_counts.plot(kind='bar', stacked=True, figsize=(12, 6), colormap='Paired')
plt.title('Monthly Transaction Count by SKU Id')
plt.xlabel('Month')
plt.ylabel('Transaction Count')
plt.xticks(rotation=45)
plt.legend(title='SKU Id', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

#prepare data for grouped bar chart
sku_transaction_counts.plot(kind='bar', figsize=(12, 6), colormap='Set2')
plt.title('Monthly Transaction Count by SKU Id')
plt.xlabel('Month')
plt.ylabel('Transaction Count')
plt.xticks(rotation=45)
plt.legend(title='SKU Id', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

#prepare data for stacked area chart
sku_revenue = sales_df.groupby(['Month', 'Sku Id'])['Amount (Merchant Currency)'].sum().unstack()

#plot stacked area chart
sku_revenue.plot(kind='area', figsize=(12, 6), colormap='coolwarm', alpha=0.8)
plt.title('Monthly Total Amount by SKU Id')
plt.xlabel('Month')
plt.ylabel('Total Amount (EUR)')
plt.xticks(rotation=45)
plt.legend(title='SKU Id', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

#prepare data for horizontal bar chart
top_skus = sales_df.groupby('Sku Id')['Amount (Merchant Currency)'].sum().sort_values(ascending=False)

#plot horizontal bar chart
top_skus.plot(kind='barh', figsize=(10, 6), color='orange', alpha=0.8)
plt.title('Total Amount by SKU Id')
plt.xlabel('Total Amount (EUR)')
plt.ylabel('SKU Id')
plt.tight_layout()
plt.show()
