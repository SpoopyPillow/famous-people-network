import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from dash import Dash, dcc, html, Input, Output, callback
import networkx as nx
import dash_cytoscape as cyto
from famous_people_network.people_network import PeopleNetwork

app = Dash(__name__)

people_network = PeopleNetwork()
people_network.add_person("Aristotle", 3)

pos = nx.nx_pydot.graphviz_layout(people_network.graph, prog="neato")
cytoscape_json = nx.cytoscape_data(people_network.graph)
for node in cytoscape_json["elements"]["nodes"]:
    name = node["data"].pop("name")
    node["data"]["label"] = name
    node["position"] = {"x": pos[name][0] * 5, "y": pos[name][1] * 5}

app.layout = html.Div(
    [
        cyto.Cytoscape(
            id="people-network",
            layout={"name": "preset", "directed": True},
            style={"width": "100%", "height": "400px"},
            elements=cytoscape_json["elements"],
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
        )
    ]
)

if __name__ == "__main__":
    app.run(debug=True)
