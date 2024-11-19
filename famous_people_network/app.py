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
                        html.Pre(html.H1("Famous People Network")),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        dcc.Dropdown(
                                            id="dropdown-operation",
                                            options=[
                                                {
                                                    "label": html.Pre(
                                                        ["Add Person"],
                                                    ),
                                                    "value": "Add Person",
                                                },
                                                {
                                                    "label": html.Pre(
                                                        ["Remove Person"],
                                                    ),
                                                    "value": "Remove Person",
                                                },
                                            ],
                                            value="Add Person",
                                            multi=False,
                                            clearable=False,
                                            style={
                                                "width": "100%",
                                                "text-align": "center",
                                            },
                                        ),
                                    ],
                                    style={"flex": 1},
                                ),
                                html.Div(
                                    html.Pre(
                                        html.P("Depth: "),
                                    ),
                                    style={"flex": 2, "padding": "10px", "text-align": "center"},
                                ),
                            ],
                            style={"display": "flex", "flexDirection": "row"},
                        ),
                        html.Div(
                            [
                                html.Div(
                                    dcc.Input(
                                        id="input-person",
                                        className="input-default",
                                        value="",
                                        type="text",
                                        style={"width": "100%", "padding": "5px"},
                                    ),
                                    style={"flex": 1},
                                ),
                                html.Div(
                                    dcc.Slider(
                                        id="slider-depth",
                                        min=1,
                                        max=5,
                                        step=1,
                                        value=1,
                                    ),
                                    style={"flex": 2, "padding": "0 0 0 5%"},
                                ),
                            ],
                            style={"display": "flex", "flexDirection": "row"},
                        ),
                        html.Div(
                            html.Button(
                                id="button-submit",
                                className="button-default",
                                disabled=False,
                                children="Submit",
                                style={"margin": "0 auto", "height": "5vh", "width": "100vw"},
                            ),
                            style={"padding": "20px 0 0 0", "display": "flex"},
                        ),
                        html.Div(
                            id="graph-info",
                            style={
                                "height": "50vh",
                                "margin": "5vh auto",
                                "padding": "0 10px 0px 10px",
                                "border": "1px white solid",
                            },
                        ),
                        html.Div(
                            html.Button(
                                id="button-reset",
                                className="button-default",
                                children="Reset",
                                style={"margin": "0 auto", "height": "5vh", "width": "100vw"},
                            ),
                            style={"display": "flex"},
                        ),
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
                                        "background-color": "data(color)",
                                    },
                                },
                                {
                                    "selector": "edge",
                                    "style": {},
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
    State("dropdown-operation", "value"),
    running=[(Output("button-submit", "disabled"), True, False)],
)
def update_graph(clicked, person_name, depth, operation):
    if clicked is None:
        raise PreventUpdate
    if clicked == "reset":
        people_network.reset_graph()
    elif clicked == "submit":
        if operation == "Add Person":
            people_network.add_person(person_name, depth - 1)
        elif operation == "Remove Person":
            people_network.remove_person(person_name, depth - 1)

    return people_network.to_ctyoscape_cluster()


@callback(
    Output("graph-info", "children"),
    Input("people-network", "selectedNodeData"),
    Input("people-network", "selectedEdgeData"),
)
def display_node_page(selected_nodes, selected_edges):
    output = []

    if selected_nodes:
        node = selected_nodes[-1]
        title = node["name"]
        summary = people_network.get_page(title).summary
        output.append(html.H3(title))
        output.append(html.P(summary))

    elif selected_edges:
        edge = selected_edges[-1]
        source = people_network.get_page(edge["source"])
        target = people_network.get_page(edge["target"])
        source_to_target = source.extract_sidebar_link_info(target)
        target_to_source = target.extract_sidebar_link_info(source)

        output.append(html.H3("Connection"))
        if source_to_target:
            output.append(
                html.P(source.title + " (" + ", ".join(source_to_target) + "): " + target.title)
            )
        if target_to_source:
            output.append(
                html.P(target.title + " (" + ", ".join(target_to_source) + "): " + source.title)
            )

    return output


if __name__ == "__main__":
    app.run(debug=True)
