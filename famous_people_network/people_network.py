import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from famous_people_network.wiki import Wiki
from collections import defaultdict
import re
import requests
import networkx as nx
import json


class PeopleNetwork:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.wiki = Wiki()

    def add_person(self, title, depth=0):
        if not self.wiki.extract_people(title):
            return
        self.graph.add_node(title)

        is_connected = set()
        # TODO Use deque
        people = [title]
        for level in range(depth):
            new_people = []
            pages = self.wiki.extract_pages(people)

            for person, page in pages.items():
                if person in is_connected:
                    continue

                neighbors = page.extract_sidebar_links()
                people_neighbors = self.wiki.extract_people(neighbors)

                for neighbor in people_neighbors:
                    self.graph.add_edge(
                        person,
                        neighbor,
                        labels=json.dumps(page.extract_sidebar_link_info(neighbor)),
                    )

                new_people.extend(people_neighbors)
                is_connected.add(person)

            people = new_people

    def to_ctyoscape(self):
        label_fix = nx.relabel_nodes(
            self.graph, lambda x: x.encode("ascii", errors="ignore").decode()
        )
        pos = nx.nx_pydot.graphviz_layout(label_fix, prog="sfdp")
        cytoscape_json = nx.cytoscape_data(label_fix)
        for node in cytoscape_json["elements"]["nodes"]:
            name = node["data"]["name"]
            node["position"] = {"x": pos[name][0] * 3, "y": pos[name][1] * 3}

        return cytoscape_json
