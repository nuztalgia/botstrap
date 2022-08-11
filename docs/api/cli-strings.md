<!-- prettier-ignore -->
::: botstrap.CliStrings
    options:
      members:
        - compact
        - default
      show_root_full_path: false

<!-- prettier-ignore -->
??? quote "Default Attribute Values"
    {%
      include "../../botstrap/strings.py"
      start='\n\n    """'
      end='"""\n\n    # region ATTRIBUTE DEFINITIONS'
    %}
    ```py title="botstrap/strings.py" linenums="89"
    {%
      include "../../botstrap/strings.py"
      start='# region ATTRIBUTE DEFINITIONS'
      end='# endregion ATTRIBUTE DEFINITIONS'
    %}
    ```
