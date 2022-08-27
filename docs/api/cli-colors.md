## CliColors {#}

<!-- prettier-ignore -->
::: botstrap.CliColors
    options:
      heading_level: 1
      members:
        - default

??? note sourcedefs "Note - All default color values"

    ```{.py title="botstrap/colors.py" .annotate .line-numbers-off}
    {%
      include "../../botstrap/colors.py"
      start=':\n        ```\n    """\n\n'
      end='\n\n    @classmethod\n    def default'
    %}
    ```

    1.  This "field" is just a sentinel value for
        [`dataclasses`](https://docs.python.org/3/library/dataclasses.html#dataclasses.KW_ONLY).
        - Any fields **after** a pseudo-field with the type of `KW_ONLY` are marked
          as **keyword-only fields**.
        - These fields signify `#!py __init__()` parameters that must be specified
          as keywords when the class is instantiated.

::: botstrap.CliColors.off

<link rel="stylesheet" href="../stylesheets/cli-colors.css" />
<link rel="stylesheet" href="../../stylesheets/code-navigation.css" />
