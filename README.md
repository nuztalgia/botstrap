<div align="center">

[![Botstrap Logo](https://raw.githubusercontent.com/nuztalgia/botstrap/main/docs/images/logo-192.png)](https://botstrap.readthedocs.io)

# Botstrap

[![Development Status](https://img.shields.io/pypi/status/botstrap)](https://pypi.org/project/botstrap/)
[![Latest Version](https://img.shields.io/pypi/v/botstrap?label=latest%20version)](https://pypi.org/project/botstrap/)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/botstrap)](https://pypi.org/project/botstrap/)
<br>
[![Tests](https://github.com/nuztalgia/botstrap/actions/workflows/tests.yml/badge.svg)](https://github.com/nuztalgia/botstrap/actions/workflows/tests.yml)
[![Docs](https://img.shields.io/readthedocs/botstrap?logo=read-the-docs&logoColor=9fa6ae&label=Docs&labelColor=313a43)](https://readthedocs.org/projects/botstrap)
[![CodeQL](https://github.com/nuztalgia/botstrap/actions/workflows/codeql.yml/badge.svg)](https://github.com/nuztalgia/botstrap/actions/workflows/codeql.yml)
<br>
[![Codacy](https://img.shields.io/codacy/grade/6864639715f04899b62d3a4460eba83e?logo=codacy)](https://app.codacy.com/gh/nuztalgia/botstrap)
[![Codecov](https://img.shields.io/codecov/c/github/nuztalgia/botstrap?logo=codecov&logoColor=fff)](https://app.codecov.io/github/nuztalgia/botstrap)
[![Libraries.io](https://img.shields.io/librariesio/github/nuztalgia/botstrap?logo=librariesdotio&logoColor=ddd&logoWidth=12&label=deps)](https://libraries.io/github/nuztalgia/botstrap)

An easy-to-use utility toolbelt for Discord bots written in Python.<br>
[**Read the docs »**](https://botstrap.readthedocs.io)

</div>

## Overview

Do you store your Discord bot token in
[plaintext](https://en.wikipedia.org/wiki/Plaintext)? Don't get caught with your pants
down. Strap in!

**Botstrap** is a ~~Python library~~ suit of power armor that perfectly fits your
Discord bot. It offers:

- 🔐 **Secure encryption** and password protection to keep your bot tokens safe
- 🤹 A straightforward way to **manage multiple tokens** and/or bot configurations
- 🌈 An intuitive, colorful, and customizable **command-line interface** for your bot
- 🤝 Out-of-the-box **compatibility** with all of the most popular Python
  [Discord libraries](https://github.com/nuztalgia/botstrap/tree/main/examples/libraries)
- ... and more to come!

## Installation

Python **3.10** or higher is required. It's also generally a good idea to upgrade pip
(`python -m pip install -U pip`).

```sh
pip install -U botstrap
```

For additional/alternative installation instructions, see the
[documentation](https://botstrap.readthedocs.io/en/latest/getting-started/#installation).

## Quickstart

Coming soon! In the meantime, check out:

- The [examples](https://github.com/nuztalgia/botstrap/tree/main/examples) directory
- Starter
  [bot templates](https://github.com/nuztalgia/botstrap/tree/main/examples/libraries)
  for various Discord libraries
- **And most importantly:** The extremely detailed
  [Botstrap API Reference](https://botstrap.readthedocs.io/en/latest/api/)

## Git Hooks

Adding one or both of Botstrap's [pre-commit](https://github.com/pre-commit/pre-commit)
hooks to your `git` workflow is an easy and seamless way to improve the security of your
codebase. (If you're unfamiliar with pre-commit, here's its
[quickstart](https://pre-commit.com/index.html#quick-start) guide. Highly recommend!)

See below for descriptions of the available hooks, and add the one(s) you like to your
`.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/nuztalgia/botstrap
  rev: 0.2.7
  hooks:
    - id: detect-discord-bot-tokens
    - id: detect-encrypted-tokens
```

### 🕵️ `detect-discord-bot-tokens`

This hook checks the contents of your added/changed files every time you `git commit`,
and raises an error if it finds any unencrypted bot tokens. It won't catch any plaintext
tokens that you've `.gitignore`-d or already committed, but it _will_ prevent you from
accidentally committing new ones.

**Note:** This hook is especially useful for bots whose tokens aren't secured by the
main Botstrap library - **including bots written in languages other than Python!** ✨

### 💂 `detect-encrypted-tokens`

Although it isn't _quite_ as dangerous to commit your encrypted bot tokens, doing so is
still very much a security risk. This hook prevents that from happening by raising an
error if you try to `git commit` a file whose name matches the pattern used by
Botstrap's encrypted token files. (**Hint:** Keep this hook happy by adding `*.key` to
your `.gitignore`.)

## Badges

Let everyone know your Discord bot is secure by adding a badge to your repository's
`README.md`:

[![Botstrap: On](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnuztalgia%2Fbotstrap%2Fmain%2F.github%2Fbadges%2Fbotstrap-on.json)](https://github.com/nuztalgia/botstrap)
[![Botstrap: Enabled](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnuztalgia%2Fbotstrap%2Fmain%2F.github%2Fbadges%2Fbotstrap-enabled.json)](https://github.com/nuztalgia/botstrap)
[![Tokens: Encrypted](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnuztalgia%2Fbotstrap%2Fmain%2F.github%2Fbadges%2Ftokens-encrypted.json)](https://github.com/nuztalgia/botstrap)
[![Tokens: Secure](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnuztalgia%2Fbotstrap%2Fmain%2F.github%2Fbadges%2Ftokens-secure.json)](https://github.com/nuztalgia/botstrap)
[![Botstrap](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnuztalgia%2Fbotstrap%2Fmain%2F.github%2Fbadges%2Fbotstrap.json)](https://github.com/nuztalgia/botstrap)

```
[![Botstrap](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnuztalgia%2Fbotstrap%2Fmain%2F.github%2Fbadges%2Fbotstrap-on.json)](https://github.com/nuztalgia/botstrap)
```

You can replace `botstrap-on` in the above snippet with the text on one of the other
badges (e.g. `tokens-secure`).

For more granular customization options, check out the available style parameters on
[shields.io](https://shields.io/#styles).

## License

Copyright © 2022 [Nuztalgia](https://github.com/nuztalgia). Released under the
[Apache License, Version 2.0](https://github.com/nuztalgia/botstrap/blob/main/LICENSE).
