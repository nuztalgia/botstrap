<!-- prettier-ignore -->
::: botstrap.CliStrings
    options:
      heading_level: 1
      members:
        - default

??? note "Note - All default string values"

    {%
      include "../../botstrap/strings.py"
      start='\n\n    """\n    NOTE:'
      end='"""\n\n    # region FIELDS'
    %}

    === "Dynamic Table"
        | Group | Name | Type  | Default Value |
        | ----- | ---- | ----- | ------------- |
        | Will  |  be  | added |  dynamically. |

    === "Source Code"
        ```{.py title="botstrap/strings.py" .line-numbers-off}
        {%
          include "../../botstrap/strings.py"
          start='# region FIELDS'
          end='# endregion FIELDS'
        %}
        ```

::: botstrap.CliStrings.compact

<link rel="stylesheet" href="../../stylesheets/cli-strings.css" />
