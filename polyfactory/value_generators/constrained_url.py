from polyfactory.field_meta import UrlConstraints


# FIXME: remove the pragma when switching to pydantic v2 permanently
def handle_constrained_url(constraints: UrlConstraints) -> str:  # pragma: no cover
    schema = (constraints.get("allowed_schemes") or ["http", "https"])[0]
    default_host = constraints.get("default_host") or "localhost"
    default_port = constraints.get("default_port") or 80
    default_path = constraints.get("default_path") or ""

    return f"{schema}://{default_host}:{default_port}{default_path}"
