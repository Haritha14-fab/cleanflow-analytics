
from pathlib import Path
import pandas as pd

# Project folders
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Dataset is inside data/sample/
RAW_FILE = (
    PROJECT_DIR
    / "data"
    / "sample"
    / "cleanflow_sample_sales.csv"
)

CLEANED_DIR = PROJECT_DIR / "data" / "cleaned"
CLEANED_FILE = CLEANED_DIR / "cleaned_sales.csv"

REPORTS_DIR = PROJECT_DIR / "reports"
EXCEPTIONS_FILE = REPORTS_DIR / "data_quality_exceptions.csv"


def clean_sales_data(file_path: Path) -> pd.DataFrame:
    """Clean sales data and save invalid records separately."""

    # Check dataset exists
    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    # Load dataset
    df = pd.read_csv(file_path)
    original_rows = len(df)

    if df.empty:
        raise ValueError("The dataset is empty.")

    # Check required columns
    required_columns = [
        "Order_ID",
        "Order_Date",
        "Customer",
        "Region",
        "Category",
        "Product",
        "Quantity",
        "Unit_Price",
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Remove exact duplicate rows
    duplicate_count = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    # Clean text columns
    text_columns = [
        "Order_ID",
        "Customer",
        "Region",
        "Category",
        "Product",
    ]

    for column in text_columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

    # Convert blank strings into missing values
    for column in text_columns:
        df[column] = df[column].replace("", pd.NA)

    # Standardize text
    df["Region"] = df["Region"].str.title()
    df["Category"] = df["Category"].str.title()

    # Convert dates and numeric columns
    df["Order_Date"] = pd.to_datetime(
        df["Order_Date"],
        errors="coerce",
        dayfirst=True,
    )

    df["Quantity"] = pd.to_numeric(
        df["Quantity"],
        errors="coerce",
    )

    df["Unit_Price"] = pd.to_numeric(
        df["Unit_Price"],
        errors="coerce",
    )

    # Identify invalid records for manual review
    invalid_rows = (
        df["Order_ID"].isna()
        | df["Customer"].isna()
        | df["Region"].isna()
        | df["Category"].isna()
        | df["Product"].isna()
        | df["Order_Date"].isna()
        | df["Quantity"].isna()
        | df["Quantity"].le(0)
        | df["Unit_Price"].isna()
        | df["Unit_Price"].lt(0)
    )

    # Preserve exceptions instead of silently deleting them
    exceptions = df.loc[invalid_rows].copy()

    # Keep only valid records for the cleaned dataset
    cleaned = df.loc[~invalid_rows].copy()

    # Calculate sales
    cleaned["Sales"] = (
        cleaned["Quantity"] * cleaned["Unit_Price"]
    )

    # Create output folders
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Save output files
    cleaned.to_csv(CLEANED_FILE, index=False)
    exceptions.to_csv(EXCEPTIONS_FILE, index=False)

    # Display summary
    print("\n===== CLEANFLOW DATA CLEANING =====")
    print(f"Original rows: {original_rows}")
    print(f"Duplicate rows removed: {duplicate_count}")
    print(f"Rows after duplicate removal: {len(df)}")
    print(f"Valid cleaned rows: {len(cleaned)}")
    print(f"Exception rows for review: {len(exceptions)}")
    print(f"\nCleaned dataset: {CLEANED_FILE}")
    print(f"Exceptions report: {EXCEPTIONS_FILE}")
    print("\nData cleaning completed successfully!")

    return cleaned


if __name__ == "__main__":
    clean_sales_data(RAW_FILE)
