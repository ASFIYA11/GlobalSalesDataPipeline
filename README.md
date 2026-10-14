# GlobalCart --- Global Sales Data Pipeline

An end-to-end e-commerce data pipeline that demonstrates how raw sales
data can be extracted from Amazon S3, cleaned and transformed with
Python and Pandas, and loaded into MySQL for downstream analytics and
Power BI reporting.

**Repository:** https://github.com/ASFIYA11/GlobalSalesDataPipeline

## Overview

Businesses often collect order, customer, and product data in separate
files. Before this data can be used for reporting, it needs to be
cleaned, standardized, combined, and stored in a consistent structure.

GlobalCart demonstrates this workflow using an Extract, Transform, Load
(ETL) pipeline:

1.  **Extract** --- read CSV objects from an Amazon S3 bucket into
    Pandas DataFrames.
2.  **Transform** --- standardize selected text fields, process order
    data, remove cancelled orders according to the implemented rule,
    join order items with orders, and remove duplicate rows.
3.  **Load** --- write processed datasets to local CSV files, attempt to
    upload processed files to S3, and load DataFrames into MySQL through
    SQLAlchemy.
4.  **Analyse** --- make structured sales data available for SQL
    analysis and Power BI reporting.

> **Scope note:** This README describes the current code structure and
> intended workflow. Successful execution, production readiness,
> data-quality percentages, and business results should only be claimed
> after testing the pipeline with the required AWS and database
> configuration.

## Architecture

``` text
CSV objects in Amazon S3
          |
          v
   src/extract.py
   Read data with Boto3
          |
          v
  src/transform.py
  Clean and combine data
          |
          v
    src/load.py
  Local CSV + S3 upload
  + MySQL via SQLAlchemy
          |
          v
 SQL analysis / Power BI
```

## Technology Stack

-   **Python** --- pipeline implementation
-   **Pandas** --- tabular data processing and transformation
-   **Boto3** --- Amazon S3 access
-   **SQLAlchemy** --- database connection and table loading
-   **MySQL** --- relational storage for processed data
-   **Amazon S3** --- object storage for source and processed files
-   **Power BI** --- downstream reporting and visualization

## Repository Structure

The main pipeline files are organized by responsibility:

``` text
GlobalSalesDataPipeline/
├── main.py             # Orchestrates extraction, transformation, and loading
├── src/
│   ├── extract.py      # Reads CSV data from S3
│   ├── transform.py    # Cleans and combines datasets
│   └── load.py         # Writes outputs and loads MySQL tables
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

If your repository contains additional files, dashboards, or
configuration modules, update this tree to match the current contents.

## Prerequisites

Before running the pipeline, prepare:

-   Python installed on your machine
-   Access to an Amazon S3 bucket containing the expected CSV datasets
-   AWS credentials with the required S3 permissions
-   A running MySQL instance and a database account with the necessary
    permissions
-   The dependencies listed in `requirements.txt`

## Setup

### 1. Clone the repository

``` bash
git clone https://github.com/ASFIYA11/GlobalSalesDataPipeline.git
cd GlobalSalesDataPipeline
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

``` powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

``` bat
python -m venv .venv
.venv\Scripts\activate.bat
```

**macOS / Linux:**

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration

The code requires AWS/S3 configuration and a database connection string.
In particular, the loader reads `DATABASE_URL`, and extraction requires
`S3_BUCKET_NAME`.

Set the variables in your shell or in a local `.env` file **only if the
application is configured to load that file**. Do not commit credentials
to GitHub.

Example placeholders:

``` text
S3_BUCKET_NAME=your-s3-bucket-name
DATABASE_URL=mysql+<your-sqlalchemy-driver>://<username>:<password>@<host>:3306/<database>
```

Configure AWS credentials using an appropriate AWS credential provider,
such as an AWS CLI profile, environment variables, or an execution role.
Grant only the S3 permissions required by the pipeline.

**Important:** Check the code and `requirements.txt` for the exact
region, S3 prefix, SQLAlchemy driver, and any other configuration names
used by your version. The README and implementation should use the same
names. URL-encode special characters in database passwords when required
by SQLAlchemy.

## Running the Pipeline

From the repository root, run:

``` bash
python main.py
```

The orchestrator calls the extraction, transformation, and loading
stages. The pipeline needs valid AWS access, the expected input objects,
a reachable MySQL database, and correctly configured environment
variables.

If the command fails, check the error message and verify:

1.  AWS credentials and S3 permissions.
2.  Bucket name, region, prefix, and expected CSV object names.
3.  Required CSV columns and data types.
4.  MySQL host, port, database, credentials, and SQLAlchemy driver.
5.  Installed package versions and environment-variable names.

## Data Model

The project documentation describes these analytical tables:

-   `fact_orders` --- order-related facts used for analysis
-   `dim_customer` --- customer attributes
-   `dim_product` --- product attributes

A fact-and-dimension layout is commonly used for analytics. Before
relying on this model, verify the actual table schemas, keys,
relationships, and grain in the current code and database.

## Data Transformations

The transformation module includes operations such as:

-   Trimming whitespace from selected customer text fields
-   Standardizing product-category values
-   Filtering orders marked as cancelled
-   Joining order-item data with order data
-   Removing duplicate rows

The exact effect depends on the source data and business rules. In
particular, confirm the meaning of amount and revenue columns before
aggregating after a join: joining an order-level total to multiple item
rows can repeat that total and inflate revenue.

## Data Quality and Validation

A successful run does not, by itself, prove that the resulting data is
correct. Recommended checks include:

-   Compare source and destination row counts while accounting for
    documented filters.
-   Check required columns and data types.
-   Count nulls in required fields.
-   Check duplicate business keys.
-   Validate that fact-table foreign keys map to valid dimension
    records.
-   Reconcile order counts and revenue totals against independently
    calculated source values.
-   Run the pipeline more than once and check whether repeated execution
    causes unintended duplicates or inconsistent output.
-   Compare MySQL query results with Power BI measures using identical
    filters and date ranges.

Do not report an accuracy percentage unless the metric and calculation
are clearly defined and the results have been verified.

## Security Notes

-   Never commit AWS access keys, database passwords, or `.env` files.
-   Use environment variables or an appropriate secret manager for
    credentials.
-   Use least-privilege IAM permissions and restricted database
    accounts.
-   Avoid logging credentials or sensitive customer data.
-   Keep `.env`, virtual environments, caches, and generated sensitive
    data out of version control.

## Known Implementation Considerations

Review these areas before using the pipeline with important data:

-   **Configuration consistency:** ensure the README and code agree on
    environment-variable names. The loader expects `DATABASE_URL`;
    document any additional variables read by the extraction code.
-   **S3 pagination:** if listing many objects, use a Boto3 paginator so
    the pipeline does not stop at the first page of results.
-   **Revenue calculations:** verify the row grain and aggregation logic
    after joining orders and order items.
-   **Loading strategy:** the current loader uses table replacement
    (`if_exists="replace"`). This is a full-refresh-style operation, not
    an incremental upsert, and should be handled carefully.
-   **Failure handling:** ensure failed S3 uploads or database writes
    are surfaced clearly and do not leave the pipeline appearing fully
    successful.

These are implementation considerations to validate, not claims that
every issue will occur in every run.

## Future Improvements

Possible next steps include:

-   Add automated unit and integration tests.
-   Add explicit schema and data-quality checks.
-   Add structured logging and clear failure reporting.
-   Make loading idempotent and support incremental loads where needed.
-   Add S3 pagination and retry handling.
-   Add a reproducible Power BI report with documented measures.
-   Add a sample configuration file that contains placeholders only.
-   Document verified sample outputs and test results.

## Interview Summary

GlobalCart demonstrates the main stages of an ETL workflow: extracting
CSV data from S3 with Boto3, transforming data with Pandas, and loading
structured datasets into MySQL through SQLAlchemy. The processed data
can then support SQL analysis and Power BI reporting.

The key engineering concerns are data quality, correct aggregation,
configuration management, reliable loading, and validation of the final
results.

## Author

**Asfiya Anjum**\
GitHub: https://github.com/ASFIYA11
