import logging

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger()


url = "./data/Sample - Superstore.csv"

COLUMN_MAP = {
    "Row ID": "row_id",
    "Order ID": "order_id",
    "Order Date": "order_date",
    "Ship Date": "ship_date",
    "Ship Mode": "ship_mode",
    "Customer ID": "customer_id",
    "Customer Name": "customer_name",
    "Segment": "segment",
    "Country": "country",
    "City": "city",
    "State": "state",
    "Postal Code": "postal_code",
    "Region": "region",
    "Product ID": "product_id",
    "Category": "category",
    "Sub-Category": "sub_category",
    "Product Name": "product_name",
    "Sales": "sales",
    "Quantity": "quantity",
    "Discount": "discount",
    "Profit": "profit",
}

def extract(file):
    """Load data with pandas and return it as a dataframe
    """
    df = pd.read_csv(file, encoding="latin-1")
    return df



def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize the raw Superstore data.

    Steps:
        1. Rename columns to snake_case.
        2. Convert date columns to datetime.
        3. Drop duplicate rows (ignoring row_id).
        4. Drop rows missing critical values.

    Args:
        df: Raw DataFrame returned by extract().

    Returns:
        Cleaned DataFrame with a reset index.
    """
    # Rename columns (returns a new DataFrame, input is not modified)
    df = df.rename(columns=COLUMN_MAP)

    # Parse dates
    df["order_date"] = pd.to_datetime(df["order_date"], format="%m/%d/%Y")
    df["ship_date"] = pd.to_datetime(df["ship_date"], format="%m/%d/%Y")

    # Remove duplicates (row_id is unique, so exclude it from the check)
    dedup_cols = [c for c in df.columns if c != "row_id"]
    df = df.drop_duplicates(subset=dedup_cols)

    # Drop rows missing critical fields only
    df = df.dropna(subset=["order_id", "order_date", "sales"])

    return df.reset_index(drop=True)



if __name__ == "__main__":
    logger.info("Extracting data...")
    df = extract(url)
    logger.info(f"Number of rows: {df.shape[0]}")
    # logger.info(f"2 first rows: \n {df.head(2).T}")
    # logger.info(f"Columns: \n {df.columns.to_list()}")
    # logger.info(f"Types: \n {df.dtypes}")
    # logger.info(f"Null values: {df.isna().sum()}")
    logger.info("Transforming data...")
    df = transform(df)
    logger.info(f"Number of rows after transformation step: {df.shape[0]}")
    




