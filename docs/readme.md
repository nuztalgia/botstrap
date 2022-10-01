# <a href="https://botstrap.rtfd.io"><img src="/docs/images/logo-48.png" width=24></a> Documentation

To view the Botstrap documentation, head on over to the
[official site](https://botstrap.readthedocs.io/)! It's much more informative than the
raw source files contained here.

If you have a question that isn't answered in the docs and you think it should be,
please start a [discussion](https://github.com/nuztalgia/botstrap/discussions) on what
could be clarified and/or improved! Our goal is to make this library as easy-to-use as
possible, so all feedback is welcome and appreciated. :sparkling_heart:

The rest of this file contains information about building the **documentation site**
from the source files in this directory.

<table>
<tr><th>Table of Contents</th></tr>
<tr><td><p>

1. [Configuration & Requirements](#configuration--requirements)
   - [Setting up a virtual environment](#setting-up-a-virtual-environment)&emsp;
2. [Installing/Updating Dependencies](#installingupdating-dependencies)
   - [Installing all requirements](#installing-all-requirements)
   - [Updating `requirements.txt`](#updating-requirementstxt)
3. [Building & Previewing the Site](#building--previewing-the-site)
   - [For general development](#for-general-development)
   - [For one-off builds](#for-one-off-builds)
4. [Miscellaneous Questions](#miscellaneous-questions)

</p></td></tr>
</table>

## Configuration & Requirements

Botstrap's documentation is built using [MkDocs](https://www.mkdocs.org/), a
super-extensible static site generator that turns Markdown files into HTML pages. MkDocs
uses a YAML configuration file in the root project directory named
[`mkdocs.yml`](../mkdocs.yml). This file contains the config for the entire
documentation site, including its **theme** (the amazing
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)), **plugins** (most
notably [mkdocstrings](https://mkdocstrings.github.io/)), and **extensions** (almost all
[PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/)).

<details>
<summary>All of these major dependencies, as well as some more minor (but still direct) dependencies,
are pinned and listed in <a href="requirements.in"><code>requirements.in</code></a>.</summary><br>

| Dependency           | PyPI Version                                                                                                                      | GitHub Activity                                                                                                                                          |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mkdocs`             | [![PyPI](https://img.shields.io/pypi/v/mkdocs)](https://pypi.org/project/mkdocs/)                                                 | [![GitHub](https://img.shields.io/github/last-commit/mkdocs/mkdocs)](https://github.com/mkdocs/mkdocs)                                                   |
| `mkdocs-material`    | [![PyPI](https://img.shields.io/pypi/v/mkdocs-material)](https://pypi.org/project/mkdocs-material/)                               | [![GitHub](https://img.shields.io/github/last-commit/squidfunk/mkdocs-material)](https://github.com/squidfunk/mkdocs-material)                           |
| `mkdocstrings`       | [![PyPI](https://img.shields.io/pypi/v/mkdocstrings)](https://pypi.org/project/mkdocstrings/)                                     | [![GitHub](https://img.shields.io/github/last-commit/mkdocstrings/mkdocstrings)](https://github.com/mkdocstrings/mkdocstrings)                           |
| `pymdown-extensions` | [![PyPI](https://img.shields.io/pypi/v/pymdown-extensions)](https://pypi.org/project/pymdown-extensions/)                         | [![GitHub](https://img.shields.io/github/last-commit/facelessuser/pymdown-extensions)](https://github.com/facelessuser/pymdown-extensions)               |
| `include-markdown`   | [![PyPI](https://img.shields.io/pypi/v/mkdocs-include-markdown-plugin)](https://pypi.org/project/mkdocs-include-markdown-plugin/) | [![GitHub](https://img.shields.io/github/last-commit/mondeja/mkdocs-include-markdown-plugin)](https://github.com/mondeja/mkdocs-include-markdown-plugin) |
| `pygments`           | [![PyPI](https://img.shields.io/pypi/v/pygments)](https://pypi.org/project/pygments/)                                             | [![GitHub](https://img.shields.io/github/last-commit/pygments/pygments)](https://github.com/pygments/pygments)                                           |
| `mkdocs-exclude`     | [![PyPI](https://img.shields.io/pypi/v/mkdocs-exclude)](https://pypi.org/project/mkdocs-exclude/)                                 | [![GitHub](https://img.shields.io/github/last-commit/apenwarr/mkdocs-exclude)](https://github.com/apenwarr/mkdocs-exclude)                               |

</details>

In order to make sure the site is built consistently and deterministically, we'll use
[`pip-tools`](https://pip-tools.readthedocs.io/) inside a
[virtual environment](https://docs.python.org/3/tutorial/venv.html). This allows us to
install the exact versions of all of the dependencies required to build this
documentation, without conflicting with any other projects or apps.

### Setting up a virtual environment

1. From this project's [root directory](/../../), run `python -m venv docs/venv` to
   create a new virtual env just for docs.

2. Activate the virtual environment. The command for this step differs depending on your
   OS:

   - On Unix or MacOS, run `source docs/venv/bin/activate`.
   - <details><summary>On Windows, run <code>docs\venv\Scripts\activate</code>.
     </summary>If you're in PowerShell and encounter a security error, run
     <a href="https://go.microsoft.com/fwlink/?LinkID=135170"><code>
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser</code></a>
     and confirm your choice, then try the activation command again.</details>

3. Verify that `(venv)` appears somewhere in your shell's prompt, then run
   `pip install pip-tools`.

The rest of this file assumes that you’ve activated your `docs/venv` virtual environment
and that `pip-tools` is installed correctly. To exit the virtual environment when you're
done building/previewing the site, simply run `deactivate`.

## Installing/Updating Dependencies

As mentioned above, the documentation site's direct dependencies can be found in
[`requirements.in`](requirements.in). Each one is pinned to a specific version, which
will (most of the time) be its latest stable release, thanks to
[Renovate](https://github.com/renovatebot/renovate). However, this setup is not quite
immune to problems:

- An automatic, unchecked update to a dependency might introduce a change that breaks
  something on the documentation site.
- Transitive dependencies are not specified, which might result in inconsistencies when
  building the site across different environments.

To mitigate these potential issues, we use
[`pip-compile`](https://pip-tools.readthedocs.io/en/latest/#example-usage-for-pip-compile)
to generate the [`requirements.txt`](requirements.txt) file with a complete list of all
direct **and** transitive dependencies, along with their respective pinned versions and
[hashes](https://pip.pypa.io/en/stable/topics/secure-installs/#hash-checking-mode) in
order to ensure correctness. This file is therefore the "canonical" set of requirements
for properly building the documentation - both locally for development and on
[Read the Docs](https://readthedocs.org/), which hosts the
[official site](https://botstrap.readthedocs.io/).

All of the following commands assume that you're in the root project directory and that
you've set up your virtual env [as described above](#setting-up-a-virtual-environment).

### Installing all requirements

```
pip-sync docs/requirements.txt
```

Note that this command behaves similarly to `pip install -r docs/requirements.txt`, but
will stop with an error if it's run from outside a virtual environment. This acts as a
convenient fail-safe to help you avoid accidentally cluttering or overwriting your
system-wide package installs. It will also uninstall any packages that **aren't** listed
in the specified file, to ensure that the official set of requirements is both complete
and minimal.

### Updating `requirements.txt`

```
pip-compile --generate-hashes docs/requirements.in
```

In general, this command will be sufficient to properly update `requirements.txt` based
on the current contents of `requirements.in`. However, after doing so, there are a few
things to double-check and adjust if necessary:

- Re-run `pip-sync docs/requirements.txt` to ensure that the packages installed in your
  virtual env match the newly specified versions.

- When any dependency releases a significant update, it's often a good idea to re-build
  and preview the site to see if any breaking changes were introduced. If so, the
  corresponding update to `requirements.txt` should be deferred until a fix or
  workaround is implemented.

- If you're on Windows, the line endings produced by `pip-compile` may be incorrect.
  This should be caught and automatically fixed by the
  [`mixed-line-ending`](https://github.com/pre-commit/pre-commit-hooks#mixed-line-ending)
  [pre-commit](https://pre-commit.com/) hook. Alternatively, you may install
  jazzband/pip-tools#1584, which implements `--force-lf-newlines`.

## Building & Previewing the Site

[MkDocs](https://www.mkdocs.org/getting-started/#creating-a-new-project) provides a
built-in live preview server that makes the documentation site locally available in your
web browser. In general, this server should be used to make and test any changes before
they're [deployed](https://readthedocs.org/projects/botstrap/). Because this repository
is automatically integrated into
[Read the Docs](https://docs.readthedocs.io/en/stable/integrations.html), the
redeployment process will be triggered whenever any documentation-related changes are
pushed to the `main` branch.

### For general development

```
mkdocs serve
```

This command will start the local dev server. While it's running, open up
http://127.0.0.1:8000/ in your browser and you should see your copy of the documentation
site, which will be automatically rebuilt and reloaded whenever a change is made (and
saved) to a relevant file.

If it's taking an undesirably long time to rebuild the entire site after each change,
you may opt to use
[`--dirtyreload`](https://www.mkdocs.org/about/release-notes/#support-for-dirty-builds-990)
mode to speed things up by limiting the scope of the rebuild to only the pages (i.e.
source markdown files) that have been changed since the previous build. However, to
avoid inconsistent behavior in the site navigation and other links, this flag should
only be used while developing content on a specific page.

### For one-off builds

```
mkdocs build
```

Most of the time, this command will only be used by the automated build system on
[Read the Docs](https://readthedocs.org/projects/botstrap/builds/) in order to generate
and serve the official documentation site. In certain cases, however, it may be useful
to invoke this command manually to produce a static local copy of the site. The result
will be saved in the `site` directory, which can be found in the project root (alongside
[`.gitignore`](../.gitignore), where it's already listed).

## Miscellaneous Questions

<ul><li>

<b>Why isn't the name of this file (</b><code>readme.md</code><b>) capitalized?</b>

MkDocs recognizes `index.md` and `README.md` as valid names for
[index pages](https://www.mkdocs.org/user-guide/writing-your-docs/#index-pages). If both
are present, then the `index.md` file is used as the index page and the `README.md` file
is ignored, but a warning is emitted every time the site is built. This project includes
both files, but for different purposes - one is the actual home page of the
documentation site, and the other is this file, for displaying dev info on GitHub.

Fortunately, MkDocs' `README.md` file name detection is case-sensitive (as of version
1.3.1) and GitHub's isn't. This means that this file can be named `readme.md` without
triggering the aforementioned warning, while still being rendered for this directory on
GitHub.

Further reading: mkdocs/mkdocs#608, mkdocs/mkdocs#1580, mkdocs/mkdocs#2846,
sindresorhus/ama#197

</li><li>

<b>Why is this file (and/or the documentation) so overly and unnecessarily detailed?</b>

It was written with love and neurodivergence. :purple_heart: I had to comb through quite
a few different resources to learn these concepts and how to put them all together, so
it's nice to have all the information (including the reasoning behind each step, and
plenty of links) in one place for easy recovery when it's inevitably and inexplicably
wiped from my memory. Hopefully it can be helpful to you too! &ensp;&ndash;
[@nuztalgia](https://github.com/nuztalgia)

</li></ul>
