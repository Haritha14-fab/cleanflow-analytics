from pathlib import Path
import pandas as pd

# Project folders
PROJECT_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = PROJECT_DIR / "data" / "raw" / "cleanflow_sample_sales.csv"
CLEANED_DIR = PROJECT_DIR / "data" / "cleaned"
CLEANED_FILE = CLEANED_DIR / "cleaned_sales.csv"

CLEANED_DIR.mkdir(parents = True, exist_ok = True)


def clean_sales_data(file_path: Path) -> pd.DataFrame:
    # Load raw data
df = pd.read_csv(file_path)

    # Remove exact duplicate rows
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
   df[column] = df[column].astype("string").str.strip()

    # Standardize text formatting
df["Region"] = df["Region"].str.title()
df["Category"] = df["Category"].str.title()

    # Convert dates and numeric columns
df["Order_Date"] = pd.to_datetime(
   df["Order_Date"],
   errors = "coerce",
   dayfirst = True,
)

df["Quantity"] = pd.to_numeric(
   df["Quantity"], errors = "coerce"
)

df["Unit_Price"] = pd.to_numeric(
   df["Unit_Price"], errors = "coerce"
)

    # Mark invalid records
invalid_rows = (
   df["Order_ID"].isna()
   | df["Order_ID"].eq("")
   | df["Customer"].isna()
   | df["Customer"].eq("")
   | df["Order_Date"].isna()
   | df["Quantity"].isna()
   | df["Quantity"].le(0)
   | df["Unit_Price"].isna()
   | df["Unit_Price"].lt(0)
)

    # Keep invalid records in a separate report for review
    exceptions = df.loc[invalid_rows].copy()

    # Keep valid records in cleaned output
cleaned = df.loc[~invalid_rows].copy()

    # Calculate sales revenue
cleaned["Sales"] = (
   cleaned["Quantity"] * cleaned["Unit_Price"]
)

    # Save outputs
cleaned.to_csv(CLEANED_FILE, index = False)

exceptions_file = (
   PROJECT_DIR / "reports" / "data_quality_exceptions.csv"
)
exceptions_file.parent.mkdir(parents = True, exist_ok = True)
exceptions.to_csv(exceptions_file, index = False)

print("Data cleaning completed!")
print(f"Original rows after duplicate removal: {len(df)}")
print(f"Cleaned valid rows: {len(cleaned)}")
print(f"Exception rows: {len(exceptions)}")
print(f"Cleaned file: {CLEANED_FILE}")
print(f"Exceptions file: {exceptions_file}")

return cleaned


if __name__ == "__main__":
   clean_sales_data(RAW_FILE)