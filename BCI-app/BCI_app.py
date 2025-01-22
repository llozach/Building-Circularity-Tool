import faicons as fa
import plotly.express as px
import numpy as np
import pandas as pd

# Load data and compute static values
from shared import app_dir
from shinywidgets import render_plotly
# from functools import partial # used for creating navigation bars

from shiny import reactive, render
from shiny.express import input, ui
# from shiny.ui import page_navbar # used for creating navigation bars
import ibis
import helpers
# Initialize the Ibis connection
con = ibis.duckdb.connect(database=':memory:')

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
}

R_strategies = pd.DataFrame(
    np.array([[0.1, 0.2, 0.3, 0.4],[0.25, 0.25, 0.25, 0.25],[0.9, 0, 0.1, 0]]),
    columns=["Virgin", "Reused", "Recycled", "Repurposed"],
    index=["Product 1", "Product 2", "Product 3"]
)

with ui.layout_columns(fill=False):
    with ui.value_box(showcase=ICONS["building"]):
        "Linear Flow Index"

        @render.express
        def linear_flow():
            f"{lfi():.1%}"

    with ui.value_box(showcase=ICONS["MCI/BCI"]):
        "Material Circularity Indicator"

        @render.express
        def material_circularity():
            f"{mci():.1%}"

    with ui.value_box(showcase=ICONS["cost"]):
        "Project cost"

        @render.express
        def average_bill():
            f"${project_cost():.2f}"


"Section 1: Assessing Product Circularity"

with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Circularity strategies applied for each product")

        @render.data_frame
        def table():
            return render.DataGrid(R_strategies, editable=True)

    with ui.card(full_screen=True):
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "Circularity pie chart"
            with ui.popover(title="Product to display", placement="top"):
                ICONS["MCI/BCI"]
                ui.input_radio_buttons(
                    "plot_selection",
                    None,
                    list(R_strategies.index),
                    inline=True,
                )

        @render_plotly
        def scatterplot():
            product_data = table.data_view().loc[input.plot_selection()]
            return px.pie(
                product_data,
                values=product_data.values,
                names=product_data.index,
                title=f"Strategies for {input.plot_selection()}",
            )

# Define checkboxes for calculating the disassembly potential
"Section 2: Assessing Product Disassembly Potential"

with ((ui.layout_columns())):
    with ui.card(full_screen=True):
        ui.card_header("Determining Disassembly factors")
        ui.input_radio_buttons(
            "Accessibility",
            "Accessibility to connection",
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
        ui.input_radio_buttons(
            "Type",
            "Type of connection",
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

    with ui.card(full_screen=True):
        ui.card_header("Whole Building Circularity Indicator")

        @render.data_frame
        def disassembly_potential():

            df = pd.DataFrame(ddf_input(), columns=["DDF name", "DDF score"])

            return render.DataGrid(df)

"Section 3: Assessing Whole Building Circularity Indicator"

with ((ui.layout_columns())):
    with ui.card(full_screen=True):
        ui.card_header("Building Circularity Indicator")
        "Trying to display some text in the card"
        with ui.value_box(showcase=ICONS["building"]):
            "Whole Building Circularity Indicator"


            @render.express
            def building_indicator():
                f"{bci():.1%}"


# Add CSS styles to the app
ui.include_css(app_dir / "styles.css")

# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------


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
    acc, typ = 0, 0

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

    return np.array([["Accessibility to connection", acc], ["Type of connection", typ]])


@reactive.calc
def bci():
    acc = ddf_input()[0][1]
    typ = ddf_input()[1][1]
    pci = mci()
    return (float(acc)+float(typ))/2*pci


@reactive.effect
@reactive.event(input.reset)
def _():
    ui.update_checkbox_group("Accessibility")


