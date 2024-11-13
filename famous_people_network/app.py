import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from dash import Dash, dcc, html, Input, Output, State, callback
from dash.exceptions import PreventUpdate
import dash_cytoscape as cyto
from famous_people_network.people_network import PeopleNetwork

app = Dash(__name__)

people_network = PeopleNetwork()

app.layout = html.Div(
    children=[
        html.Div(
            [
                html.Div(
                    [
                        "Person Name: ",
                        dcc.Input(id="input-person", value="", type="text"),
                    ]
                ),
                html.Div(
                    [
                        "Depth: ",
                        dcc.Slider(id="slider-depth", min=0, max=5, step=1, value=0),
                    ]
                ),
                html.Button(id="submit-button-state", disabled=False, children="Submit"),
            ]
        ),
        cyto.Cytoscape(
            id="people-network",
            layout={"name": "preset", "directed": True},
            style={"width": "100%", "height": "600px"},
            stylesheet=[
                {"selector": "node", "style": {"label": "data(id)"}},
                {
                    "selector": "edge",
                    "style": {
                        # The default curve style does not work with certain arrows
                        "curve-style": "bezier",
                        "target-arrow-shape": "triangle",
                    },
                },
            ],
        ),
    ]
)


@callback(
    Output("people-network", "elements"),
    Input("submit-button-state", "n_clicks"),
    State("input-person", "value"),
    State("slider-depth", "value"),
)
def add_person(n_clicks, person_name, depth):
    if n_clicks is None:
        raise PreventUpdate
    people_network.add_person(person_name, depth)
    return people_network.to_ctyoscape()["elements"]


if __name__ == "__main__":
    app.run(debug=True)
