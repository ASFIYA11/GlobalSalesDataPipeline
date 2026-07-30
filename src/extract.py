# src/extract.py
import os
import io
import logging
import pandas as pd
import boto3

def extract_raw_data() -> dict[str, pd.DataFrame]:
    """
    Connects to AWS S3, loops through CSV files in S3_RAW_KEY,
    and returns a dictionary mapping filename (without .csv) to its DataFrame.
    """
    logging.info("Starting multi-file extraction from AWS S3...")
    
    bucket = os.getenv("S3_BUCKET_NAME")
    prefix = os.getenv("S3_RAW_KEY", "raw/ecommerce_dataset/")
    
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION", "us-east-1")
    )
    
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    
    if "Contents" not in response:
        raise FileNotFoundError(f"No files found in s3://{bucket}/{prefix}")

    datasets = {}
    
    for obj in response["Contents"]:
        file_key = obj["Key"]
        
        if file_key.endswith("/") or not file_key.endswith(".csv"):
            continue
            
        file_name = file_key.split("/")[-1].replace(".csv", "")
        logging.info(f"Downloading and parsing dataset: '{file_name}' from s3://{bucket}/{file_key}")
        
        file_obj = s3_client.get_object(Bucket=bucket, Key=file_key)
        df = pd.read_csv(io.BytesIO(file_obj["Body"].read()))
        datasets[file_name] = df

    if not datasets:
        raise ValueError(f"No valid CSV files were loaded from S3 path: s3://{bucket}/{prefix}")

    logging.info(f"Successfully loaded {len(datasets)} datasets: {list(datasets.keys())}")
    return datasets