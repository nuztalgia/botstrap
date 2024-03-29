<h1>
<picture>
<img alt="Botstrap Logo" src="../docs/images/logo-48.png" width=32>
</picture>
Testing
</h1>

<table>
<tr><th colspan=2>CI Status</th></tr>
<tr align="center"><td>
<a href="https://github.com/nuztalgia/botstrap/actions/workflows/tests.yml"><img src="https://img.shields.io/github/actions/workflow/status/nuztalgia/botstrap/tests.yml?branch=main&style=for-the-badge&logo=github&label=tests"></a>
</td><td>
<a href="https://app.codecov.io/github/nuztalgia/botstrap"><img src="https://img.shields.io/codecov/c/github/nuztalgia/botstrap?style=for-the-badge&logo=codecov&logoColor=fff"></a>
</td></tr>
</table>

## Tools & Configuration

Botstrap's unit tests are written and run using [`pytest`], with coverage reports
produced by [`pytest-cov`]. These tools are configured as follows:

[`pytest`]: https://pypi.org/project/pytest/
[`pytest-cov`]: https://pypi.org/project/pytest-cov/

<ul>
<li><details><summary>
Default <a href="https://docs.pytest.org/en/7.1.x/reference/reference.html#ini-options-ref"><b>pytest
options</b></a> are specified in <a href="/pyproject.toml"><code>pyproject.toml</code></a>.</summary>

https://github.com/nuztalgia/botstrap/blob/d08cefd21cd95e357ecd9cabc169715fec901216/pyproject.toml#L50-L61

</details></li>
<li><details><summary>
The <a href="https://pytest-cov.readthedocs.io/en/latest/config.html"><b>pytest-cov
config</b></a> lives in <a href="./.coverage.ini"><code>tests/.coverage.ini</code></a>.
</summary>

https://github.com/nuztalgia/botstrap/blob/d08cefd21cd95e357ecd9cabc169715fec901216/tests/.coverage.ini#L1-L12

More details about the contents of this config file can be found in the [documentation]
for [`coverage.py`], which powers `pytest-cov`.

[documentation]: https://coverage.readthedocs.io/en/latest/config.html
[`coverage.py`]: https://pypi.org/project/coverage/

</details>
</ul>

Whenever a commit that affects [`botstrap`](/botstrap) and/or [`tests`](.) is pushed to
the `main` branch, the [Tests] workflow will automatically run `pytest` on an assortment
of operating systems and supported Python versions. If all tests pass, the resulting
coverage report will be uploaded to [Codecov].

[tests]: https://github.com/nuztalgia/botstrap/actions/workflows/tests.yml
[codecov]: https://app.codecov.io/github/nuztalgia/botstrap

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

Then, use the following command to run the tests:

```
pytest
```

And that's it! Hopefully all the tests pass. :innocent:

## Useful `pytest` Options

Use `-S` to skip slow tests. This is a custom option defined in
[`conftest.py`](./conftest.py). It causes `pytest` to ignore tests that are explicitly
marked as slow.

```
pytest -S
```

Use `-k` to only run tests whose names (or module names) match a given pattern. This can
greatly speed up the workflow of writing, running, and/or fixing tests for a specific
module or feature.

```
pytest -k test_modulename
```

Use `--cov` to see a coverage summary for the tests currently being run. (**Note:**
Combining this option with options that skip tests, such as `-S`, will result in an
incomplete coverage report and is usually not recommended.)

```
pytest --cov
```

Use `--durations=N` to see the slowest `N` tests. (**Note:** Any tests that take longer
than `0.01s` to run should be marked with `@pytest.mark.slow` so that they can be
conveniently skipped with the `-S` option.)

```
pytest --durations=50
```

For more information about `pytest` and its available options, check out the [usage
guide] (and, of course, `pytest -h`).

[usage guide]: https://docs.pytest.org/en/latest/how-to/usage.html
