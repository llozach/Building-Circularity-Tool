#%% imports
import faicons as fa
import plotly.express as px
import numpy as np
import pandas as pd
# Load data and compute static values
from shinywidgets import render_plotly
# from functools import partial # used for creating navigation bars
from shiny import reactive, render
from shiny.express import input, ui
# from shiny.ui import page_navbar # used for creating navigation bars
import duckdb
#import ibis
#import helpers
#import os
from pathlib import Path

#%%
# Defining project paths

app_dir = Path(__file__).parent
data_dir = app_dir / "data"

#%%

# Checking whether using the database connection or not

database = True

# open connection to a building database file 'building_data.db'
if database:
    con = duckdb.connect(data_dir / "building_data.db")


#%%
# Defining the app functionalities and layout

# Add page title and sidebar
ui.page_opts(title="Building Circularity Tool", fillable=False)

with ui.sidebar(open="desktop"):
    ui.input_slider(
        "M",
        "Product Mass",
        min=0,
        max=100,
        value=50,
        post="t",
    )
    ui.input_slider(
        "V",
        "Virgin Materials",
        min=0,
        max=100,
        value=50,
        post="t",
    )
    ui.input_slider(
        "W",
        "Total Waste",
        min=0,
        max=100,
        value=50,
        post="t",
    )
    ui.input_slider(
        "W_c",
        "Recycling waste after collection",
        min=0,
        max=100,
        value=50,
        post="t",
    )
    ui.input_slider(
        "W_f",
        "Recycling waste before production",
        min=0,
        max=100,
        value=50,
        post="t",
    )
    ui.input_slider(
        "L",
        "Product lifetime",
        min=0,
        max=100,
        value=50,
        post="yr",
    )
    ui.input_slider(
        "U",
        "Product functional unit",
        min=0,
        max=100,
        value=50,
        post=".unit",
    )
    ui.input_slider(
        "M_av",
        "Average product mass",
        min=0,
        max=100,
        value=50,
        post="t",
    )
    ui.input_slider(
        "L_av",
        "Average product lifetime",
        min=0,
        max=100,
        value=50,
        post="yr",
    )
    ui.input_slider(
        "U_av",
        "Average product functional unit",
        min=0,
        max=100,
        value=50,
        post=".unit",
    )
    ui.input_checkbox_group(
        "utility",
        "Available data",
        ["Mass", "Lifetime", "Functional units"],
        selected=["Mass", "Lifetime", "Functional units"],
        inline=True,
    )
    ui.input_action_button("reset", "Reset filter")

# Add main content
ICONS = {
    "building": fa.icon_svg("building", "regular"),
    "MCI/BCI": fa.icon_svg("recycle", "solid"),
    "cost": fa.icon_svg("dollar-sign"),
    "gear": fa.icon_svg("gears", "solid"),
}

if database:
    R_strategies = con.table("r_strategies").df()
    # R_strategies.drop(columns=["Product"], inplace=True)
    print(R_strategies)

    default_building_data = pd.DataFrame(
        {"Product": "Product "+str(len(R_strategies)+1), "Virgin": 0.0, "Reused": 0.0, "Recycled": 0.0, "Repurposed": 0.0},
        index=["Product"]
    )

else:
    R_strategies = pd.DataFrame(
        np.array([[0.1, 0.2, 0.3, 0.4],[0.25, 0.25, 0.25, 0.25],[0.9, 0, 0.1, 0]]),
        columns=["Virgin", "Reused", "Recycled", "Repurposed"])
    # ,index=["Product 1", "Product 2", "Product 3"]
    # )
    print(R_strategies)


with ui.layout_columns(fill=False):
    with ui.value_box(showcase=ICONS["building"]):
        "Building Circularity Indicator"

        @render.express
        def building_circularity_score():
            f"""{bci():.1%}"""

    with ui.value_box(showcase=ICONS["MCI/BCI"]):
        "Material Circularity Indicator"

        @render.express
        def material_circularity():
            f"""{mci():.1%}"""

    with ui.value_box(showcase=ICONS["cost"]):
        "Project cost"

        @render.express
        def average_bill():
            f"""${project_cost():.2f}"""


ui.markdown(
    """
    ## Section 1: Product Circularity
    
    The following section displays the different **circularity strategies** applied to each product,
    and allows you to feed the database with new product data.
    
    """
)

with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Circular strategies for each product")

        @render.data_frame
        def table():
            return render.DataGrid(R_strategies, editable=True)

        if database:

            ui.markdown(
                """
                `Write a product in the database by entering data:`
                """
            )

            @render.data_frame
            def building_data_input():
                return render.DataGrid(default_building_data, editable=True)


            ui.input_action_button("storing_data", "Store new product data")

    with ui.card(full_screen=True):
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "Product circularity pie chart"
            with ui.popover(title="Product to display", placement="top"):
                ICONS["MCI/BCI"]
                ui.input_radio_buttons(
                    "plot_selection",
                    None,
                    ["Product " + str(prod+1) for prod in list(R_strategies.index)],
                    inline=True,
                )

        @render_plotly
        def scatterplot():
            product_data = table.data_view().loc[int(input.plot_selection()[-1:])-1]
            return px.pie(
                product_data,
                values=product_data.values,
                names=product_data.index,
                title=f"Strategies for {input.plot_selection()}",
            )


ui.markdown(
    """
    ## Section 2: Product Disassembly Potential

    The following section relies on Durmisevic Determining Disassembly Factors (DDFs) for quantifying the disassembly
    potential of each product based on fuzzy variables.

    """
)

# Define checkboxes for calculating the disassembly potential
with ((ui.layout_columns())):
    with ui.card(full_screen=True):
        ui.card_header("Determining Disassembly factors (DDFs)")
        with ui.div(style="max-height: 400px; overflow-y: auto;"):
            ui.markdown(
                """
                **Accessibility to connection**
                """
            )
            ui.input_radio_buttons(
                "Accessibility",
                "",
                [
                    "Accessible",
                    "Accessible with additional operation which causes no damage",
                    "Accessible with additional operation which is reparable damage",
                    "Accessible with additional operation which causes damage",
                    "Not accessible, total damage"
                ],
                inline=False,
                width="100%",
            )
            ui.markdown(
                """
                **Type of connection**
                """
            )
            ui.input_radio_buttons(
                "Type",
                "",
                [
                    "Accessory external connection or connection system",
                    "Direct connection with additional fixing devices",
                    "Direct integral connection with inserts (pin)",
                    "Filled soft chemical connection",
                    "Filled hard chemical connection",
                    "Direct chemical connection"
                ],
                inline=False,
                width="100%",
            )
            ui.markdown(
                """
                **Independency**
                """
            )
            ui.input_radio_buttons(
                "Independency",
                "",
                [
                    "Modular zoning",
                    "Planned interpenetrating",
                    "Planned for one solution",
                    "Unplanned interpenetrating",
                    "Total dependence"
                ],
                inline=False,
                width="100%",
            )
            ui.markdown(
                """
                **Method of fabrication**
                """
            )
            ui.input_radio_buttons(
                "Method",
                "",
                [
                    "Pre-made geometry",
                    "Half standardized geometry",
                    "Geometry made on construction site"
                ],
                inline=False,
                width="100%",
            )
            ui.markdown(
                """
                **Type of relational pattern**
                """
            )
            ui.input_radio_buttons(
                "Pattern",
                "",
                [
                    "One or two connections",
                    "Three connections",
                    "Four connections",
                    "Five or more connections"
                ],
                inline=False,
                width="100%",
            )

    with ui.card(full_screen=True):
        ui.card_header("Disassembly Potential")

        ui.markdown(
            """
            `Qualitative DDFs are allocated a fuzzy variable based on Durmisevic.`
            """
        )

        @render.data_frame
        def disassembly_potential():

            df = pd.DataFrame(ddf_input(), columns=["Determining Disassembly Factor", "Score"])

            return render.DataGrid(df)

        ui.markdown(
            """
            `DDFs are attributed equal weights for the calculation of the disassembly potential.`
            """
        )

        with ui.value_box(showcase=ICONS["gear"]):
            "Disassembly Score"

            @render.express
            def disassembly_score():
                f"{dis_pot():.1%}"

ui.markdown(
    """
    ## Section 3: Whole Building Circularity Indicator

    The following section aggregates both product **circularity** and **disassembly** potential into a final indicator
    at the building level. Some tracks for improvement are also suggested.

    """
)

with ((ui.layout_columns())):
    with ui.card(full_screen=True):
        ui.card_header("Building Circularity Indicator")

        with ui.value_box(showcase=ICONS["building"]):
            "Whole Building Circularity Indicator"


            @render.express
            def building_indicator():
                f"{bci():.1%}"

    with ui.card(full_screen=True):
        ui.card_header("Potential Tracks for Improvement")
        ui.markdown(
            """
            The building circularity can be improved by:
            - **Increasing products lifetime**
            - **Reducing products mass**
            - **Include design for disassembly**            
            """
        )


# Add CSS styles to the app
ui.include_css(app_dir / "styles.css")

# explicitly close the connection
#con.close()

#%%
# Reactive calculations and effects


@reactive.calc
def lfi():
    m = input.M()
    v = input.V()
    w = input.W()
    w_f = input.W_f()
    w_c = input.W_c()
    return (v+w)/(2*m + (w_f-w_c)/2)


@reactive.calc
def mci():
    m = input.M()
    v = input.V()
    w = input.W()
    w_f = input.W_f()
    w_c = input.W_c()
    lifetime = input.L()
    lifetime_av = input.L_av()
    u = input.U()
    u_av = input.U_av()
    m_av = input.M_av()
    x_param = input.utility()

    linear_flow_index = (v+w) / (2*m + (w_f-w_c)/2)

    if "Mass" not in x_param:
        m, m_av = 1, 1
    elif "Lifetime" not in x_param:
        lifetime, lifetime_av = 1, 1
    elif "Functional units" not in x_param:
        u, u_av = 1, 1

    x = (lifetime*u*m) / (lifetime_av*u_av*m_av)
    f = 0.9/x
    return max(0, 1-linear_flow_index*f)


@reactive.calc
def project_cost():
    m = input.M()
    v = input.V()
    cost_per_kg_v = 12  # in USD
    cost_per_kg_other = 6  # in USD
    return v*cost_per_kg_v + (m-v)*cost_per_kg_other


@reactive.calc
def ddf_input():
    a = input.Accessibility()
    t = input.Type()
    i = input.Independency()
    m = input.Method()
    p = input.Pattern()

    acc, typ, ind, met, pat = 0, 0, 0, 0, 0

    if a == 'Accessible':
        acc = 1
    elif a == "Accessible with additional operation which causes no damage":
        acc = 0.8
    elif a == "Accessible with additional operation which is reparable damage":
        acc = 0.6
    elif a == "Accessible with additional operation which causes damage":
        acc = 0.4
    elif a == "Not accessible, total damage":
        acc = 0.1

    if t == "Accessory external connection or connection system":
        typ = 1
    elif t == "Direct connection with additional fixing devices":
        typ = 0.8
    elif t == "Direct integral connection with inserts (pin)":
        typ = 0.6
    elif t == "Filled soft chemical connection":
        typ = 0.2
    elif t == "Filled hard chemical connection":
        typ = 0.1
    elif t == "Direct chemical connection":
        typ = 0.1

    if i == "Modular zoning":
        ind = 1
    elif i == "Planned interpenetrating":
        ind = 0.8
    elif i == "Planned for one solution":
        ind = 0.6
    elif i == "Unplanned interpenetrating":
        ind = 0.2
    elif i == "Total dependence":
        ind = 0.1

    if m == "Pre-made geometry":
        met = 1
    elif m == "Half standardized geometry":
        met = 0.8
    elif m == "Geometry made on construction site":
        met = 0.6

    if p == "One or two connections":
        pat = 1
    elif p == "Three connections":
        pat = 0.8
    elif p == "Four connections":
        pat = 0.6
    elif p == "Five or more connections":
        pat = 0.2

    return np.array([["Accessibility to connection", acc],
                     ["Type of connection", typ],
                     ["Independency", ind],
                     ["Method of fabrication", met],
                     ["Type of relational pattern", pat]
                     ])


@reactive.calc
def dis_pot():
    acc = ddf_input()[0][1]
    typ = ddf_input()[1][1]
    ind = ddf_input()[2][1]
    met = ddf_input()[3][1]
    pat = ddf_input()[4][1]
    return (float(acc)+float(typ)+float(ind)+float(met)+float(pat))/5


@reactive.calc
def bci():
    dp = dis_pot()
    pci = mci()
    return dp*pci


@reactive.effect
@reactive.event(input.reset)
def _():
    ui.update_checkbox_group("Accessibility")

# Capture the input data from the building_data_input() table


if database:

    @reactive.effect
    @reactive.event(input.storing_data)
    def store_new_data():
        # Extract new data as scalar values
        new_data = building_data_input.data_view()
        product_name = str(new_data['Product'].iloc[0])  # Convert to string if needed
        virgin = float(new_data['Virgin'].iloc[0])  # Convert to float
        reused = float(new_data['Reused'].iloc[0])  # Convert to float
        recycled = float(new_data['Recycled'].iloc[0])  # Convert to float
        repurposed = float(new_data['Repurposed'].iloc[0])  # Convert to float

        try:
            # Use a parameterized query to insert the data
            con.execute("""
                INSERT INTO r_strategies (Product, Virgin, Reused, Recycled, Repurposed)
                VALUES (?, ?, ?, ?, ?)
            """, [product_name, virgin, reused, recycled, repurposed])

            # Optionally display the updated table
            con.sql("SELECT * FROM r_strategies").show()
            print("Data inserted successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")

    #db_input = building_data_input.data_view().loc['New product']
    # con.sql("INSERT INTO r_strategies VALUES ('New Product', 0.1, 0.2, 0.3, 0.4)")