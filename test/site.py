from html.parser import HTMLParser
from pathlib import Path
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
TALK_URL = "https://ingydotnet.github.io/oss-eu-yaml-talk/"
CONTACT_URLS = {
    "mailto:ingy@ingy.net",
    "https://github.com/ingydotnet",
    "https://www.linkedin.com/in/ingydotnet",
    "https://matrix.to/#/@ingy:yaml.io",
    "https://bsky.app/profile/ingydotnet.bsky.social",
    "https://cloud-native.slack.com/team/U08GBQNJTFC",
    "https://discord.gg/hJ7UkFbYVS",
}


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()
        self.image_alts = []
        self.slide_count = 0
        self.button_labels = set()
        self.project_menus = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "a" and "href" in attributes:
            self.links.add(attributes["href"])
        if tag == "img":
            self.image_alts.append(attributes.get("alt"))
        if tag == "figure" and "data-slide" in attributes:
            self.slide_count += 1
        if tag == "button" and attributes.get("aria-label"):
            self.button_labels.add(attributes["aria-label"])
        if tag == "details" and "data-project-menu" in attributes:
            self.project_menus += 1


def load_yaml(name):
    return yaml.safe_load((ROOT / name).read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    html_path = SITE / "index.html"
    require(html_path.is_file(), "site/index.html was not generated")

    parser = SiteParser()
    parser.feed(html_path.read_text(encoding="utf-8"))
    projects = load_yaml("projects.yaml")
    photos = load_yaml("photos.yaml")

    for project in projects:
        require(
            project["url"] in parser.links,
            f"missing project link: {project['url']}",
        )
    require(parser.project_menus == 1, "expected one project menu")

    require(parser.slide_count == len(photos), "photo count does not match")
    for photo in photos:
        require(
            photo["alt"] in parser.image_alts,
            f"missing alt: {photo['alt']}",
        )

    require(TALK_URL in parser.links, "missing talk slides link")
    require(CONTACT_URLS <= parser.links, "missing one or more contact links")
    require(
        {
            "Previous photo",
            "Next photo",
            "Pause slideshow",
            "Hide introduction",
        }
        <= parser.button_labels,
        "missing hero controls",
    )

    cname = (SITE / "CNAME").read_text(encoding="utf-8").strip()
    require(cname == "ingy.net", "generated CNAME is incorrect")
    require((SITE / "yaml-future.html").exists() is False,
            "legacy pages should not enter generated output")

    print("Site smoke tests passed")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as error:
        print(f"Site smoke test failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
