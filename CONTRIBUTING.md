# Contributing

This package is open to contributions big and small.

To contribute, please follow these steps:

1. Fork the upstream repository and clone the fork locally.
2. Install [poetry](https://python-poetry.org/), and install the project's dependencies with `poetry install`.
3. Install [pre-commit](https://pre-commit.com/) by running `pre-commit install`.
4. Make whatever changes and additions you wish and commit these - please try to keep your commit history clean.
5. Note: 100% tests are mandatory.
6. Once you are ready, add a PR in the main repo.
7. Create a pull request to the main repository with an explanation of your changes.

**NOTE**: The test suite requires having an instance of MongoDB available. You can launch one using the root level
docker-compose config with `docker-compose up --detach`, or by any other means you deem.

## Lunching the Docs

To lunch the docs locally use docker. First pull the image for the [mkdocs material theme](https://squidfunk.github.io/mkdocs-material/getting-started/) with:

```shell
docker pull squidfunk/mkdocs-material
```

And then lunch the docs with:

```shell
docker run --rm -it -p 8000:8000 -v ${PWD}:/docs squidfunk/mkdocs-material
```
