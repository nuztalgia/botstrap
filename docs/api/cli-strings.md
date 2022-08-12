<!-- prettier-ignore -->
::: botstrap.CliStrings
    options:
      members:
        - default
      show_root_full_path: false

<!-- prettier-ignore -->
??? quote "Definition - All default string values"
    {%
      include "../../botstrap/strings.py"
      start='\n\n    """ NOTE:'
      end='"""\n\n    # region FIELDS'
    %}
    ```{.py title="botstrap/strings.py" .line-numbers-off}
    {%
      include "../../botstrap/strings.py"
      start='# region FIELDS'
      end='# endregion FIELDS'
    %}
    ```

<!-- prettier-ignore -->
::: botstrap.CliStrings.compact
    options:
      heading_level: 2
      show_root_full_path: false
