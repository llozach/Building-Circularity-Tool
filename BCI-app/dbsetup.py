import duckdb
import os
from pathlib import Path

p = Path.cwd()
print(p)
os.chdir(p.parent)
data_dir = os.getcwd() + "\\data"
print(data_dir)

# create a connection to a building data file 'building_data.db'
con = duckdb.connect(data_dir + "\\building_data.db")

# create the R strategies table and load data into it
con.sql("CREATE TABLE r_strategies (Product STRING, Virgin DOUBLE, Reused DOUBLE, Recycled DOUBLE, Repurposed DOUBLE)")
con.sql("INSERT INTO r_strategies VALUES ('Product 1', 0.1, 0.2, 0.3, 0.4)")
con.sql("INSERT INTO r_strategies VALUES ('Product 2', 0.25, 0.25, 0.25, 0.25)")
con.sql("INSERT INTO r_strategies VALUES ('Product 3', 0.9, 0, 0.1, 0)")

# query the table
con.table("r_strategies").show()

# explicitly close the connection
con.close()