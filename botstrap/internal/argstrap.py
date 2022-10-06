"""This module contains the `Argstrap` class, which parses arguments for a bot's CLI."""
from __future__ import annotations

import argparse
import operator
import re
from typing import Any, Final, Iterator

from botstrap.internal.clisession import CliSession
from botstrap.internal.metadata import Metadata
from botstrap.internal.tokens import Token
from botstrap.options import Option

# Default/reserved command-line argument names.
_HELP_KEY: Final[str] = "help"
_TOKEN_KEY: Final[str] = "token"
_TOKENS_KEY: Final[str] = "tokens"
_VERSION_KEY: Final[str] = "version"

_HELP_PATTERN: Final[re.Pattern] = re.compile(r"(^|[^%])(%)([^%(]|$)")
_HELP_REPLACEMENT: Final[str] = r"\1\2\2\3"  # Escape the "%" by including it twice.


class Argstrap(argparse.ArgumentParser):
    """Parses command-line args and provides a CLI framework for bots that use Botstrap.

    This class extends [`ArgumentParser`][1] and can operate similarly, but its primary
    purpose is to automatically handle the command-line arguments expected by Botstrap.
    These may be the default options provided out-of-the-box (such as `--help` and
    `--tokens`), or custom ones defined for individual bots with the help of the
    `Option` class.

    The portion of the program flow handled by this class is fairly self-contained -
    its only method that gets called externally, aside from its (quite intricate)
    constructor, is [`parse_bot_args()`][botstrap.internal.Argstrap.parse_bot_args].
    Nevertheless, detailed documentation and source code comments are provided for
    every method, because they all contain logic that is key to how Botstrap operates.

    [1]: https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser
    """

    def __init__(
        self,
        cli: CliSession,
        tokens: list[Token],
        description: str | None = None,
        version: str | None = None,
        **custom_options: Option,
    ) -> None:
        """Initializes a new `Argstrap` instance.

        Args:
            cli:
                A `CliSession` providing the UX used by the CLI.
            tokens:
                The tokens that are defined for the bot.
                Will be used to determine its available command-line args (e.g. if
                multiple tokens are supported, a "token id" arg may be specified to
                select the [active token][botstrap.Botstrap.retrieve_active_token]).
            description:
                A short human-readable description of the bot.
                Will be displayed when the `--help` option is passed to the CLI.
                If omitted, Botstrap will try to fill this field from package
                [metadata][botstrap.internal.Metadata.get_package_info].
                If unsuccessful, this line will be left blank.
            version:
                A string representing the current version of the bot.
                Will be displayed when the `--version` option is specified.
                If omitted, that option will not be present in the bot's CLI.
            **custom_options:
                Keyword args specifying the bot's custom-defined command-line options.
                If omitted, only the default Botstrap options will be available in the
                bot's CLI.
        """
        self.cli: Final[CliSession] = cli
        self._tokens: Final[list[Token]] = tokens
        self._custom_keys: Final[tuple[str, ...]] = tuple(
            custom_key.lower().strip("_") for custom_key in custom_options
        )  # Custom keys are lower-cased and stripped of leading/trailing underscores.

        if not description:  # Try to set it from package metadata, if available.
            summary = Metadata.get_package_info(self.cli.name).get("summary")
            description = summary if isinstance(summary, str) else None
        description = f"  {description.strip()}\n" if description else ""

        # Assemble the pieces to create a well-formatted & informative "-h" description.
        program_command = Metadata.get_program_command(self.cli.name)
        mode_addendum = (is_multi_token := len(self._tokens) > 1) and (
            " " + self.cli.strings.h_desc_mode.substitute(token=self._tokens[0]).strip()
        )
        description += "  " + self.cli.strings.h_desc.substitute(
            program_command=" ".join(program_command), mode_addendum=mode_addendum or ""
        )

        super().__init__(
            prog=(prog := self.cli.colors.primary(program_command[-1])),
            description=description,
            formatter_class=argparse.RawTextHelpFormatter,
            add_help=False,
        )

        usage_components = [prog]  # Will later be joined to form the self.usage field.
        abbreviations = self.assign_arg_abbrs()  # Definitive mapping of keys -> abbrs.

        def add_arg(key: str, positional: bool = False, **kwargs: Any) -> None:
            """Adds the arg (and its abbr) to the arg parser and to usage_components."""
            name = ("" if positional else "--") + key.replace("_", "-")
            abbr = f"-{abbreviations[key]}" if abbreviations.get(key) else ""
            metavar = (
                self.cli.colors.lowlight(str(m)) if (m := kwargs.get("metavar")) else ""
            )

            if len(key) == 1:
                name = ""  # Single-char keys will only have an abbr, prefixed by "-".

            if metavar and (not positional):
                kwargs["metavar"] = "<>"  # Short metavar in "options" section of "-h".

            self.add_argument(*[s for s in (abbr, name) if s], **kwargs)

            if kwargs.get("help") == argparse.SUPPRESS:
                return  # This arg should be invisible - don't add it to usage string.

            if key == _HELP_KEY:  # Special case - don't abbreviate "--help".
                display_name = name
            elif key == _TOKEN_KEY:  # Special case - show metavar instead of name.
                display_name = metavar
            else:
                display_name = (abbr or name) + (f" {metavar}" if metavar else "")

            usage_components.append(f"[{display_name}]")

        # First, add any/all custom-defined (a.k.a. probably the most relevant) options.
        for i, option in enumerate(custom_options.values()):
            option_key = self._custom_keys[i]  # Use the sanitized key.
            if not isinstance(option, Option):
                raise TypeError(
                    f"Invalid type for custom option '{option_key}'. "
                    f"Expected {Option}, but found {type(option)}."
                )
            option_dict: dict[str, Any] = {
                "action": "store_true" if option.flag else "store",
                "help": _HELP_PATTERN.sub(_HELP_REPLACEMENT, option.help or ""),
            }
            if not option.flag:
                option_dict["default"] = (default := option.default)
                option_dict["type"] = (option_type := type(default))
                option_dict["metavar"] = f"<{option_type.__name__}>"
                if choices := option.choices:
                    option_dict["choices"] = (  # Make sure default value is included.
                        choices if (default in choices) else [default, *choices]
                    )
            add_arg(option_key, **option_dict)

        # Then add the default options, in order of their usefulness when viewing "-h".
        add_arg(_TOKENS_KEY, action="store_true", help=self.cli.strings.h_tokens)

        if version:
            version_help = self.cli.strings.h_version
            add_arg(_VERSION_KEY, action="version", version=version, help=version_help)

        add_arg(_HELP_KEY, action="help", help=self.cli.strings.h_help)

        # Finally, add the positional "token id" argument iff there's more than 1 token.
        if is_multi_token:
            joined_uids = self.cli.strings.join_choices(
                token_uids := [token.uid for token in self._tokens],
                conjunction=self.cli.strings.m_conj_and,
            )
            add_arg(
                _TOKEN_KEY,
                positional=True,
                nargs="?",
                choices=token_uids,
                default=token_uids[0],
                help=self.cli.strings.h_token_id.substitute(token_ids=joined_uids),
                metavar="<token id>",
            )

        # Join all the components together to produce the complete usage string.
        self.usage = " ".join(usage_components)

    def assign_arg_abbrs(self) -> dict[str, str | None]:
        """Returns a dictionary mapping arg/option keys to their possible abbreviations.

        This method is called by [`__init__()`][botstrap.internal.Argstrap.__init__] in
        order to determine which command-line arguments are eligible to be abbreviated,
        and what those abbreviations should be. It has no purpose after the constructor
        finishes - at that point, all the available command-line arguments/options
        (and their abbrs) will have been decided and set using the superclass method
        [`add_argument()`][1].

        ??? info "Info - Contents of the resulting dictionary"
            The dictionary returned by this method represents a mapping of arg/option
            keys (i.e. names) to their abbreviations. It has the following properties:

            - Each **key** is the "full name" of a command-line argument or option that
              may later be parsed by this `Argstrap` instance. As is the norm for `dict`
              objects, all keys are unique. The [order][2] in which they are specified
              (all default args/options first, then all custom options) is not relevant
              to the user.

            - The **value** for each key will either be a single-character `str`
              containing the first letter of the argument name, or `None` if a
              higher-[priority](./#abbr-priority) argument starting with the
              same letter was previously added to the `dict`.

            - Values that represent abbreviations (i.e. all of the `str` values)
              are guaranteed to be **unique**.

        ??? note "Note - Determining abbreviation priority"
            <div id="abbr-priority"/>
            Ideally, the command-line arguments/options would all start with different
            letters, and would all be conveniently and intuitively abbreviated.
            Since that won't always be the case, this method reserves letters for
            abbreviations according to the following priority:

            1.  First, `-h` is reserved for the `--help` option. This is an extremely
                common abbreviation for command-line tools, so it is given top priority.

            2.  Then, abbreviations for **custom-defined options** are reserved in the
                same [order][3] in which the keyword arguments were originally passed
                in. For example, with three custom options named `--hoo`, `--bar`, and
                `--baz`, the only resulting new abbreviation would be `-b` for `--bar`.
                -   **Special Case:** Any options with single-character names will be
                    given priority over longer names that would otherwise be able to
                    use that single character as an abbreviation.

            3.  Last, if `-t` and/or `-v` have not been reserved yet, they are assigned
                to `--tokens` and `--version` respectively. These are default options
                provided by Botstrap, so they have lower priority than custom options,
                which tend to be more useful for the bots that define them. For example,
                a bot with a custom `--verbose` option would be able to toggle it with
                `-v`, and would have to use the full name of the `--version` option.

            This procedure ensures that all abbreviations are uniquely assigned, and
            that they are (hopefully) delegated to the most valuable options for each
            individual bot. :four_leaf_clover:

        [1]: https://docs.python.org/3/library/argparse.html#the-add-argument-method
        [2]: https://docs.python.org/3/whatsnew/3.6.html#new-dict-implementation
        [3]: https://peps.python.org/pep-0468/

        Returns:
            A dictionary mapping argument/option names to their possible abbreviations.

        Raises:
            ValueError: If an option key/name is not unique across <u>**all**</u>
                arguments (custom-defined *and* default).
        """
        assigned_options: dict[str, str | None] = {}

        def add_options(
            *keys: str, allow_existing_keys: bool = False, add_abbrs: bool = False
        ) -> None:
            """Adds options to dict. By default, forbids dupe keys and forgoes abbrs."""
            for key in keys:
                if (key in assigned_options) and (not allow_existing_keys):
                    raise ValueError(f"'{key}' is not a unique command-line arg name.")
                elif add_abbrs and ((abbr := key[0]) not in assigned_options.values()):
                    assigned_options[key] = abbr
                else:
                    assigned_options[key] = None

        def select_custom_keys(single_char: bool) -> Iterator[str]:
            """Yields valid keys with length == or > 1, depending on the param value."""
            for key in self._custom_keys:
                if (not key) or (key == "h") or not isinstance(key, str):
                    raise ValueError(f"Invalid command-line argument name: '{key}'.")
                elif (operator.eq if single_char else operator.gt)(len(key), 1):
                    yield key

        # First, assign the keys & abbrs that are strictly reserved by default options.
        add_options(_HELP_KEY, add_abbrs=True)
        add_options(_TOKEN_KEY, _TOKENS_KEY, _VERSION_KEY)

        # Then, try to assign keys and abbreviations for any/all custom-defined options,
        # prioritizing those with names consisting of only a single character.
        add_options(*select_custom_keys(single_char=True), add_abbrs=True)
        add_options(*select_custom_keys(single_char=False), add_abbrs=True)

        # Last, try to add abbrs for the default options that can use them (-t and -v).
        add_options(_TOKENS_KEY, _VERSION_KEY, allow_existing_keys=True, add_abbrs=True)

        return assigned_options

    def parse_bot_args(self) -> tuple[Token, Option.Results]:
        """Parses command-line args and returns the results along with the active token.

        This method relies on [`parse_args()`][1] for most of the heavy lifting to do
        with parsing command-line arguments and switching to the`--help` or `--version`
        paths if those options are detected.
        On its own, it does a similar check for `--tokens`, which triggers a call to
        [`manage_tokens()`][botstrap.internal.Argstrap.manage_tokens].

        If no default options are provided to trigger an alternate program flow, this
        method will select the [active token][botstrap.Botstrap.retrieve_active_token],
        either based on the "token id" argument (if it was specified) or a reasonable
        default. It will package the `Token` along with an `Option.Results` containing
        the parsed values for any custom options that were defined, and return both
        objects together in a `tuple`.

        [1]: https://docs.python.org/3/library/argparse.html#the-parse-args-method

        ??? example "Example - Parsing argument values"
            ```py title="example.py"
            from botstrap import Option
            from botstrap.internal import Argstrap, CliSession, Token

            token, results = Argstrap(
                cli=(cli := CliSession(name="argstrap-example")),
                tokens=[Token(cli, "t_dev"), Token(cli, "t_prod")],
                a_flag=Option(flag=True),
                a_float=Option(default=3.14),
            ).parse_bot_args()

            print(f"Token('{token}'), {results}")
            ```

            ```console title="Console Session"
            $ python example.py
            Token('t_dev'), Results(a_flag=False, a_float=3.14)
            $ python example.py -a
            Token('t_dev'), Results(a_flag=True, a_float=3.14)
            $ python example.py --a-float 0.50
            Token('t_dev'), Results(a_flag=False, a_float=0.5)
            $ python example.py t_prod
            Token('t_prod'), Results(a_flag=False, a_float=3.14)
            $ python example.py -a t_prod --a-float 12345
            Token('t_prod'), Results(a_flag=True, a_float=12345.0)
            $ python example.py -h
            usage: example.py [-a] [--a-float <float>] [-t] [--help] [<token id>]
            ```

        Returns:
            A tuple of the active `Token` and the `Results` for custom options.

        Raises:
            SystemExit: If a parsed option calls for an alternate program flow that
                exits on completion (e.g. `--tokens`).
        """
        args = vars(super().parse_args())

        # Check whether to switch to token management flow, which exits on completion.
        if args.get(_TOKENS_KEY):
            try:
                self.manage_tokens()
            except KeyboardInterrupt:
                exit_reason = self.cli.strings.m_exit_by_interrupt
                self.cli.exit_process(exit_reason, is_error=False)

        # Select the token to use, based on command-line args (if present) or defaults.
        if token_uid := args.get(_TOKEN_KEY):
            token = next(t for t in self._tokens if t.uid == token_uid)
        elif len(self._tokens) == 1:
            token = self._tokens[0]
        else:
            token = Token.get_default(self.cli)

        # Return the token for Botstrap, and the parsed custom options for the user.
        return token, Option.Results(*self._custom_keys, **args)

    def manage_tokens(self) -> None:
        """Starts the token management flow for viewing and deleting saved token files.

        This method is automatically invoked by
        [`parse_bot_args()`][botstrap.internal.Argstrap.parse_bot_args] when the
        `--tokens` option is specified on the command line. In terms of diverting the
        program flow, it takes precedence over any custom options (if applicable)
        but yields to both `--help` and `--version`.

        Once this method is called, there's no `return`ing to the original program
        flow - the process is guaranteed to exit when this method finishes. For more
        details, expand the boxes below.

        ??? note "Note - Exiting from this method"
            The process will end with exit code `0` (to indicate success) when one
            of the following things happens:

            - The user has **no existing files** for any of the
              [`tokens`][botstrap.internal.Argstrap.__init__] in the list that was
              provided when this `Argstrap` instance was created. If the `"default"`
              token wasn't included in that original list, it will be appended for the
              purposes of this method, just in case the user has existing files
              associated with it.

            - The user still has existing token files, but **chooses not to delete**
              any (more) of them.

            There are currently no cases in which this process ends with a non-`0`
            exit code.

        ??? example "Example - Deleting a saved token"
            ```{.console title="Console Session" .annotate}
            $ python examplebot.py -t # (1)

            examplebot: You currently have the following bot tokens saved:
              1. development ->  ~/botstrap/examples/examplebot/.botstrap_keys/.dev.*
              2. production  ->  ~/botstrap/examples/examplebot/.botstrap_keys/.prod.*

            Would you like to delete any of these tokens? If so, type "yes" or "y": y
            Please enter the number next to the token you want to delete: 0

            That number doesn't match any of the above tokens. (Expected "1" or "2".)

            Would you like to try again? If so, type "yes" or "y": y
            Please enter the number next to the token you want to delete: 1

            Token successfully deleted.

            examplebot: You currently have the following bot tokens saved:
              1. production  ->  ~/botstrap/examples/examplebot/.botstrap_keys/.prod.*

            Would you like to delete any of these tokens? If so, type "yes" or "y": n

            Received a non-affirmative response. Exiting process.
            ```

            1.  Notice that the bot is started with the `-t` flag, which (in this case)
                is an abbreviation for `--tokens`.

        Raises:
            SystemExit: When the user cannot (or does not want to) delete any more
                token files.
        """
        ansi_pattern = re.compile(r"\x1b\[[0-9]+m")
        default_token = Token.get_default(self.cli)

        if not any(t for t in self._tokens if t.uid == default_token.uid):
            # Add the default token just in case it's stored. (No effect if it isn't.)
            self._tokens.append(default_token)

        # Keep looping as long as the list of "tokens with existing files" is not empty.
        while saved_tokens := [t for t in self._tokens if t.file_path.is_file()]:
            self.cli.print_prefixed(self.cli.strings.t_manage_list)
            enumeration = {str(n): t for n, t in enumerate(saved_tokens, start=1)}
            token_width = max(len(ansi_pattern.sub("", str(t))) for t in saved_tokens)

            # Print a numbered line for each token, displaying its name and file path.
            for token_num, token in enumeration.items():
                num = self.cli.colors.highlight(token_num)
                padding = token_width - len(ansi_pattern.sub("", str(token)))
                index = str(token.file_path).rindex(token.uid) + len(token.uid)
                path = self.cli.colors.lowlight(f"{str(token.file_path)[:index]}.*")
                print(f"  {num}. {token}{' ' * padding} ->  {path}")

            # "Would you like to permanently delete any of these tokens?" Yes or exit.
            self.cli.confirm_or_exit(self.cli.strings.t_delete)

            prompt = self.cli.strings.t_delete_cue
            joined_nums = self.cli.strings.join_choices(
                token_nums := enumeration.keys(),
                format_choice=self.cli.colors.highlight,
            )

            # Loop until the user either inputs a valid token number or decides to stop.
            while (token_num := self.cli.get_input(prompt)) not in token_nums:
                invalid_input_text = (
                    self.cli.colors.warning(self.cli.strings.t_delete_mismatch),
                    self.cli.strings.t_delete_hint.substitute(token_nums=joined_nums),
                )
                print(" ".join(invalid_input_text))
                self.cli.confirm_or_exit(self.cli.strings.t_delete_retry)

            enumeration[token_num].clear()  # The token files are permanently deleted.
            print(self.cli.colors.success(self.cli.strings.t_delete_success))

        # The user has no more saved bot tokens (or had none to begin with).
        self.cli.print_prefixed(self.cli.strings.t_manage_none)
        self.cli.exit_process(is_error=False)
