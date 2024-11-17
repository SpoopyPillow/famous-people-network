import sys
import os
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from famous_people_network.page import Page


class Wiki:
    url = "https://en.wikipedia.org/w/api.php"

    def __init__(self):
        # maybe include language
        self.people_pages = {}
        self.visited_titles = set()

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

    def extract_people(self, titles):
        if not isinstance(titles, list):
            titles = [titles]

        pages = self.extract_pages(titles)
        people = [title for title in pages if pages[title].is_person()]

        return people

    # Visited pages that are not people are not included
    def extract_pages(self, titles):
        if not isinstance(titles, list):
            titles = [titles]

        pages = {}
        unvisited = []

        for title in titles:
            if title in self.people_pages:
                pages[title] = self.people_pages[title]
            elif title not in self.visited_titles:
                unvisited.append(title)

        titles = unvisited

        sidebars = self._extract_sidebars(titles)
        summaries = self._extract_summaries(titles)
        for title in set([*sidebars, *summaries]):
            sidebar = sidebars[title] if title in sidebars else ""
            summary = summaries[title] if title in summaries else ""
            page = Page(title=title, sidebar=sidebar, summary=summary)

            pages[title] = page
            self.visited_titles.add(title)
            if page.is_person():
                self.people_pages[title] = page
        return pages

    def _extract_sidebars(self, titles):
        if not isinstance(titles, list):
            titles = [titles]
        session = requests.Session()
        sidebars = {}
        step = 50

        for i in range(0, len(titles), step):
            params = {
                "action": "query",
                "prop": "revisions",
                "format": "json",
                "rvprop": "content",
                "rvslots": "main",
                "rvsection": 0,
                "redirects": 1,
                "titles": "|".join(titles[i : i + step]),
            }
            data = session.get(self.url, params=params).json()
            pages = data["query"]["pages"]

            for page in pages.values():
                if "revisions" in page:
                    title = page["title"]
                    sidebars[title] = page["revisions"][0]["slots"]["main"]["*"]

            while "continue" in data:
                rvcontinue = data["continue"]["rvcontinue"]
                params["rvcontinue"] = rvcontinue

                data = session.get(url=self.url, params=params).json()
                pages = data["query"]["pages"]

                for page in pages.values():
                    if "revisions" in page:
                        title = page["title"]
                        sidebars[title] = page["revisions"][0]["slots"]["main"]["*"]

        return sidebars

    def _extract_summaries(self, titles):
        if not isinstance(titles, list):
            titles = [titles]
        session = requests.Session()
        summaries = {}
        step = 50

        for i in range(0, len(titles), step):
            params = {
                "action": "query",
                "prop": "extracts",
                "format": "json",
                "exintro": 0,
                "exsentences": 5,
                "explaintext": 0,
                "redirects": 1,
                "titles": "|".join(titles[i : i + step]),
            }
            data = session.get(self.url, params=params).json()
            pages = data["query"]["pages"]

            for page in pages.values():
                if "extract" in page:
                    title = page["title"]
                    summaries[title] = page["extract"]

            while "continue" in data:
                excontinue = data["continue"]["excontinue"]
                params["excontinue"] = excontinue

                data = session.get(url=self.url, params=params).json()
                pages = data["query"]["pages"]

                for page in pages.values():
                    if "extract" in page:
                        title = page["title"]
                        summaries[title] = page["extract"]

        return summaries

    def update_portraits(self, titles):
        if not isinstance(titles, list):
            titles = [titles]
        session = requests.Session()
        step = 50

        for i in range(0, len(titles), step):
            params = {
                "action": "query",
                "prop": "pageimages",
                "format": "json",
                "pithumbsize": 500,
                "titles": "|".join(titles[i : i + step]),
            }
            data = session.get(self.url, params=params).json()
            pages = data["query"]["pages"]

            for page in pages.values():
                if "thumbnail" in page:
                    title = page["title"]
                    self.people_pages[title].image = page["thumbnail"]["source"]

    def _extract_links(self, title):
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

    def _extract_categories(self, titles):
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
