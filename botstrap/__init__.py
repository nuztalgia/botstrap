"""This package exports the classes that make up Botstrap's public API.

* [`Botstrap`](botstrap)
* [`Color`](color)
* [`Strings`](strings)
* [`ThemeColors`](theme-colors)

For more details, see the documentation for each class. [Start here.](botstrap)
"""
from botstrap.api import Botstrap
from botstrap.internal import Color, Strings, ThemeColors

__all__ = [
    "Botstrap",
    "Color",
    "Strings",
    "ThemeColors",
]
