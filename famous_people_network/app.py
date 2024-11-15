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
        PanelGroup(
            id="panel-group",
            children=[
                Panel(
                    id="panel-1",
                    style={},
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
                        html.Button(id="button-submit-state", disabled=False, children="Submit"),
                        html.Div(id="graph-info"),
                    ],
                ),
                PanelResizeHandle(
                    html.Div(style={"backgroundColor": "grey", "height": "100%", "width": "5px"})
                ),
                Panel(
                    id="panel-2",
                    style={},
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
                                    },
                                },
                                {
                                    "selector": "edge",
                                    "style": {
                                        # The default curve style does not work with certain arrows
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
        )
    ],
    style={"height": "100vh"},
)


@callback(
    Output("people-network", "elements"),
    Input("button-submit-state", "n_clicks"),
    State("input-person", "value"),
    State("slider-depth", "value"),
    running=[(Output("button-submit-state", "disabled"), True, False)],
)
def add_person(n_clicks, person_name, depth):
    if n_clicks is None:
        raise PreventUpdate
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
