---
hide:
  - footer
---

# Getting Started

## Installation

Botstrap is published as a package on [PyPI][1] and can be easily installed using `pip`:

```{.text .line-numbers-off title=""}
pip install -U botstrap
```

This will also automatically install compatible versions of Botstrap's dependencies
([`colorama`][2] and [`cryptography`][3]), so there's no need to install those packages
separately.

??? info "Info - Python requirements"

    Botstrap requires a recent version of [Python][4] as well as the Python package
    manager, [`pip`][5], to be installed on your system. You can check your
    currently-installed versions from the command line:

    ```console title=""
    $ python --version
    Python 3.10.7
    ```

    ```console title=""
    $ pip --version
    pip 22.2.2 from /usr/local/lib/python3.10/site-packages/pip (python 3.10)
    ```

    For reference, Botstrap supports Python versions
    [![](https://img.shields.io/pypi/pyversions/botstrap?color=7e56c2&label="")][1]
    and the latest `pip` version is
    [![](https://img.shields.io/pypi/v/pip?color=7e56c2&label="")][6].

??? note "Note - Installing from source"

    Botstrap can alternatively be installed from GitHub by cloning its [repository][7].
    This might be of interest if you want to use the very latest snapshot, or if you
    want to play with the code (and maybe make a [contribution][8]). :purple_heart:

    To create a development installation of Botstrap in your current environment, use
    the following commands:

    ```console title=""
    $ git clone https://github.com/nuztalgia/botstrap.git
    ```

    ```{.console title="" .annotate}
    $ pip install -e botstrap # (1)
    ```

    1. Using the `-e` flag produces an [editable][9] installation.

[1]: https://pypi.org/project/botstrap/
[2]: https://pypi.org/project/colorama/
[3]: https://pypi.org/project/cryptography/
[4]: https://www.python.org/downloads/
[5]: https://pip.pypa.io/en/stable/installation/
[6]: https://pypi.org/project/pip/
[7]: https://github.com/nuztalgia/botstrap
[8]: https://github.com/nuztalgia/botstrap/blob/main/.github/CONTRIBUTING.md
[9]: https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs

<link rel="stylesheet" href="../stylesheets/getting-started.css" />
