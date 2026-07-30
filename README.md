# GlobalCart E-Commerce Data Lake & Analytics Pipeline

An end-to-end Data Engineering pipeline that ingests raw e-commerce data from AWS S3, processes and transforms it into a Star Schema using Python (Pandas), loads it into a local MySQL Data Warehouse, and visualizes executive KPIs using Power BI.

---

## Architecture Overview

1. **Storage (Data Lake):** AWS S3 hosting raw transaction, user, and product datasets.
2. **ETL Pipeline:** Python script orchestrated to extract, clean, and map entities into fact/dimension models.
3. **Data Warehouse:** Local MySQL database storing `fact_orders`, `dim_customer`, and `dim_product`.
4. **Analytics & BI:** Interactive Power BI dashboard with dynamic cross-filtering and key DAX measures.

---

## Data Model (Star Schema)

- **`fact_orders`**: Central transactions table storing revenue, item counts, and order timestamps.
- **`dim_customer`**: Customer metadata (email, gender, signup date, location).
- **`dim_product`**: Product catalog details (brand, category, price, ratings).

---

## Power BI Dashboard Preview

![Dashboard Preview](docs/dashboard_preview.png)

### Key Metrics Tracked
- **Total Revenue** (`SUM(total_amount)`)
- **Total Orders** (`COUNTROWS(fact_orders)`)
- **Average Order Value (AOV)** (`Total Revenue / Total Orders`)

---

## How to Run the Project Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/globalcart-analytics.git](https://github.com/your-username/globalcart-analytics.git)
   cd globalcart-analytics

   Set up virtual environment & install dependencies:

Bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
Configure Environment Variables:
Create a .env file in the root directory:

Code snippet
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=globalcart_dw
Execute Pipeline:

Bash
python main.py
Open Dashboard:
Open GlobalCart_Executive_Dashboard.pbix in Power BI Desktop and click Refresh.