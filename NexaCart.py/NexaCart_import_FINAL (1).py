import csv
import os
import pyodbc

SERVER = r"LAPTOP-BD7BPLL2\SQLEXPRESS"
DATABASE = "NexaCart"
DATA_DIR = r"D:\NexaCartSQL"

drivers = pyodbc.drivers()
if "ODBC Driver 18 for SQL Server" in drivers:
    DRIVER = "ODBC Driver 18 for SQL Server"
elif "ODBC Driver 17 for SQL Server" in drivers:
    DRIVER = "ODBC Driver 17 for SQL Server"
else:
    raise RuntimeError("ODBC Driver 17/18 for SQL Server was not found.")

conn_str = (
    f"DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};"
    "Trusted_Connection=yes;TrustServerCertificate=yes;"
)

TABLES = {
    "customers": {
        "file":"customers.csv",
        "columns":[("Customer_ID","VARCHAR(30)"),("Signup_Date","DATE"),("City","VARCHAR(100)"),
                   ("Region","VARCHAR(30)"),("Customer_Segment","VARCHAR(30)"),("Plan","VARCHAR(30)"),
                   ("Acquisition_Channel","VARCHAR(50)")],
        "key":"Customer_ID"},
    "products": {
        "file":"products.csv",
        "columns":[("Product_ID","VARCHAR(30)"),("Product_Name","VARCHAR(150)"),("Category","VARCHAR(50)"),
                   ("Supplier_ID","VARCHAR(30)"),("Unit_Cost","DECIMAL(18,2)"),("Selling_Price","DECIMAL(18,2)"),
                   ("Reorder_Level","INT")],
        "key":"Product_ID"},
    "orders": {
        "file":"orders.csv",
        "columns":[("Order_ID","VARCHAR(30)"),("Customer_ID","VARCHAR(30)"),("Order_Date","DATE"),
                   ("Order_Status","VARCHAR(30)"),("Order_Channel","VARCHAR(30)")],
        "key":"Order_ID"},
    "order_items": {
        "file":"order_items.csv",
        "columns":[("Order_Item_ID","VARCHAR(30)"),("Order_ID","VARCHAR(30)"),("Product_ID","VARCHAR(30)"),
                   ("Quantity","INT"),("Selling_Price","DECIMAL(18,2)"),("Unit_Cost","DECIMAL(18,2)"),
                   ("Discount_Percent","DECIMAL(8,2)"),("Line_Revenue","DECIMAL(18,2)")],
        "key":"Order_Item_ID"},
    "payments": {
        "file":"payments.csv",
        "columns":[("Payment_ID","VARCHAR(30)"),("Order_ID","VARCHAR(30)"),("Payment_Method","VARCHAR(30)"),
                   ("Payment_Status","VARCHAR(30)"),("Payment_Amount","DECIMAL(18,2)")],
        "key":"Payment_ID"},
    "delivery": {
        "file":"delivery.csv",
        "columns":[("Delivery_ID","VARCHAR(30)"),("Order_ID","VARCHAR(30)"),("Delivery_Status","VARCHAR(30)"),
                   ("Promised_Date","DATE"),("Actual_Delivery_Date","DATE"),("Delivery_Partner","VARCHAR(100)")],
        "key":"Delivery_ID"},
    "refunds": {
        "file":"refunds.csv",
        "columns":[("Refund_ID","VARCHAR(30)"),("Order_ID","VARCHAR(30)"),("Refund_Reason","VARCHAR(100)"),
                   ("Refund_Amount","DECIMAL(18,2)"),("Refund_Date","DATE")],
        "key":"Refund_ID"},
    "inventory_events": {
        "file":"inventory_events.csv",
        "columns":[("Inventory_Event_ID","VARCHAR(30)"),("Product_ID","VARCHAR(30)"),("Event_Date","DATE"),
                   ("Location","VARCHAR(100)"),("Opening_Stock","INT"),("Units_Sold","INT"),
                   ("Stock_Received","INT"),("Closing_Stock","DECIMAL(18,2)")],
        "key":"Inventory_Event_ID"},
    "customer_events": {
        "file":"customer_events.csv",
        "columns":[("Event_Id","VARCHAR(30)"),("Customer_ID","VARCHAR(30)"),("Event_Date","DATE"),
                   ("Event_Type","VARCHAR(50)"),("Platform","VARCHAR(30)")],
        "key":"Event_Id"}
}

LOAD_ORDER = ["customers","products","orders","order_items","payments","delivery",
              "refunds","inventory_events","customer_events"]

def cv(value, sql_type):
    if value is None or value.strip() == "":
        return None
    if sql_type == "INT":
        return int(float(value))
    if sql_type.startswith("DECIMAL"):
        return float(value)
    return value.strip()

conn = pyodbc.connect(conn_str, autocommit=False)
cur = conn.cursor()
# Fast executemany is intentionally disabled because some NexaCart text columns
# have longer values later in the batch; disabling it avoids pyodbc buffer truncation.
cur.fast_executemany = False

# Remove views created by the previous script.
for view in ["vw_Revenue_By_Region","vw_Category_Performance","vw_Product_Profitability",
             "vw_Payment_Friction","vw_Refund_Analysis","vw_Monthly_Performance","vw_Customer_Friction"]:
    cur.execute(f"IF OBJECT_ID('dbo.{view}','V') IS NOT NULL DROP VIEW dbo.{view};")

# Remove old tables, then recreate them cleanly.
for table in reversed(LOAD_ORDER):
    cur.execute(f"IF OBJECT_ID('dbo.{table}','U') IS NOT NULL DROP TABLE dbo.{table};")

for table in LOAD_ORDER:
    info = TABLES[table]
    defs = ", ".join(f"[{n}] {t}" for n,t in info["columns"])
    cur.execute(f"CREATE TABLE dbo.{table} ({defs}, CONSTRAINT PK_{table} PRIMARY KEY ([{info['key']}]));")

conn.commit()
print("Tables recreated successfully.")

BATCH = 5000

for table in LOAD_ORDER:
    info = TABLES[table]
    path = os.path.join(DATA_DIR, info["file"])
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    names = [n for n,_ in info["columns"]]
    types = [t for _,t in info["columns"]]
    cols = ",".join(f"[{n}]" for n in names)
    marks = ",".join("?" for _ in names)
    sql = f"INSERT INTO dbo.{table} ({cols}) VALUES ({marks})"

    total = 0
    batch = []
    print(f"Loading {table}...")

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Normalize CSV header spelling/case (for example Event_ID vs Event_Id).
            normalized_row = {
                str(k).strip().lower(): v
                for k, v in row.items()
                if k is not None
            }
            batch.append([
                cv(normalized_row[n.lower()], t)
                for n, t in zip(names, types)
            ])
            if len(batch) == BATCH:
                cur.executemany(sql, batch)
                total += len(batch)
                batch.clear()
        if batch:
            cur.executemany(sql, batch)
            total += len(batch)

    conn.commit()
    print(f"  {total:,} rows loaded.")

print("\nFINAL ROW COUNTS")
print("-"*35)
for table in LOAD_ORDER:
    cur.execute(f"SELECT COUNT(*) FROM dbo.{table}")
    print(f"{table:20s} {cur.fetchone()[0]:>10,}")

cur.close()
conn.close()
print("\nNexaCart import completed successfully.")

