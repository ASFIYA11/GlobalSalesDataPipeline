# src/load.py
import os
import io
import logging
import pandas as pd
import boto3
from sqlalchemy import create_engine, text

def save_to_local_processed(df: pd.DataFrame, filename: str):
    """
    Saves a DataFrame locally inside data/processed/
    """
    output_dir = os.path.join("data", "processed")
    os.makedirs(output_dir, exist_ok=True)
    
    file_path = os.path.join(output_dir, f"{filename}.csv")
    df.to_csv(file_path, index=False)
    logging.info(f"Saved local processed file: {file_path}")

def save_to_s3_processed(df: pd.DataFrame, filename: str):
    """
    Saves a DataFrame back to AWS S3 under processed/ directory
    """
    bucket = os.getenv("S3_BUCKET_NAME")
    if not bucket:
        logging.warning("S3_BUCKET_NAME not found in .env. Skipping S3 processed upload.")
        return

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION", "us-east-1")
    )
    
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    s3_key = f"processed/{filename}.csv"
    
    s3_client.put_object(Bucket=bucket, Key=s3_key, Body=csv_buffer.getvalue())
    logging.info(f"Uploaded to S3: s3://{bucket}/{s3_key}")

def load_to_mysql(dim_customer: pd.DataFrame, dim_product: pd.DataFrame, fact_orders: pd.DataFrame):
    """
    1. Exports clean Star Schema CSVs to local data/processed/ folder.
    2. Uploads processed CSV backups to AWS S3 processed/ folder.
    3. Auto-creates MySQL database if missing and writes tables.
    """
    # Step A: Export Processed Files (Local + Cloud)
    logging.info("Saving transformed Star Schema datasets to 'data/processed/'...")
    tables = {
        "dim_customer": dim_customer,
        "dim_product": dim_product,
        "fact_orders": fact_orders
    }

    for name, df in tables.items():
        if not df.empty:
            save_to_local_processed(df, name)
            save_to_s3_processed(df, name)

    # Step B: Load into MySQL Data Warehouse
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL is not set in your .env file!")

    db_name = db_url.split("/")[-1].split("?")[0]
    base_url = db_url.rsplit("/", 1)[0]

    logging.info(f"Ensuring database '{db_name}' exists in MySQL...")
    server_engine = create_engine(base_url)
    with server_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name};"))
        conn.commit()

    logging.info(f"Connecting to MySQL Data Warehouse ({db_name})...")
    dw_engine = create_engine(db_url)

    with dw_engine.begin() as conn:
        if not dim_customer.empty:
            logging.info("Writing dim_customer table to MySQL...")
            dim_customer.to_sql("dim_customer", con=conn, if_exists="replace", index=False)

        if not dim_product.empty:
            logging.info("Writing dim_product table to MySQL...")
            dim_product.to_sql("dim_product", con=conn, if_exists="replace", index=False)

        if not fact_orders.empty:
            logging.info("Writing fact_orders table to MySQL...")
            fact_orders.to_sql("fact_orders", con=conn, if_exists="replace", index=False)

    logging.info("Data successfully loaded into MySQL Data Warehouse!")