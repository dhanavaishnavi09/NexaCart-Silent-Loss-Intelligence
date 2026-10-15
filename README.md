# NexaCart — Silent Loss Intelligence Engine

A data analytics portfolio project exploring revenue performance, profitability, payment failures, refunds, delivery friction, inventory signals, and customer behaviour for a fictional omnichannel commerce business.

## Project Overview

NexaCart is a fictional e-commerce business used to demonstrate how data analytics can turn operational data into business insights. The project brings together order, product, payment, delivery, refund, inventory, and customer-event data to highlight where performance may be under pressure and where further investigation could be valuable.

**Core question:** Where do operational friction and commercial performance signals suggest that NexaCart should investigate potential revenue or customer-experience risks?

## Tools

- **SQL Server:** data storage, querying, joins, aggregations, and analytical checks
- **Power BI:** interactive dashboards, KPI reporting, comparisons, and drill-through analysis
- **Excel:** supporting data review and analysis
- **Python:** include only the scripts and analysis actually used in this project

## Repository Structure

```text
NexaCart_final_project/
├── README.md
├── powerbi/
│   └── NexaCart.pbix
├── excel/
│   └── Supporting workbook (if suitable for sharing)
├── sql/
│   └── SQL analysis scripts
├── python/
│   └── Python scripts or notebooks (if used)
├── screenshots/
│   └── Dashboard screenshots
└── docs/
    ├── KPI definitions
    ├── Data dictionary
    └── Key findings
```

The folder names above describe the intended organisation. Remove sections or folders that do not contain actual project files.

## Dashboards

The Power BI report is organised around these analysis areas:

1. **Executive Control Room** — revenue, orders, average order value, gross profit, gross margin, and high-level alerts.
2. **Silent Loss** — customer-event signals such as stockout encounters, payment failures, and delivery-delay views.
3. **Customers** — customer-segment contribution, order activity, revenue trends, and refund-rate comparisons.
4. **Products** — product and category revenue contribution and product-level comparisons.
5. **Regions** — regional revenue, orders, gross profit, and margin comparisons.
6. **Regional Deep Dive** — regional customer-friction breakdown with drill-through filtering.

Add screenshots to the `screenshots/` folder and update this section if your final report uses different page names.

## Selected Findings

The current analysis of the project dataset indicates:

- **Revenue:** ₹415.41 million (approximately ₹41.54 crore)
- **Orders:** 50,000
- **Average order value:** approximately ₹8,308.20
- **Gross profit:** approximately ₹56.69 million
- **Gross margin:** approximately 13.65%
- **Discounted orders:** approximately 81.56% of orders
- **Payment records marked failed:** 3,085
- **Customer events recorded as stockout encounters:** 14,018
- **Customer events recorded as payment failures:** 9,856
- **Customer events recorded as delivery-delay views:** 9,982

These are dataset-level results and may change when filters are applied. Payment records and customer-event records are different sources and should not be treated as interchangeable.

### Discount and margin

In the current dataset, gross margin decreases as the recorded discount level rises. The margin is negative in the 25% and 30% discount groups. This is an association in the analysed data, not proof that discounts alone caused the margin outcome.

### Customer-friction signals

Stockout encounters, payment-failure events, and delivery-delay views are used as friction signals to identify areas for further investigation. They do **not** by themselves prove that a sale was lost or that a customer churned.

## KPI Definitions

- **Total Revenue:** sum of line revenue in the order-items data.
- **Total Orders:** distinct order IDs.
- **Average Order Value (AOV):** total revenue divided by distinct orders.
- **Gross Profit:** line revenue minus quantity multiplied by unit cost, summed across order items.
- **Gross Margin:** gross profit divided by total revenue.
- **Refund Amount:** sum of recorded refund amounts.
- **Refund Rate:** orders marked with a refunded status divided by distinct orders. This is different from counting refund records.
- **Customer Friction Events:** counts of selected customer events, including stockout encounters, payment failures, and delivery-delay views.

See `docs/` for a more detailed data dictionary and KPI definitions when those files have been prepared.

## Methodology

1. Load the project data into SQL Server.
2. Review data structure, key fields, and table relationships.
3. Query and aggregate the data to investigate commercial and operational patterns.
4. Build Power BI measures and visuals for KPI monitoring and comparisons.
5. Use dashboard filters and drill-through to explore regional and segment-level results.
6. Validate totals and clearly document limitations before drawing conclusions.

## Limitations and Responsible Interpretation

- NexaCart is a **fictional portfolio dataset**, not a real company dataset.
- The analysis is descriptive; it does not establish causality.
- Customer-friction events are investigation signals, not confirmed lost revenue.
- Payment status counts and customer-event counts come from different tables.
- Delivery status labels and date-derived lateness flags may represent different definitions; they should not be combined without validating the business rules.
- Inventory fields should not be presented as verified current stock unless the underlying inventory logic has been validated.
- Any estimated risk score is a project-defined prioritisation aid, not proof of customer loss.
- Results depend on the dataset and current model logic; validate calculations and relationships before using them for decisions.

## How to Explore the Project

1. Open `NexaCart.pbix` in Power BI Desktop.
2. If the report requests a data source, configure the connection for your own environment. Do not publish database credentials.
3. Review the Executive Control Room first, then explore the Silent Loss, Customers, Products, and Regions pages.
4. Use the regional drill-through page where available to inspect a selected region.
5. Review the SQL scripts and supporting documentation to understand the calculations.

## Future Improvements

- Add a documented data dictionary and model relationship diagram.
- Add repeatable SQL validation checks for key totals and relationships.
- Add clear definitions for operational alerts and investigate their thresholds.
- Add refresh and data-quality checks.
- Improve the analysis with validated time-based trends and clearly documented business rules.

## Author

**Yele Dhana Vaishnavi**

Data analytics portfolio project using SQL Server, Power BI, Excel, and Python where applicable.
