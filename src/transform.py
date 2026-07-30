# src/transform.py
import logging
import pandas as pd

def clean_and_transform(datasets: dict[str, pd.DataFrame]):
    """
    Cleans individual datasets from the Kaggle schema and builds Star Schema tables:
    - dim_customer (from users)
    - dim_product (from products)
    - fact_orders (from orders & order_items)
    """
    logging.info("Starting Data Transformation & Quality Checks...")
    
    # Extract individual dataframes safely
    users_df = datasets.get("users", pd.DataFrame()).copy()
    products_df = datasets.get("products", pd.DataFrame()).copy()
    orders_df = datasets.get("orders", pd.DataFrame()).copy()
    order_items_df = datasets.get("order_items", pd.DataFrame()).copy()

    # --- 1. Clean & Build dim_customer ---
    logging.info("Building dim_customer...")
    if not users_df.empty:
        # Standardize text columns if they exist
        for col in ["first_name", "last_name", "email", "country"]:
            if col in users_df.columns:
                users_df[col] = users_df[col].astype(str).str.strip()
        
        dim_customer = users_df.drop_duplicates().reset_index(drop=True)
    else:
        dim_customer = pd.DataFrame()

    # --- 2. Clean & Build dim_product ---
    logging.info("Building dim_product...")
    if not products_df.empty:
        if "category" in products_df.columns:
            products_df["category"] = products_df["category"].astype(str).str.strip().str.title()
        dim_product = products_df.drop_duplicates().reset_index(drop=True)
    else:
        dim_product = pd.DataFrame()

    # --- 3. Clean & Build fact_orders ---
    logging.info("Building fact_orders...")
    if not orders_df.empty:
        # Filter invalid or canceled orders if status column exists
        if "status" in orders_df.columns:
            orders_df = orders_df[orders_df["status"].astype(str).str.lower() != "cancelled"]

        # Merge order items with orders if order_items exists
        if not order_items_df.empty and "order_id" in order_items_df.columns and "order_id" in orders_df.columns:
            fact_orders = order_items_df.merge(orders_df, on="order_id", how="inner")
        else:
            fact_orders = orders_df.copy()
            
        fact_orders = fact_orders.drop_duplicates().reset_index(drop=True)
    else:
        fact_orders = pd.DataFrame()

    logging.info("Transformation Successful! Star Schema DataFrames generated.")
    return dim_customer, dim_product, fact_orders