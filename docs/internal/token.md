::: botstrap.internal.Token
    options:
      heading_level: 1
      members: false

??? abstract hide-on-small-screens "Diagram - Class Relationships & Structure"

    <figure markdown>
      ```mermaid
      classDiagram
          direction BT
          class Token {
              cli: CliSession
              resolve(allow_token_creation)
          }
          class Botstrap {
              _tokens_by_uid: dict[str, Token]
              _active_token: Token | None
              register_token(...)
              parse_args(...)
              retrieve_active_token(...)
              run_bot(...)
          }
          class Secret {
              uid: str
              requires_password: bool
              display_name: str
              storage_directory: Path
              file_path: Path
              min_pw_length: int
              clear()
              read(password)
              validate(data)
              write(data, password)
          }
          class CliSession {
              name: str
              colors: CliColors
              strings: CliStrings
              confirm_or_exit(...)
              exit_process(...)
              get_bool_input(...)
              get_hidden_input(...)
              get_input(...)
              print_prefixed(...)
          }

          Token --|> Secret : inheritance
          Token "*" ..* "1" Botstrap : composition
          Botstrap --|> CliSession : inheritance
          CliSession "1" ..o "*" Token : aggregation

          link Token "#"
          link Botstrap "../../api/botstrap/"
          link CliSession "../cli-session/"
          link Secret "../secret/"
      ```
    </figure>

::: botstrap.internal.Token.__init__
    options:
      show_signature_annotations: false

::: botstrap.internal.Token.get_default

::: botstrap.internal.Token.resolve
    options:
      show_source: true
