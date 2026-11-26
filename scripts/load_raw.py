"""Load the Northwind CSV sources into the raw schema in DuckDB."""

import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DB_PATH = ROOT / "northwind.duckdb"

SOURCES = {
    # Current sales system
    "customer": "raw/customer.csv",
    "employees": "raw/employees.csv",
    "orders": "raw/orders.csv",
    "order_details": "raw/order_details.csv",
    "products": "raw/products.csv",
    "shippers": "raw/shippers.csv",
    "suppliers": "raw/suppliers.csv",
    # Legacy sales system
    "legacy_orders": "legacy/orders.csv",
    "legacy_order_details": "legacy/order_details.csv",
}


def main() -> None:
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    with duckdb.connect(str(DB_PATH)) as con:
        con.execute("CREATE SCHEMA IF NOT EXISTS raw")

        print(f"โหลดข้อมูลเข้า {DB_PATH.name}")
        for table, relative_path in SOURCES.items():
            csv_path = DATA_DIR / relative_path
            if not csv_path.is_file():
                raise FileNotFoundError(f"ไม่พบไฟล์ {csv_path}")

            # Escape single quotes so paths remain valid SQL string literals.
            csv_path_sql = csv_path.as_posix().replace("'", "''")
            con.execute(
                f"""
                CREATE OR REPLACE TABLE raw.{table} AS
                SELECT *
                FROM read_csv('{csv_path_sql}', header = true)
                """
            )
            row_count = con.execute(
                f"SELECT COUNT(*) FROM raw.{table}"
            ).fetchone()[0]
            print(f" raw.{table:<22} {row_count:>6,} แถว")

    print("เสร็จแล้ว — ขั้นต่อไป: dbt run")


if __name__ == "__main__":
    main()
