<style>
  /* Hide line numbers in the code block for "Default Strings". */
  details.quote .language-py .linenos { display: none; }
</style>

<!-- prettier-ignore -->
::: botstrap.CliStrings
    options:
      members:
        - compact
        - default
      show_root_full_path: false

<!-- prettier-ignore -->
??? quote "Default Strings"
    {%
      include "../../botstrap/strings.py"
      start='\n\n    """'
      end='"""\n\n    # region ATTRIBUTE DEFINITIONS'
    %}
    ```py title="botstrap/strings.py"
    {%
      include "../../botstrap/strings.py"
      start='# region ATTRIBUTE DEFINITIONS'
      end='# endregion ATTRIBUTE DEFINITIONS'
    %}
    ```
