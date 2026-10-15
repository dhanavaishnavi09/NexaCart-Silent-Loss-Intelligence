import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

file_path = "Data/NexaCart.xlsx"

#excel_file = pd.ExcelFile(file_path)
#print(excel_file.sheet_names) by this we get to know all the shee names in the excel
customers = pd.read_excel(file_path, sheet_name="customers_raw_cleaned")
products = pd.read_excel(file_path, sheet_name="products_raw_cleaned")
orders = pd.read_excel(file_path, sheet_name="orders_raw_cleaned")
order_items = pd.read_excel(file_path, sheet_name="Order_items_raw")
payments = pd.read_excel(file_path, sheet_name="payments_raw")
delivery = pd.read_excel(file_path, sheet_name="delivery_raw")
refunds = pd.read_excel(file_path, sheet_name="refunds_raw")
inventory = pd.read_excel(file_path, sheet_name="Inventory_events_cleaned")
customer_events = pd.read_excel(file_path, sheet_name="customer_event_raw")

print("Customers:", customers.shape)
print("Products:", products.shape)
print("Orders:", orders.shape)
print("Order Items:", order_items.shape)
print("Payments:", payments.shape)
print("Delivery:", delivery.shape)
print("Refunds:", refunds.shape)
print("Inventory:", inventory.shape)
print("Customer Events:", customer_events.shape)
print("\n--- Missing Values ---")

datasets = {
    "Customers": customers,
    "Products": products,
    "Orders": orders,
    "Order Items": order_items,
    "Payments": payments,
    "Delivery": delivery,
    "Refunds": refunds,
    "Inventory": inventory,
    "Customer Events": customer_events
}

for name, df in datasets.items():
    print(f"\n{name}")
    print(df.isnull().sum())

# Remove Excel audit/helper columns

customers = customers[
    ["Customer_ID", "Signup_Date", "City", "Region",
     "Customer_Segment", "Plan", "Acquisition_Channel"]
]

products = products[
    ["Product_ID", "Product_Name", "Category",
     "Supplier_ID", "Unit_Cost", "Selling_Price", "Reorder_Level"]
]

order_items = order_items[
    ["Order_Item_ID", "Order_ID", "Product_ID", "Quantity",
     "Selling_Price", "Unit_Cost", "Discount_Percent", "Line_Revenue"]
]

payments = payments[
    ["Payment_ID", "Order_ID", "Payment_Method",
     "Payment_Status", "Payment_Amount"]
]

delivery = delivery[
    ["Delivery_ID", "Order_ID", "Delivery_Status",
     "Promised_Date", "Actual_Delivery_Date", "Delivery_Partner"]
]

refunds = refunds[
    ["Refund_ID", "Order_ID", "Refund_Reason",
     "Refund_Amount", "Refund_Date"]
]

inventory = inventory[
    ["Inventory_Event_ID", "Product_ID", "Event_Date",
     "Location", "Opening_Stock", "Units_Sold",
     "Stock_Received", "Closing_Stock",
     "Calculated_Closing_Stock", "Inventory_Anomaly",
     "Closing_Stock_Cleaned"]
]

customer_events = customer_events[
    ["Event_ID", "Customer_ID", "Event_Date",
     "Event_Type", "Platform"]
]
# Update the datasets dictionary with the cleaned DataFrames

datasets = {
    "Customers": customers,
    "Products": products,
    "Orders": orders,
    "Order Items": order_items,
    "Payments": payments,
    "Delivery": delivery,
    "Refunds": refunds,
    "Inventory": inventory,
    "Customer Events": customer_events
}

print("\n--- Cleaned Column Counts ---")

for name, df in datasets.items():
    print(name, df.shape)
print("\n--- Data Types ---")

for name, df in datasets.items():
    print(f"\n{name}")
    print(df.dtypes)

print("\n--- Order Status Distribution ---")

order_status = orders["Order_Status"].value_counts()

print(order_status)
order_status_pct = orders["Order_Status"].value_counts(normalize=True) * 100

print("\n--- Order Status Percentage ---")
print(order_status_pct.round(2))

print("\n--- Order Channel Distribution ---")

print(orders["Order_Channel"].value_counts())

print("\n--- Revenue Analysis ---")

total_revenue = order_items["Line_Revenue"].sum()
total_units = order_items["Quantity"].sum()
total_orders = orders["Order_ID"].nunique()

print("Total Revenue:", round(total_revenue, 2))
print("Total Units Sold:", total_units)
print("Total Orders:", total_orders)

avg_order_value = total_revenue / total_orders

print("Average Order Value:", round(avg_order_value, 2))
print("\n--- Profitability Analysis ---")

order_items["Gross_Profit"] = (
    order_items["Line_Revenue"]
    - (order_items["Unit_Cost"] * order_items["Quantity"])
)

total_cost = (
    order_items["Unit_Cost"] * order_items["Quantity"]
).sum()

total_profit = order_items["Gross_Profit"].sum()

gross_margin = (total_profit / total_revenue) * 100

print("Total Product Cost:", round(total_cost, 2))
print("Total Gross Profit:", round(total_profit, 2))
print("Gross Margin:", round(gross_margin, 2), "%")

print("\n--- Discount Analysis ---")

order_items["Discount_Amount"] = (
    order_items["Selling_Price"]
    * order_items["Quantity"]
    * order_items["Discount_Percent"] / 100
)

total_discount = order_items["Discount_Amount"].sum()

orders_with_discount = (
    order_items[order_items["Discount_Percent"] > 0]["Order_ID"]
    .nunique()
)

discounted_revenue = (
    order_items[order_items["Discount_Percent"] > 0]["Line_Revenue"]
    .sum()
)

print("Total Discount Given:", round(total_discount, 2))
print("Orders With Discount:", orders_with_discount)
print("Revenue From Discounted Items:", round(discounted_revenue, 2))

print("\n--- Profit Margin by Discount Level ---")

discount_analysis = (
    order_items
    .groupby("Discount_Percent")
    .agg(
        Orders=("Order_ID", "nunique"),
        Revenue=("Line_Revenue", "sum"),
        Units=("Quantity", "sum"),
        Profit=("Gross_Profit", "sum"),
        Discount_Amount=("Discount_Amount", "sum")
    )
    .reset_index()
)

discount_analysis["Margin_%"] = (
    discount_analysis["Profit"]
    / discount_analysis["Revenue"]
    * 100
)

print(discount_analysis.round(2).to_string(index=False))

print("\n--- Discount Validation ---")

order_items["Expected_Revenue_After_Discount"] = (
    order_items["Selling_Price"]
    * order_items["Quantity"]
    * (1 - order_items["Discount_Percent"] / 100)
)

order_items["Revenue_Difference"] = (
    order_items["Line_Revenue"]
    - order_items["Expected_Revenue_After_Discount"]
)

print(
    "Maximum Revenue Difference:",
    round(order_items["Revenue_Difference"].abs().max(), 2)
)

print(
    "Average Revenue Difference:",
    round(order_items["Revenue_Difference"].abs().mean(), 2)
)

print("\n--- Refund Analysis ---")

total_refund = refunds["Refund_Amount"].sum()
refunded_orders = refunds["Order_ID"].nunique()

refund_rate = (refunded_orders / total_orders) * 100

print("Total Refund Amount:", round(total_refund, 2))
print("Refunded Orders:", refunded_orders)
print("Refund Rate:", round(refund_rate, 2), "%")

print("\n--- Refund Reasons ---")

refund_reasons = (
    refunds.groupby("Refund_Reason")
    .agg(
        Refunds=("Refund_ID", "count"),
        Refund_Amount=("Refund_Amount", "sum")
    )
    .sort_values("Refund_Amount", ascending=False)
)

print(refund_reasons.round(2))

print("\n--- Refund KPIs ---")

total_refund = refunds["Refund_Amount"].sum()
refunded_orders = refunds["Order_ID"].nunique()

refund_rate = (refunded_orders / total_orders) * 100

print("Total Refund Amount:", round(total_refund, 2))
print("Refunded Orders:", refunded_orders)
print("Refund Rate:", round(refund_rate, 2), "%")

# ==============================
# DELIVERY DELAY ANALYSIS
# ==============================

print("\n--- Delivery Analysis ---")

# Calculate delivery delay in days
delivery["Delivery_Delay_Days"] = (
    delivery["Actual_Delivery_Date"] -
    delivery["Promised_Date"]
).dt.days

# Delivery status
print("\nDelivery Status:")
print(delivery["Delivery_Status"].value_counts())

# Late deliveries
late_deliveries = delivery[delivery["Delivery_Delay_Days"] > 0]

print("\nLate Deliveries:", len(late_deliveries))
print(
    "Late Delivery Rate:",
    round(len(late_deliveries) / len(delivery) * 100, 2),
    "%"
)

# Average delay
print(
    "Average Delay:",
    round(late_deliveries["Delivery_Delay_Days"].mean(), 2),
    "days"
)

# Maximum delay
print(
    "Maximum Delay:",
    late_deliveries["Delivery_Delay_Days"].max(),
    "days"
)
# ==============================
# DELIVERY DELAY vs REFUNDS
# ==============================

print("\n--- Delivery Delay vs Refunds ---")

# Mark each order as late or not
delivery["Late_Flag"] = delivery["Delivery_Delay_Days"] > 0

# Add refund information to delivery data
delivery_refund = delivery.merge(
    refunds[["Order_ID", "Refund_Amount"]],
    on="Order_ID",
    how="left"
)

# Orders with refunds
delivery_refund["Has_Refund"] = delivery_refund["Refund_Amount"].notna()

# Compare refund rate
delay_refund_analysis = (
    delivery_refund.groupby("Late_Flag")
    .agg(
        Orders=("Order_ID", "count"),
        Refunded_Orders=("Has_Refund", "sum"),
        Refund_Amount=("Refund_Amount", "sum")
    )
)

delay_refund_analysis["Refund_Rate_%"] = (
    delay_refund_analysis["Refunded_Orders"]
    / delay_refund_analysis["Orders"] * 100
)

print(delay_refund_analysis.round(2))

# ==============================
# PAYMENT ANALYSIS
# ==============================

print("\n--- Payment Analysis ---")

# Payment status distribution
payment_status = payments["Payment_Status"].value_counts()

print("\nPayment Status:")
print(payment_status)

# Payment status percentage
payment_status_pct = (
    payments["Payment_Status"]
    .value_counts(normalize=True) * 100
)

print("\nPayment Status %:")
print(payment_status_pct.round(2))

# Payment method distribution
print("\nPayment Methods:")
print(payments["Payment_Method"].value_counts())

# Total failed payments
failed_payments = payments[
    payments["Payment_Status"].str.lower().str.contains("fail")
]

print("\nFailed Payments:", len(failed_payments))

print(
    "Payment Failure Rate:",
    round(len(failed_payments) / len(payments) * 100, 2),
    "%"
)

print(
    "Failed Payment Amount:",
    round(failed_payments["Payment_Amount"].sum(), 2)
)

# ==============================
# CUSTOMER EVENT ANALYSIS
# ==============================

print("\n--- Customer Event Analysis ---")

# Event distribution
event_counts = (
    customer_events["Event_Type"]
    .value_counts()
)

print("\nEvent Counts:")
print(event_counts)

# Event percentages
event_pct = (
    customer_events["Event_Type"]
    .value_counts(normalize=True) * 100
)

print("\nEvent Percentages:")
print(event_pct.round(2))

# Platform distribution
print("\nPlatform Distribution:")
print(customer_events["Platform"].value_counts())

# Important friction events
friction_events = [
    "Payment Failed",
    "Stockout Encountered",
    "Delivery Delay Viewed"
]

print("\nCustomer Friction Events:")

friction = customer_events[
    customer_events["Event_Type"].isin(friction_events)
]["Event_Type"].value_counts()

print(friction)

# ==============================
# STOCKOUT ANALYSIS
# ==============================

print("\n--- Stockout Analysis ---")

# Identify stockout events
stockout_events = customer_events[
    customer_events["Event_Type"] == "Stockout Encountered"
]

print("Total Stockout Events:", len(stockout_events))

# Stockout events by platform
print("\nStockout Events by Platform:")
print(
    stockout_events["Platform"]
    .value_counts()
)

# Stockout events by region/customer
# Connect stockout events with customer information
stockout_customer = stockout_events.merge(
    customers[["Customer_ID", "Region", "Customer_Segment"]],
    on="Customer_ID",
    how="left"
)

print("\nStockout Events by Region:")
print(
    stockout_customer["Region"]
    .value_counts()
)

print("\nStockout Events by Customer Segment:")
print(
    stockout_customer["Customer_Segment"]
    .value_counts()
)

# ==============================
# STOCKOUT vs PURCHASE ATTEMPT
# ==============================

print("\n--- Stockout vs Purchase Attempt ---")

# Customers who encountered stockout
stockout_customers = set(
    customer_events.loc[
        customer_events["Event_Type"] == "Stockout Encountered",
        "Customer_ID"
    ]
)

# Customers who attempted purchase
purchase_attempt_customers = set(
    customer_events.loc[
        customer_events["Event_Type"] == "Purchase Attempt",
        "Customer_ID"
    ]
)

# Overlap
both = stockout_customers.intersection(purchase_attempt_customers)

print("Customers with Stockout:", len(stockout_customers))
print("Customers with Purchase Attempt:", len(purchase_attempt_customers))
print("Customers with Both:", len(both))

# Percentage of stockout customers who also attempted purchase
if len(stockout_customers) > 0:
    print(
        "Stockout Customers Who Also Attempted Purchase:",
        round(len(both) / len(stockout_customers) * 100, 2),
        "%"
    )

# ==============================
# HIDDEN LOSS CHAIN
# ==============================

print("\n--- Hidden Loss Chain ---")

# Create one row per customer
customer_signals = customer_events.groupby("Customer_ID").agg(
    Stockout_Encountered=(
        "Event_Type",
        lambda x: (x == "Stockout Encountered").any()
    ),
    Purchase_Attempted=(
        "Event_Type",
        lambda x: (x == "Purchase Attempt").any()
    ),
    Payment_Failed=(
        "Event_Type",
        lambda x: (x == "Payment Failed").any()
    ),
    Delivery_Delay_Viewed=(
        "Event_Type",
        lambda x: (x == "Delivery Delay Viewed").any()
    )
).reset_index()

# Create the loss-chain groups
customer_signals["Loss_Chain"] = np.select(
    [
        customer_signals["Stockout_Encountered"] &
        customer_signals["Purchase_Attempted"] &
        customer_signals["Payment_Failed"],

        customer_signals["Stockout_Encountered"] &
        customer_signals["Purchase_Attempted"],

        customer_signals["Purchase_Attempted"] &
        customer_signals["Payment_Failed"],

        customer_signals["Delivery_Delay_Viewed"]
    ],
    [
        "Stockout + Purchase Attempt + Payment Failure",
        "Stockout + Purchase Attempt",
        "Purchase Attempt + Payment Failure",
        "Delivery Delay Viewed"
    ],
    default="Other"
)

print("\nLoss Chain Distribution:")
print(
    customer_signals["Loss_Chain"]
    .value_counts()
)

# ==============================
# LOSS CHAIN SCORE
# ==============================

print("\n--- Loss Chain Score ---")

customer_signals["Loss_Chain_Score"] = (
    customer_signals["Stockout_Encountered"].astype(int)
    + customer_signals["Purchase_Attempted"].astype(int)
    + customer_signals["Payment_Failed"].astype(int)
    + customer_signals["Delivery_Delay_Viewed"].astype(int)
)

print("\nLoss Chain Score Distribution:")
print(
    customer_signals["Loss_Chain_Score"]
    .value_counts()
    .sort_index()
)

print("\nAverage Loss Chain Score:",
      round(customer_signals["Loss_Chain_Score"].mean(), 2))
# ==============================
# MONTHLY BUSINESS TRENDS
# ==============================

print("\n--- Monthly Business Trends ---")

# Create month column
orders["Month"] = orders["Order_Date"].dt.to_period("M")

# Monthly order count
monthly_orders = (
    orders.groupby("Month")
    .agg(
        Orders=("Order_ID", "nunique"),
        Customers=("Customer_ID", "nunique")
    )
    .reset_index()
)

print("\nMonthly Orders:")
print(monthly_orders)

# Monthly revenue
order_items["Month"] = (
    order_items["Order_ID"]
    .map(
        orders.set_index("Order_ID")["Month"]
    )
)

monthly_revenue = (
    order_items.groupby("Month")
    .agg(
        Revenue=("Line_Revenue", "sum"),
        Units=("Quantity", "sum")
    )
    .reset_index()
)

print("\nMonthly Revenue:")
print(monthly_revenue)

# ==============================
# INVENTORY ANOMALY ANALYSIS
# ==============================

print("\n--- Inventory Anomaly Analysis ---")

# Product-level inventory summary
inventory_summary = (
    inventory.groupby("Product_ID")
    .agg(
        Total_Units_Sold=("Units_Sold", "sum"),
        Total_Stock_Received=("Stock_Received", "sum"),
        Avg_Closing_Stock=("Closing_Stock_Cleaned", "mean"),
        Inventory_Events=("Inventory_Event_ID", "count")
    )
    .reset_index()
)

# Products with negative calculated stock
negative_stock_products = (
    inventory[inventory["Inventory_Anomaly"] == "Negative Stock"]
    .groupby("Product_ID")
    .size()
    .reset_index(name="Negative_Stock_Events")
    .sort_values("Negative_Stock_Events", ascending=False)
)

print("\nTop Products with Negative Stock Events:")
print(negative_stock_products.head(10))

# Products with high sales but low average closing stock
inventory_summary["Stock_Risk"] = (
    inventory_summary["Total_Units_Sold"] /
    (inventory_summary["Avg_Closing_Stock"] + 1)
)

high_risk_products = inventory_summary.sort_values(
    "Stock_Risk",
    ascending=False
)

print("\nTop Inventory Risk Products:")
print(
    high_risk_products[
        [
            "Product_ID",
            "Total_Units_Sold",
            "Avg_Closing_Stock",
            "Stock_Risk"
        ]
    ].head(10)
)