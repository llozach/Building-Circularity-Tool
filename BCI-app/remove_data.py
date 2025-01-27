# python snippet that will remove all products with only zero entries in the table r_strategies

import duckdb

# replace path to building_data.db as needed. Connection to db from other users must be closed
con = duckdb.connect('/Users/tlm/Documents/Building-Circularity-Tool/BCI-app/data/building_data.db')

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
