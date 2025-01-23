# helpers.py

from shiny.express import ui, render
import ibis
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go


def initialize_database(con, source_db, table_name):
    source_con = ibis.duckdb.connect(database=source_db)
    table = source_con.table(table_name).execute()
    con.create_table(table_name, table)
    source_con.disconnect()
