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

uv run bump-my-version bump --new-version "$bumped_version"
