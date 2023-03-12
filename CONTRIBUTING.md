# Contributing

This package is open to contributions big and small.

To contribute, please follow these steps:

1. [Fork](https://github.com/starlite-api/pydantic-factories/fork) the upstream repository and clone the fork locally.
2. Install [poetry](https://python-poetry.org/), and install the project's dependencies with `poetry install`.
3. Install [pre-commit](https://pre-commit.com/) by running `pre-commit install`.
4. Make whatever changes and additions you wish and commit these - please try to keep your commit history clean.
   1. > **NOTE**: 100% tests are mandatory.
5. Once you are ready, add a PR in the main repo.
6. Create a pull request to the main repository with an explanation of your changes.

**NOTE**: The test suite requires having an instance of MongoDB available. You can launch one using the root level
docker-compose config with `docker-compose up --detach`, or by any other means you deem.

## Launching the Docs

To launch the docs locally use docker. First pull the image for the [mkdocs material theme](https://squidfunk.github.io/mkdocs-material/getting-started/) with:

```shell
docker pull squidfunk/mkdocs-material
```

And then launch the docs with:

```shell
docker run --rm -it -p 8000:8000 -v ${PWD}:/docs squidfunk/mkdocs-material
```

## Release workflow (Maintainers only)

1. Update changelog.md
2. Increment the version in [pyproject.toml](pyproject.toml)
3. Commit and push.
4. In GitHub go to the [releases tab](https://github.com/starlite-api/pydantic-factories/releases)
5. Pick "[draft a new release](https://github.com/starlite-api/pydantic-factories/releases/new)"
6. Give it a title and a tag, both `vX.X.X`
7. Fill in the release description, you can let GitHub do it for you and then edit as needed.
8. Publish the release.
9. Look under the action pane and make sure the release action runs correctly
