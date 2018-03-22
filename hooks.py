from pathlib import Path
from urllib.parse import urlparse

import yaml
from mkdocs.exceptions import ConfigurationError


ROOT = Path(__file__).resolve().parent


def _load_yaml(name):
    path = ROOT / name
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise ConfigurationError(f"Cannot load {name}: {error}") from error

    if not isinstance(data, list) or not data:
        raise ConfigurationError(f"{name} must contain a non-empty sequence")
    return data


def _validate_fields(item, name, index, required, optional=()):
    if not isinstance(item, dict):
        raise ConfigurationError(f"{name} item {index} must be a mapping")

    allowed = set(required) | set(optional)
    missing = set(required) - set(item)
    unknown = set(item) - allowed
    if missing:
        fields = ", ".join(sorted(missing))
        raise ConfigurationError(f"{name} item {index} is missing {fields}")
    if unknown:
        fields = ", ".join(sorted(unknown))
        raise ConfigurationError(f"{name} item {index} has unknown {fields}")

    for field in required:
        if not isinstance(item[field], str) or not item[field].strip():
            raise ConfigurationError(
                f"{name} item {index} field {field} must be text"
            )


def _load_projects():
    projects = _load_yaml("projects.yaml")
    names = set()
    urls = set()

    for index, project in enumerate(projects, start=1):
        _validate_fields(project, "projects.yaml", index, ("name", "url"))
        parsed = urlparse(project["url"])
        if parsed.scheme != "https" or not parsed.netloc:
            raise ConfigurationError(
                f"projects.yaml item {index} url must be an HTTPS URL"
            )
        if project["name"] in names or project["url"] in urls:
            raise ConfigurationError(
                f"projects.yaml item {index} duplicates an earlier project"
            )
        names.add(project["name"])
        urls.add(project["url"])

    return projects


def _load_photos(config):
    photos = _load_yaml("photos.yaml")
    docs_dir = Path(config["docs_dir"]).resolve()

    for index, photo in enumerate(photos, start=1):
        _validate_fields(
            photo,
            "photos.yaml",
            index,
            ("src", "alt"),
            ("position",),
        )
        source = (docs_dir / photo["src"]).resolve()
        try:
            source.relative_to(docs_dir)
        except ValueError as error:
            raise ConfigurationError(
                f"photos.yaml item {index} src must stay under src/"
            ) from error
        if not source.is_file():
            raise ConfigurationError(
                f"photos.yaml item {index} does not exist: {photo['src']}"
            )
        position = photo.get("position")
        if position is not None and not isinstance(position, str):
            raise ConfigurationError(
                f"photos.yaml item {index} position must be text"
            )

    return photos


def on_config(config, **kwargs):
    extra = config.get("extra") or {}
    extra["projects"] = _load_projects()
    extra["photos"] = _load_photos(config)
    config["extra"] = extra
    return config
