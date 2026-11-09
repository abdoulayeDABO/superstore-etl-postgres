import logging

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger()


url = "./data/Sample - Superstore.csv"

def extract(file):
    df = pd.read_csv(file, encoding="latin-1")
    return df


if __name__ == "__main__":
    logger.info("Extracting data")
    df = extract(url)
    logger.info(f"Number of rows: {df.shape[0]}")




