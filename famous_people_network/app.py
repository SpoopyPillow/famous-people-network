import sys
import os
from dash import Dash, dcc, html, Input, Output, State, callback
from dash.exceptions import PreventUpdate
import dash_cytoscape as cyto
from dash_resizable_panels import PanelGroup, Panel, PanelResizeHandle

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from famous_people_network.people_network import PeopleNetwork


app = Dash(__name__)

people_network = PeopleNetwork()

app.layout = html.Div(
    [
        html.Div(id="none", children=None),
        PanelGroup(
            id="panel-group",
            children=[
                Panel(
                    id="panel-1",
                    style={"padding": 10, "margin": 10},
                    children=[
                        html.H1("Famous People Network"),
                        html.Div(
                            [
                                html.P("Person Name: "),
                                dcc.Input(id="input-person", value="", type="text"),
                            ]
                        ),
                        html.Div(
                            [
                                html.P("Depth: "),
                                dcc.Slider(id="slider-depth", min=0, max=5, step=1, value=0),
                            ]
                        ),
                        html.Button(id="button-submit", disabled=False, children="Submit"),
                        html.Div(id="graph-info"),
                        html.Div([html.Button(id="button-reset", children="Reset")]),
                    ],
                ),
                PanelResizeHandle(
                    html.Div(style={"backgroundColor": "grey", "height": "100%", "width": "5px"})
                ),
                Panel(
                    id="panel-2",
                    style={"padding": 10, "margin": 10},
                    children=[
                        cyto.Cytoscape(
                            id="people-network",
                            layout={"name": "preset", "directed": True},
                            style={"height": "100%"},
                            stylesheet=[
                                {
                                    "selector": "node",
                                    "style": {
                                        "label": "data(name)",
                                        "color": "white",
                                        "width": "data(size)",
                                        "height": "data(size)",
                                        "background-fit": "cover",
                                        "background-image": "data(url)",
                                        "background-color": "white",
                                    },
                                },
                                {
                                    "selector": "edge",
                                    "style": {
                                        "curve-style": "straight",
                                        "target-arrow-shape": "triangle",
                                    },
                                },
                            ],
                        ),
                    ],
                ),
            ],
            direction="horizontal",
        ),
        dcc.Store(id="button-previous", data={"reset": 0, "submit": 0}),
        dcc.Store(id="button-clicked"),
    ],
    style={"height": "100vh"},
)


@callback(
    Output("button-clicked", "data"),
    Output("button-previous", "data"),
    Input("button-reset", "n_clicks"),
    Input("button-submit", "n_clicks"),
    State("button-previous", "data"),
)
def button_action(reset, submit, previous):
    clicked = None
    if reset is not None and reset != previous["reset"]:
        previous["reset"] += 1
        clicked = "reset"
    if submit is not None and submit != previous["submit"]:
        previous["submit"] += 1
        clicked = "submit"

    return clicked, previous


@callback(
    Output("people-network", "elements"),
    Input("button-clicked", "data"),
    State("input-person", "value"),
    State("slider-depth", "value"),
    running=[(Output("button-submit", "disabled"), True, False)],
)
def update_graph(clicked, person_name, depth):
    if clicked is None:
        raise PreventUpdate
    if clicked == "reset":
        people_network.reset_graph()
    elif clicked == "submit":
        people_network.add_person(person_name, depth)

    return people_network.to_ctyoscape()["elements"]


@callback(
    Output("graph-info", "children"),
    Input("people-network", "selectedNodeData"),
    Input("people-network", "selectedEdgeData"),
)
def display_node_page(selected_nodes, selected_edges):
    if selected_nodes and selected_edges:
        return "node and edge"
    elif selected_nodes:
        node = selected_nodes[-1]
        title = node["name"]
        return people_network.get_page(title).summary
    elif selected_edges:
        return "edge"


if __name__ == "__main__":
    app.run(debug=True)
