import sys
import os
import json
import networkx as nx

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from famous_people_network.wiki import Wiki


class PeopleNetwork:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.wiki = Wiki()

    def add_person(self, title, depth=0):
        if not self.wiki.extract_people(title):
            return False
        self.graph.add_node(title)
        self.wiki.update_portraits(title)
        self.get_page(title).user_added = True

        is_connected = set()
        people = [title]
        for level in range(depth):
            pages = self.wiki.extract_pages(people)
            people = []
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

                people.extend(people_neighbors)
                is_connected.add(person)

        return True

    def remove_person(self, title, depth=0):
        if not self.graph.has_node(person):
            return False
        people = self.graph.neighbors(title)
        self.graph.remove_node(title)

        for level in range(depth):
            new_people = []
            for person in people:
                if not self.graph.has_node(person):
                    continue
                neighbors = self.graph.neighbors(person)
                self.graph.remove_node(person)
                new_people.extend(neighbors)

            people = new_people

        return True

    def to_ctyoscape(self):
        label_fix = nx.relabel_nodes(self.graph, lambda x: hash(x) % 2**sys.hash_info.width)

        positions = nx.nx_pydot.graphviz_layout(label_fix, prog="sfdp")
        cytoscape_json = nx.cytoscape_data(self.graph)
        for node in cytoscape_json["elements"]["nodes"]:
            name = node["data"]["name"]
            pos = positions[hash(name) % 2**sys.hash_info.width]
            page = self.get_page(name)
            node["position"] = {"x": pos[0] * 3, "y": pos[1] * 3}

            if page.image is not None:
                node["data"]["url"] = page.image
            node["data"]["size"] = 120 if page.user_added else 30

        return cytoscape_json

    def get_page(self, title):
        return self.wiki.people_pages[title]
