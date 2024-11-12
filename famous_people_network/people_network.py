from collections import defaultdict
import re
import requests
import networkx as nx


class PeopleNetwork:
    url = "https://en.wikipedia.org/w/api.php"

    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.sidebars = {}
        self.visited_pages = set()

    def search_wiki(self, title):
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "utf8": 1,
            "srsearch": title,
        }

        data = requests.get(self.url, params=params).json()
        pages = data["query"]["search"]
        return pages

    def add_person(self, title, depth=0):
        self.graph.add_node(title)
        is_connected = set()

        people = [title]
        for level in range(depth):
            new_people = []
            sidebars = self._get_sidebars(people)

            for person in people:
                if person in is_connected or person not in sidebars:
                    continue

                if person not in self.visited_pages:
                    neighbors = self._get_sidebar_links(sidebars[person])
                    people_neighbors = self._get_people(neighbors)

                    self.graph.add_edges_from([(person, neighbor) for neighbor in people_neighbors])
                else:
                    people_neighbors = self.graph.neighbors(person)

                new_people.extend(people_neighbors)
                is_connected.add(person)

            self.visited_pages.update(people)
            people = new_people

    def _get_people(self, titles):
        if not isinstance(titles, list):
            titles = [titles]

        # TODO More checks for person
        all_sidebars = self._get_sidebars(titles)
        regexp = re.compile(r"\| birth_date")
        people = []

        for title in titles:
            if (
                self.graph.has_node(title)
                or title in all_sidebars
                and regexp.search(all_sidebars[title]) is not None
            ):
                people.append(title)
                self.sidebars[title] = all_sidebars[title]
            else:
                self.visited_pages.add(title)

        return people

    def _get_sidebar_links(self, sidebar):
        return list(set(re.findall(r"\[\[.*?(.*?)[\|\]]", sidebar)))

    def _get_sidebars(self, titles):
        if not isinstance(titles, list):
            titles = [titles]

        sidebars = {}
        step = 50
        # TODO check if already visited
        for i in range(0, len(titles), step):
            params = {
                "action": "query",
                "prop": "revisions",
                "format": "json",
                "rvprop": "content",
                "rvslots": "main",
                "titles": "|".join(titles[i : i + step]),
                "rvsection": 0,
            }
            data = requests.get(self.url, params=params).json()
            pages = data["query"]["pages"]

            for page in pages.values():
                if "revisions" in page:
                    sidebars[page["title"]] = page["revisions"][0]["slots"]["main"]["*"]

        return sidebars

    def _get_links(self, title):
        session = requests.Session()
        params = {
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "links",
            "pllimit": "max",
        }

        data = session.get(url=self.url, params=params).json()
        pages = data["query"]["pages"]

        links = set()

        for val in pages.values():
            if "links" not in val:
                return []
            for link in val["links"]:
                links.add(link["title"])

        while "continue" in data:
            plcontinue = data["continue"]["plcontinue"]
            params["plcontinue"] = plcontinue

            data = session.get(url=self.url, params=params).json()
            pages = data["query"]["pages"]

            for val in pages.values():
                for link in val["links"]:
                    links.add(link["title"])

        return links

    def _get_categories(self, titles):
        if not isinstance(titles, list):
            titles = [titles]

        sidebars = {}
        step = 50

        for i in range(0, len(titles), step):
            params = {
                "action": "query",
                "format": "json",
                "prop": "categories",
                "titles": "|".join(titles),
            }
            data = requests.get(self.url, params=params).json()
            pages = data["query"]["pages"]

            for j, page in enumerate(pages.values()):
                if "revisions" in page:
                    sidebars[titles[i + j]] = page["revisions"][0]["slots"]["main"]["*"]

        return sidebars
