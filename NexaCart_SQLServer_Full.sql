/* NexaCart - SQL Server full setup + analysis */
IF DB_ID('NexaCart') IS NULL CREATE DATABASE NexaCart;
GO
USE NexaCart;
GO

IF OBJECT_ID('dbo.customer_events','U') IS NOT NULL DROP TABLE dbo.customer_events;
IF OBJECT_ID('dbo.inventory_events','U') IS NOT NULL DROP TABLE dbo.inventory_events;
IF OBJECT_ID('dbo.refunds','U') IS NOT NULL DROP TABLE dbo.refunds;
IF OBJECT_ID('dbo.delivery','U') IS NOT NULL DROP TABLE dbo.delivery;
IF OBJECT_ID('dbo.payments','U') IS NOT NULL DROP TABLE dbo.payments;
IF OBJECT_ID('dbo.order_items','U') IS NOT NULL DROP TABLE dbo.order_items;
IF OBJECT_ID('dbo.orders','U') IS NOT NULL DROP TABLE dbo.orders;
IF OBJECT_ID('dbo.products','U') IS NOT NULL DROP TABLE dbo.products;
IF OBJECT_ID('dbo.customers','U') IS NOT NULL DROP TABLE dbo.customers;
GO

CREATE TABLE dbo.customers(Customer_ID varchar(10) PRIMARY KEY,Signup_Date date,City varchar(100),Region varchar(20),Customer_Segment varchar(30),[Plan] varchar(30),Acquisition_Channel varchar(50));
CREATE TABLE dbo.products(Product_ID varchar(10) PRIMARY KEY,Product_Name varchar(100),Category varchar(50),Supplier_ID varchar(20),Unit_Cost decimal(12,2),Selling_Price decimal(12,2),Reorder_Level int);
CREATE TABLE dbo.orders(Order_ID varchar(15) PRIMARY KEY,Customer_ID varchar(10),Order_Date date,Order_Status varchar(30),Order_Channel varchar(30),FOREIGN KEY(Customer_ID) REFERENCES dbo.customers(Customer_ID));
CREATE TABLE dbo.order_items(Order_Item_ID varchar(15) PRIMARY KEY,Order_ID varchar(15),Product_ID varchar(10),Quantity int,Selling_Price decimal(12,2),Unit_Cost decimal(12,2),Discount_Percent decimal(5,2),Line_Revenue decimal(14,2),FOREIGN KEY(Order_ID) REFERENCES dbo.orders(Order_ID),FOREIGN KEY(Product_ID) REFERENCES dbo.products(Product_ID));
CREATE TABLE dbo.payments(Payment_ID varchar(15) PRIMARY KEY,Order_ID varchar(15),Payment_Method varchar(30),Payment_Status varchar(30),Payment_Amount decimal(14,2),FOREIGN KEY(Order_ID) REFERENCES dbo.orders(Order_ID));
CREATE TABLE dbo.delivery(Delivery_ID varchar(15) PRIMARY KEY,Order_ID varchar(15),Delivery_Status varchar(30),Promised_Date date,Actual_Delivery_Date date,Delivery_Partner varchar(50),FOREIGN KEY(Order_ID) REFERENCES dbo.orders(Order_ID));
CREATE TABLE dbo.refunds(Refund_ID varchar(15) PRIMARY KEY,Order_ID varchar(15),Refund_Reason varchar(100),Refund_Amount decimal(14,2),Refund_Date date,FOREIGN KEY(Order_ID) REFERENCES dbo.orders(Order_ID));
CREATE TABLE dbo.inventory_events(Inventory_Event_ID varchar(15) PRIMARY KEY,Product_ID varchar(10),Event_Date date,Location varchar(100),Opening_Stock int,Units_Sold int,Stock_Received int,Closing_Stock int,FOREIGN KEY(Product_ID) REFERENCES dbo.products(Product_ID));
CREATE TABLE dbo.customer_events(Event_Id varchar(15) PRIMARY KEY,Customer_ID varchar(10),Event_Date date,Event_Type varchar(50),Platform varchar(30),FOREIGN KEY(Customer_ID) REFERENCES dbo.customers(Customer_ID));
GO

/* FAST IMPORT: extract this package to D:\NexaCartSQL first. */
BULK INSERT dbo.customers FROM 'D:\NexaCartSQL\customers.csv' WITH(FORMAT='CSV',FIRSTROW=2,FIELDQUOTE='"',TABLOCK,CODEPAGE='65001');
BULK INSERT dbo.products FROM 'D:\NexaCartSQL\products.csv' WITH(FORMAT='CSV',FIRSTROW=2,FIELDQUOTE='"',TABLOCK,CODEPAGE='65001');
BULK INSERT dbo.orders FROM 'D:\NexaCartSQL\orders.csv' WITH(FORMAT='CSV',FIRSTROW=2,FIELDQUOTE='"',TABLOCK,CODEPAGE='65001');
BULK INSERT dbo.order_items FROM 'D:\NexaCartSQL\order_items.csv' WITH(FORMAT='CSV',FIRSTROW=2,FIELDQUOTE='"',TABLOCK,CODEPAGE='65001');
BULK INSERT dbo.payments FROM 'D:\NexaCartSQL\payments.csv' WITH(FORMAT='CSV',FIRSTROW=2,FIELDQUOTE='"',TABLOCK,CODEPAGE='65001');
BULK INSERT dbo.delivery FROM 'D:\NexaCartSQL\delivery.csv' WITH(FORMAT='CSV',FIRSTROW=2,FIELDQUOTE='"',TABLOCK,CODEPAGE='65001');
BULK INSERT dbo.refunds FROM 'D:\NexaCartSQL\refunds.csv' WITH(FORMAT='CSV',FIRSTROW=2,FIELDQUOTE='"',TABLOCK,CODEPAGE='65001');
BULK INSERT dbo.inventory_events FROM 'D:\NexaCartSQL\inventory_events.csv' WITH(FORMAT='CSV',FIRSTROW=2,FIELDQUOTE='"',TABLOCK,CODEPAGE='65001');
BULK INSERT dbo.customer_events FROM 'D:\NexaCartSQL\customer_events.csv' WITH(FORMAT='CSV',FIRSTROW=2,FIELDQUOTE='"',TABLOCK,CODEPAGE='65001');
GO

/* VALIDATION */
SELECT 'customers' Table_Name,COUNT(*) Row_Count FROM dbo.customers UNION ALL SELECT 'products',COUNT(*) FROM dbo.products UNION ALL SELECT 'orders',COUNT(*) FROM dbo.orders UNION ALL SELECT 'order_items',COUNT(*) FROM dbo.order_items UNION ALL SELECT 'payments',COUNT(*) FROM dbo.payments UNION ALL SELECT 'delivery',COUNT(*) FROM dbo.delivery UNION ALL SELECT 'refunds',COUNT(*) FROM dbo.refunds UNION ALL SELECT 'inventory_events',COUNT(*) FROM dbo.inventory_events UNION ALL SELECT 'customer_events',COUNT(*) FROM dbo.customer_events;
GO

/* ANALYSIS 1: revenue by region */
SELECT c.Region,COUNT(DISTINCT o.Order_ID) Total_Orders,SUM(oi.Line_Revenue) Total_Revenue FROM dbo.customers c JOIN dbo.orders o ON c.Customer_ID=o.Customer_ID JOIN dbo.order_items oi ON o.Order_ID=oi.Order_ID GROUP BY c.Region ORDER BY Total_Revenue DESC;
/* 2: category */
SELECT p.Category,COUNT(DISTINCT oi.Order_ID) Total_Orders,SUM(oi.Quantity) Units_Sold,SUM(oi.Line_Revenue) Total_Revenue FROM dbo.products p JOIN dbo.order_items oi ON p.Product_ID=oi.Product_ID GROUP BY p.Category ORDER BY Total_Revenue DESC;
/* 3: top products */
SELECT TOP 10 p.Product_ID,p.Product_Name,p.Category,SUM(oi.Quantity) Units_Sold,SUM(oi.Line_Revenue) Revenue FROM dbo.products p JOIN dbo.order_items oi ON p.Product_ID=oi.Product_ID GROUP BY p.Product_ID,p.Product_Name,p.Category ORDER BY Revenue DESC;
/* 4: product profit */
SELECT TOP 10 p.Product_ID,p.Product_Name,p.Category,SUM(oi.Quantity) Units_Sold,SUM(oi.Line_Revenue) Revenue,SUM(oi.Quantity*oi.Unit_Cost) Product_Cost,SUM(oi.Line_Revenue)-SUM(oi.Quantity*oi.Unit_Cost) Gross_Profit FROM dbo.products p JOIN dbo.order_items oi ON p.Product_ID=oi.Product_ID GROUP BY p.Product_ID,p.Product_Name,p.Category ORDER BY Gross_Profit DESC;
/* 5: category profit */
SELECT p.Category,SUM(oi.Line_Revenue) Revenue,SUM(oi.Quantity*oi.Unit_Cost) Product_Cost,SUM(oi.Line_Revenue)-SUM(oi.Quantity*oi.Unit_Cost) Gross_Profit,ROUND((SUM(oi.Line_Revenue)-SUM(oi.Quantity*oi.Unit_Cost))*100.0/NULLIF(SUM(oi.Line_Revenue),0),2) Gross_Margin_Percent FROM dbo.products p JOIN dbo.order_items oi ON p.Product_ID=oi.Product_ID GROUP BY p.Category ORDER BY Gross_Profit DESC;
/* 6: discount impact */
SELECT oi.Discount_Percent,COUNT(DISTINCT oi.Order_ID) Total_Orders,SUM(oi.Line_Revenue) Revenue,SUM(oi.Quantity*oi.Unit_Cost) Product_Cost,SUM(oi.Line_Revenue)-SUM(oi.Quantity*oi.Unit_Cost) Gross_Profit,ROUND((SUM(oi.Line_Revenue)-SUM(oi.Quantity*oi.Unit_Cost))*100.0/NULLIF(SUM(oi.Line_Revenue),0),2) Gross_Margin_Percent FROM dbo.order_items oi GROUP BY oi.Discount_Percent ORDER BY oi.Discount_Percent;
/* 7: top customers */
SELECT TOP 10 c.Customer_ID,c.City,c.Region,c.Customer_Segment,COUNT(DISTINCT o.Order_ID) Total_Orders,SUM(oi.Line_Revenue) Total_Revenue FROM dbo.customers c JOIN dbo.orders o ON c.Customer_ID=o.Customer_ID JOIN dbo.order_items oi ON o.Order_ID=oi.Order_ID GROUP BY c.Customer_ID,c.City,c.Region,c.Customer_Segment ORDER BY Total_Revenue DESC;
/* 8: segment */
SELECT c.Customer_Segment,COUNT(DISTINCT c.Customer_ID) Total_Customers,COUNT(DISTINCT o.Order_ID) Total_Orders,SUM(oi.Line_Revenue) Total_Revenue,ROUND(SUM(oi.Line_Revenue)/NULLIF(COUNT(DISTINCT c.Customer_ID),0),2) Revenue_Per_Customer FROM dbo.customers c JOIN dbo.orders o ON c.Customer_ID=o.Customer_ID JOIN dbo.order_items oi ON o.Order_ID=oi.Order_ID GROUP BY c.Customer_Segment ORDER BY Total_Revenue DESC;
/* 9: payment failures */
SELECT p.Payment_Method,COUNT(*) Total_Payments,SUM(CASE WHEN p.Payment_Status='Failed' THEN 1 ELSE 0 END) Failed_Payments,SUM(CASE WHEN p.Payment_Status='Failed' THEN p.Payment_Amount ELSE 0 END) Failed_Amount,ROUND(SUM(CASE WHEN p.Payment_Status='Failed' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) Failure_Rate_Percent FROM dbo.payments p GROUP BY p.Payment_Method ORDER BY Failure_Rate_Percent DESC;
/* 10: refund reasons */
SELECT r.Refund_Reason,COUNT(DISTINCT r.Order_ID) Refunded_Orders,SUM(r.Refund_Amount) Total_Refund_Amount FROM dbo.refunds r GROUP BY r.Refund_Reason ORDER BY Total_Refund_Amount DESC;
/* 11: segment refund/cancel */
SELECT c.Customer_Segment,COUNT(DISTINCT o.Order_ID) Total_Orders,SUM(CASE WHEN o.Order_Status='Refunded' THEN 1 ELSE 0 END) Refunded_Orders,ROUND(SUM(CASE WHEN o.Order_Status='Refunded' THEN 1 ELSE 0 END)*100.0/COUNT(DISTINCT o.Order_ID),2) Refund_Rate_Percent,SUM(CASE WHEN o.Order_Status='Cancelled' THEN 1 ELSE 0 END) Cancelled_Orders,ROUND(SUM(CASE WHEN o.Order_Status='Cancelled' THEN 1 ELSE 0 END)*100.0/COUNT(DISTINCT o.Order_ID),2) Cancellation_Rate_Percent FROM dbo.customers c JOIN dbo.orders o ON c.Customer_ID=o.Customer_ID GROUP BY c.Customer_Segment;
/* 12: region x segment */
SELECT c.Region,c.Customer_Segment,COUNT(DISTINCT c.Customer_ID) Total_Customers,COUNT(DISTINCT o.Order_ID) Total_Orders,SUM(oi.Line_Revenue) Total_Revenue FROM dbo.customers c JOIN dbo.orders o ON c.Customer_ID=o.Customer_ID JOIN dbo.order_items oi ON o.Order_ID=oi.Order_ID GROUP BY c.Region,c.Customer_Segment ORDER BY Total_Revenue DESC;
/* 13: regional friction */
SELECT c.Region,e.Event_Type,COUNT(*) Event_Count FROM dbo.customers c JOIN dbo.customer_events e ON c.Customer_ID=e.Customer_ID WHERE e.Event_Type IN('Stockout Encountered','Payment Failed','Delivery Delay Viewed') GROUP BY c.Region,e.Event_Type ORDER BY c.Region,Event_Count DESC;
/* 14: hidden loss chain */
WITH S AS(SELECT e.Customer_ID,MAX(CASE WHEN e.Event_Type='Stockout Encountered' THEN 1 ELSE 0 END) Stockout,MAX(CASE WHEN e.Event_Type='Purchase Attempt' THEN 1 ELSE 0 END) Purchase_Attempt,MAX(CASE WHEN e.Event_Type='Payment Failed' THEN 1 ELSE 0 END) Payment_Failed,MAX(CASE WHEN e.Event_Type='Delivery Delay Viewed' THEN 1 ELSE 0 END) Delivery_Delay FROM dbo.customer_events e GROUP BY e.Customer_ID), L AS(SELECT CASE WHEN Stockout=1 AND Purchase_Attempt=1 AND Payment_Failed=1 THEN 'Stockout + Purchase Attempt + Payment Failure' WHEN Stockout=1 AND Purchase_Attempt=1 THEN 'Stockout + Purchase Attempt' WHEN Delivery_Delay=1 THEN 'Delivery Delay Viewed' WHEN Purchase_Attempt=1 AND Payment_Failed=1 THEN 'Purchase Attempt + Payment Failure' ELSE 'Other' END Loss_Chain FROM S) SELECT Loss_Chain,COUNT(*) Customers FROM L GROUP BY Loss_Chain ORDER BY Customers DESC;
/* 15: loss chain score */
WITH S AS(SELECT e.Customer_ID,MAX(CASE WHEN e.Event_Type='Stockout Encountered' THEN 1 ELSE 0 END) Stockout,MAX(CASE WHEN e.Event_Type='Purchase Attempt' THEN 1 ELSE 0 END) Purchase_Attempt,MAX(CASE WHEN e.Event_Type='Payment Failed' THEN 1 ELSE 0 END) Payment_Failed,MAX(CASE WHEN e.Event_Type='Delivery Delay Viewed' THEN 1 ELSE 0 END) Delivery_Delay FROM dbo.customer_events e GROUP BY e.Customer_ID) SELECT Stockout+Purchase_Attempt+Payment_Failed+Delivery_Delay Loss_Chain_Score,COUNT(*) Customers FROM S GROUP BY Stockout+Purchase_Attempt+Payment_Failed+Delivery_Delay ORDER BY Loss_Chain_Score;
/* 16: monthly */
SELECT YEAR(o.Order_Date) Order_Year,MONTH(o.Order_Date) Order_Month,COUNT(DISTINCT o.Order_ID) Total_Orders,SUM(oi.Line_Revenue) Total_Revenue FROM dbo.orders o JOIN dbo.order_items oi ON o.Order_ID=oi.Order_ID GROUP BY YEAR(o.Order_Date),MONTH(o.Order_Date) ORDER BY Order_Year,Order_Month;
/* 17: inventory anomalies */
SELECT Product_ID,COUNT(*) Negative_Stock_Events FROM dbo.inventory_events WHERE Closing_Stock<0 GROUP BY Product_ID ORDER BY Negative_Stock_Events DESC;
GO

/* POWER BI VIEWS */
CREATE OR ALTER VIEW dbo.vw_Revenue_By_Region AS SELECT c.Region,COUNT(DISTINCT o.Order_ID) Total_Orders,SUM(oi.Line_Revenue) Total_Revenue FROM dbo.customers c JOIN dbo.orders o ON c.Customer_ID=o.Customer_ID JOIN dbo.order_items oi ON o.Order_ID=oi.Order_ID GROUP BY c.Region;
GO
CREATE OR ALTER VIEW dbo.vw_Category_Performance AS SELECT p.Category,COUNT(DISTINCT oi.Order_ID) Total_Orders,SUM(oi.Quantity) Units_Sold,SUM(oi.Line_Revenue) Revenue,SUM(oi.Quantity*oi.Unit_Cost) Product_Cost,SUM(oi.Line_Revenue)-SUM(oi.Quantity*oi.Unit_Cost) Gross_Profit FROM dbo.products p JOIN dbo.order_items oi ON p.Product_ID=oi.Product_ID GROUP BY p.Category;
GO
CREATE OR ALTER VIEW dbo.vw_Product_Profitability AS SELECT p.Product_ID,p.Product_Name,p.Category,SUM(oi.Quantity) Units_Sold,SUM(oi.Line_Revenue) Revenue,SUM(oi.Quantity*oi.Unit_Cost) Product_Cost,SUM(oi.Line_Revenue)-SUM(oi.Quantity*oi.Unit_Cost) Gross_Profit,ROUND((SUM(oi.Line_Revenue)-SUM(oi.Quantity*oi.Unit_Cost))*100.0/NULLIF(SUM(oi.Line_Revenue),0),2) Gross_Margin_Percent FROM dbo.products p JOIN dbo.order_items oi ON p.Product_ID=oi.Product_ID GROUP BY p.Product_ID,p.Product_Name,p.Category;
GO
CREATE OR ALTER VIEW dbo.vw_Payment_Friction AS SELECT Payment_Method,COUNT(*) Total_Payments,SUM(CASE WHEN Payment_Status='Failed' THEN 1 ELSE 0 END) Failed_Payments,SUM(CASE WHEN Payment_Status='Failed' THEN Payment_Amount ELSE 0 END) Failed_Amount,ROUND(SUM(CASE WHEN Payment_Status='Failed' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) Failure_Rate_Percent FROM dbo.payments GROUP BY Payment_Method;
GO
CREATE OR ALTER VIEW dbo.vw_Refund_Analysis AS SELECT Refund_Reason,COUNT(DISTINCT Order_ID) Refunded_Orders,SUM(Refund_Amount) Total_Refund_Amount FROM dbo.refunds GROUP BY Refund_Reason;
GO
CREATE OR ALTER VIEW dbo.vw_Monthly_Performance AS SELECT YEAR(o.Order_Date) Order_Year,MONTH(o.Order_Date) Order_Month,COUNT(DISTINCT o.Order_ID) Total_Orders,SUM(oi.Line_Revenue) Total_Revenue FROM dbo.orders o JOIN dbo.order_items oi ON o.Order_ID=oi.Order_ID GROUP BY YEAR(o.Order_Date),MONTH(o.Order_Date);
GO
CREATE OR ALTER VIEW dbo.vw_Customer_Friction AS SELECT c.Region,e.Event_Type,COUNT(*) Event_Count FROM dbo.customers c JOIN dbo.customer_events e ON c.Customer_ID=e.Customer_ID WHERE e.Event_Type IN('Stockout Encountered','Payment Failed','Delivery Delay Viewed') GROUP BY c.Region,e.Event_Type;
GO
PRINT 'NexaCart SQL Server setup completed.';
