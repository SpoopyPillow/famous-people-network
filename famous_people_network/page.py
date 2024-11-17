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
        lines = re.split(r"\n\s*\|\s*", self.sidebar)[1:-1]
        output = set()
        for line in lines:
            output.update(re.findall(r".*?\[\[(.*?)[\|\]]", line))

        return list(output)

    def extract_sidebar_link_info(self, link):
        if isinstance(link, Page):
            link = link.title
        lines = re.split(r"\n\s*\|\s*", self.sidebar)[1:-1]
        infos = []
        for line in lines:
            infos.extend(re.findall(r"(.*?)\s*=.*?\[\[" + link + r"[\|\]]", line))
        return infos

    def is_person(self):
        # TODO More checks for person
        return re.search(r"\n\s*\|\s*birth_date", self.sidebar) is not None
