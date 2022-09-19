---
hide:
  - footer
---

# Getting Started

## Requirements

Botstrap requires a recent version of [Python][1] as well as the Python package manager,
[`pip`][2], to be installed on your system.

You can check your currently-installed versions from the command line:

```console title=""
$ python -V
Python 3.10.7
$ pip -V
pip 22.2.2 from /usr/local/lib/python3.10/site-packages/pip (python 3.10)
```

For reference, Botstrap supports Python versions
[![Python Version](https://img.shields.io/pypi/pyversions/botstrap?color=7e56c2&label="")][3]
and the latest `pip` version is
[![Pip Version](https://img.shields.io/pypi/v/pip?color=7e56c2&label="")][4].

## Installation

Botstrap is published as a package on [PyPI][3] and can therefore be easily installed
using `pip`:

```console title=""
$ pip install -U botstrap
```

This will also automatically install compatible versions of Botstrap's dependencies
([`colorama`][5] and [`cryptography`][6]), so there's no need to install those packages
separately.

<!-- prettier-ignore -->
??? note "Note - Installing from source"
    Botstrap can alternatively be installed from GitHub by cloning its [repository][7].
    This might be of interest if you want to use its very latest snapshot, or if you
    want to hack on it (and maybe make a [contribution][8] to its code). :purple_heart:

    To create a development installation of Botstrap in your current environment, use
    the following commands:

    ```console title=""
    $ git clone https://github.com/nuztalgia/botstrap.git
    ```

    ```{.console title="" .annotate}
    $ pip install -e botstrap # (1)
    ```

    1. Using the `-e` flag results in an [editable][9] installation.

[1]: https://www.python.org/downloads/
[2]: https://pip.pypa.io/en/stable/installation/
[3]: https://pypi.org/project/botstrap/
[4]: https://pypi.org/project/pip/
[5]: https://pypi.org/project/colorama/
[6]: https://pypi.org/project/cryptography/
[7]: https://github.com/nuztalgia/botstrap
[8]: https://github.com/nuztalgia/botstrap/blob/main/.github/CONTRIBUTING.md
[9]: https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs

<link rel="stylesheet" href="../stylesheets/getting-started.css" />
