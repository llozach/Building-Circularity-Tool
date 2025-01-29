# python snippet that will remove all products with only zero entries in the table r_strategies

import duckdb
from pathlib import Path

# Defining project paths

app_dir = Path(__file__).parent
data_dir = app_dir / "data"

# replace path to building_data.db as needed. Connection to db from other users must be closed
con = duckdb.connect(data_dir / "building_data.db")

# query to fetch and display the products with only zero entries
query = f"""SELECT * FROM r_strategies WHERE "Virgin"=0 and "Reused"=0 and "Recycled"=0 and "Repurposed"=0"""
result = con.execute(query).fetchall()
print("Products with only zero entries")
print(result)

# query to remove the products with only zero entries
remove = f"""DELETE FROM r_strategies WHERE "Virgin"=0 and "Reused"=0 and "Recycled"=0 and "Repurposed"=0"""
con.execute(remove)
result = con.execute(query).fetchall()
print("Products with only zero entries after removal")
print(result)  # should show an empty list
