# main.py
import logging
from dotenv import load_dotenv
from src.extract import extract_raw_data
from src.transform import clean_and_transform
from src.load import load_to_mysql

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def run_pipeline():
    logging.info("=== STARTING E-COMMERCE ETL PIPELINE ===")
    
    # Load environment variables from .env
    load_dotenv()

    try:
        # Step 1: Extract from S3
        raw_df = extract_raw_data()

        # Step 2: Clean & Transform
        dim_customer, dim_product, fact_orders = clean_and_transform(raw_df)

        # Step 3: Load into MySQL
        load_to_mysql(dim_customer, dim_product, fact_orders)

        logging.info("=== PIPELINE EXECUTED SUCCESSFULLY ===")

    except Exception as e:
        logging.error(f"Pipeline Failed! Reason: {str(e)}", exc_info=True)

if __name__ == "__main__":
    run_pipeline()