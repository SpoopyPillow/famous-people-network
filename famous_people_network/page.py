import re
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


class Page:
    def __init__(self, title="", sidebar="", summary=""):
        self.title = title
        self.sidebar = sidebar
        self.summary = summary
        self.image = None
        self.user_added = False

    def __hash__(self):
        return self.title.__hash__()

    def extract_sidebar_links(self):
        return list(set(re.findall(r"\[\[.*?(.*?)[\|\]]", self.sidebar)))

    def extract_sidebar_link_info(self, link):
        return re.findall(r"\n\s*\|\s*(.*?)\s*=.*?\[\[" + link + r"\]\]", self.sidebar)

    def is_person(self):
        # TODO More checks for person
        return re.search(r"\| birth_date", self.sidebar) is not None
