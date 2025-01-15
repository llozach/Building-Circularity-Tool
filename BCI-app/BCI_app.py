import faicons as fa
import plotly.express as px
import numpy as np
import pandas as pd

# Load data and compute static values
from shared import app_dir
from shinywidgets import render_plotly

from shiny import reactive, render
from shiny.express import input, ui

#Add some CSS to the app

ui.tags.style(
    ".card-header { color:white; background:#5e5a5a !important; }"
)

# Add page title and sidebar
ui.page_opts(title="Building Circularity Tool", fillable=True)

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
        "Average product lifetime",
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
        "lifetime",
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

R_strategies = pd.DataFrame(np.array([[0.1, 0.2, 0.3, 0.4],[0.25, 0.25, 0.25, 0.25],[0.9, 0, 0.1, 0]]), columns=["Virgin", "Reused", "Recycled", "Repurposed"], index=["Product 1", "Product 2", "Product 3"])

with ui.layout_columns(fill=False):
    with ui.value_box(showcase=ICONS["building"]):
        "Linear Flow Index"

        @render.express
        def linear_flow():
            f"{LFI():.1%}"

    with ui.value_box(showcase=ICONS["MCI/BCI"]):
        "Material Circularity Indicator"

        @render.express
        def material_circularity():
            f"{MCI():.1%}"

    with ui.value_box(showcase=ICONS["cost"]):
        "Project cost"

        @render.express
        def average_bill():
            f"${project_cost():.2f}"


with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Circularity strategies applied for each product")

        @render.data_frame
        def table():
            return render.DataGrid(R_strategies)

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
            product_data = R_strategies.loc[input.plot_selection()]
            return px.pie(
                product_data,
                values=product_data.values,
                names=product_data.index,
                title=f"Strategies for {input.plot_selection()}",
            )

#Define checkboxes for calculating the disassembly potential

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


with ((ui.layout_columns())):
    with ui.card(full_screen=True):
        ui.card_header("Final")

        @render.data_frame
        def disassembly_potential():

            df = pd.DataFrame(ddf_input(), columns=["DDF name", "DDF score"])

            return render.DataGrid(df)
#Add CSS styles to the app
ui.include_css(app_dir / "styles.css")

# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------


@reactive.calc
def LFI():
    M = input.M()
    V = input.V()
    W = input.W()
    W_f = input.W_f()
    W_c = input.W_c()
    return((V+W) / (2*M + (W_f-W_c)/2) )


@reactive.calc
def MCI():
    M = input.M()
    V = input.V()
    W = input.W()
    W_f = input.W_f()
    W_c = input.W_c()
    L = input.L()
    L_av = input.L_av()
    U = input.U()
    U_av = input.U_av()
    M_av = input.M_av()

    lfi = (V+W) / (2*M + (W_f-W_c)/2)

    X = (L*U*M) / (L_av*U_av*M_av)

    f = 0.9/X
    return(max(0, 1-lfi*f))


@reactive.calc
def project_cost():
    M = input.M()
    V = input.V()
    cost_per_kg_V = 12 #in USD
    cost_per_kg_other = 6
    return(V*cost_per_kg_V + (M-V)*cost_per_kg_other)


@reactive.calc
def ddf_input():
    A = input.Accessibility()
    T = input.Type()
    print(A,T)
    acc, typ = 0, 0
    if A == 'Accessible':
        acc = 1
    elif A == "Accessible with additional operation which causes no damage":
        acc = 0.8
    elif A == "Accessible with additional operation which is reparable damage":
        acc = 0.6
    elif A == "Accessible with additional operation which causes damage":
        acc = 0.4
    elif A == "Not accessible, total damage":
        acc = 0.1

    if T == "Accessory external connection or connection system":
        typ = 1
    elif T == "Direct connection with additional fixing devices":
        typ = 0.8
    elif T == "Direct integral connection with inserts (pin)":
        typ = 0.6
    elif T == "Filled soft chemical connection":
        typ = 0.2
    elif T == "Filled hard chemical connection":
        typ = 0.1
    elif T == "Direct chemical connection":
        typ = 0.1
    print([[A, T],[acc, typ]])
    print(acc, typ)
    return(np.array([["Accessibility to connection", acc],["Type of connection", typ]]))


@reactive.effect
@reactive.event(input.reset)
def _():
    ui.update_checkbox_group("Accessibility")


