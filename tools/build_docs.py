from __future__ import annotations

import argparse
import shutil
import subprocess
from contextlib import contextmanager
from pathlib import Path

REDIRECT_TEMPLATE = """
<!DOCTYPE HTML>
<html lang="en-US">
    <head>
        <title>Page Redirection</title>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="0; url={target}">
        <script type="text/javascript">window.location.href = "{target}"</script>
    </head>
    <body>
        You are being redirected. If this does not work, click <a href='{target}'>this link</a>
    </body>
</html>
"""

parser = argparse.ArgumentParser()
parser.add_argument("output")


@contextmanager
def checkout(branch: str) -> None:
    subprocess.run(["git", "checkout", branch], check=True)  # noqa: S603 S607
    yield
    subprocess.run(["git", "checkout", "-"], check=True)  # noqa: S603 S607


def build(output_dir: str) -> None:
    subprocess.run(["make", "docs"], check=True)  # noqa: S603 S607

    output_dir = Path(output_dir)
    output_dir.mkdir()
    output_dir.joinpath(".nojekyll").touch(exist_ok=True)
    output_dir.joinpath("index.html").write_text(REDIRECT_TEMPLATE.format(target="latest"))

    docs_src_path = Path("docs/_build/html")
    shutil.copytree(docs_src_path, output_dir / "latest", dirs_exist_ok=True)


def main() -> None:
    args = parser.parse_args()
    build(output_dir=args.output)


if __name__ == "__main__":
    main()
