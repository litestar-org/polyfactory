#!/usr/bin/env bash

set -e

bumped_version=$(
	uv run git-cliff \
		-c pyproject.toml \
		--github-token "$(gh auth token)" \
		--bumped-version
)

uv run git-cliff \
	-c pyproject.toml \
	--github-token "$(gh auth token)" \
	--tag "$bumped_version" \
	--output docs/changelog.rst

uvx --with 'click==8.2.2' bump-my-version@1.1.2 bump --new-version "$bumped_version" --allow-dirty
