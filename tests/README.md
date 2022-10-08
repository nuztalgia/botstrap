# <a href="https://botstrap.rtfd.io"><img src="/docs/images/logo-48.png" width=24></a> Testing

<table>
<tr><th colspan=2>CI Status</th></tr>
<tr align="center"><td>
<a href="https://github.com/nuztalgia/botstrap/actions/workflows/tests.yml"><img src="https://img.shields.io/github/workflow/status/nuztalgia/botstrap/Tests?style=for-the-badge&logo=github&label=tests"></a>
</td><td>
<a href="https://app.codecov.io/github/nuztalgia/botstrap"><img src="https://img.shields.io/codecov/c/github/nuztalgia/botstrap?style=for-the-badge&logo=codecov&logoColor=fff"></a>
</td></tr>
</table>

## Tools & Configuration

Botstrap's unit tests are written and run using
[`pytest`](https://pypi.org/project/pytest/), with coverage reports produced by
[`pytest-cov`](https://pypi.org/project/pytest-cov/). These tools are configured as
follows:

<ul>
<li><details><summary>
Default <a href="https://docs.pytest.org/en/7.1.x/reference/reference.html#ini-options-ref"><b>pytest
options</b></a> are specified in <a href="/pyproject.toml"><code>pyproject.toml</code></a>.</summary>

https://github.com/nuztalgia/botstrap/blob/b18a9f23630fb3967d39710dfbe3639dba00b058/pyproject.toml#L50-L60

</details></li>
<li><details><summary>
The <a href="https://pytest-cov.readthedocs.io/en/latest/config.html"><b>pytest-cov
config</b></a> lives in <a href=".coverage.ini"><code>tests/.coverage.ini</code></a>.
</summary>

https://github.com/nuztalgia/botstrap/blob/b18a9f23630fb3967d39710dfbe3639dba00b058/tests/.coverage.ini#L1-L13

More details about the contents of this config file can be found in the
[documentation](https://coverage.readthedocs.io/en/latest/config.html) for
[`coverage.py`](https://pypi.org/project/coverage/), which powers `pytest-cov`.

</details>
</ul>

Whenever a commit that affects [`botstrap`](/botstrap) and/or [`tests`](.) is pushed to
the `main` branch, the
[Tests](https://github.com/nuztalgia/botstrap/actions/workflows/tests.yml) workflow will
automatically run `pytest` on an assortment of operating systems and supported Python
versions. If all tests pass, the resulting coverage report will be uploaded to
[Codecov](https://app.codecov.io/github/nuztalgia/botstrap).

## Running the Tests

If you haven't already done so, clone this repo and navigate to its
[root directory](/../../):

```
git clone https://github.com/nuztalgia/botstrap.git
cd botstrap
```

Make sure you've installed/updated the required packages for testing this project:

```
pip install -U botstrap[tests]
```

Then, use the following command to run the tests and produce a coverage summary:

```
pytest
```

And that's it! Hopefully all the tests pass. :innocent:

## Useful `pytest` Options

Use `-S` to skip slow tests. This is a custom option defined in
[`conftest.py`](conftest.py). It causes pytest to ignore tests that are explicitly
marked as slow.

```
pytest -S
```

Use `-k` to only run tests whose names (or module names) match a given pattern. This can
greatly speed up the workflow of writing, running, and fixing tests for a specific
module or feature. Combine it with `--no-cov` to avoid printing an incomplete coverage
report.

```
pytest -k test_modulename --no-cov
```

Use `--durations=N` to see the slowest `N` tests. (**Note:** Any tests that take longer
than `0.01s` to run should be marked with `@pytest.mark.slow` so that they can be
conveniently skipped with the `-S` option.)

```
pytest --durations=50
```

For more information about **pytest** and its available options, check out the
[usage guide](https://docs.pytest.org/en/latest/how-to/usage.html) (and, of course,
`pytest -h`).
