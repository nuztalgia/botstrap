"""This module contains the `Argstrap` class, which parses arguments for a bot's CLI."""
import re
from argparse import ArgumentParser, RawTextHelpFormatter
from typing import Any, Final, Optional

from botstrap.internal.clisession import CliSession
from botstrap.internal.metadata import Metadata
from botstrap.internal.tokens import Token
from botstrap.options import Option

_HELP_KEY: Final[str] = "help"
_TOKEN_KEY: Final[str] = "token"
_TOKENS_KEY: Final[str] = "tokens"
_VERSION_KEY: Final[str] = "version"

_HELP_PATTERN: Final[re.Pattern] = re.compile(r"(^|[^%])(%)([^%(]|$)")
_HELP_REPLACEMENT: Final[str] = r"\1\2\2\3"  # Escape the "%" by including it twice.


class Argstrap(ArgumentParser):
    """Parses command-line args and provides a CLI framework for bots that use Botstrap.

    This class extends [`ArgumentParser`][1] and can operate similarly, but its primary
    purpose is to automatically handle the command-line arguments expected by Botstrap.
    These may be the default options provided out-of-the-box (such as `--help` and
    `--tokens`), or custom ones defined for individual bots with the help of the
    [`Option`](../../api/option) class.

    The portion of the program flow handled by this class is quite self-contained - its
    only method that gets called externally (aside from the constructor) is
    [`parse_bot_args()`][botstrap.internal.Argstrap.parse_bot_args]. Nevertheless,
    detailed documentation and source code snippets are provided for every method,
    because **all of them** contain logic that is fundamental to how Botstrap operates.

    [1]: https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser
    """

    def __init__(
        self,
        cli: CliSession,
        tokens: list[Token],
        description: Optional[str] = None,
        version: Optional[str] = None,
        **custom_options: Option,
    ) -> None:
        """Initializes a new `Argstrap` instance.

        Args:
            cli:
                A `CliSession` providing the UX used by the CLI.
            tokens:
                The tokens that are defined for the bot. Will be used to determine its
                available command-line arguments (e.g. if multiple tokens are supported,
                a "token id" argument may be specified to select which one to use).
            description:
                A short human-readable description of the bot. Will be displayed when
                the `--help` option is passed to the CLI. If omitted, Botstrap will try
                to fill this field from package metadata. If unsuccessful, this line
                will be left blank.
            version:
                A string representing the current version of the bot. Will be displayed
                when the `--version` option is specified. If omitted, that option will
                not be present in the bot's CLI.
            **custom_options:
                Keyword args specifying the bot's custom-defined command-line options.
                If omitted, only the default Botstrap options will be available in the
                bot's CLI.
        """
        self.cli: Final[CliSession] = cli
        self._tokens: Final[list[Token]] = tokens
        self._custom_keys: Final[list[str]] = []  # Keys are added as they're validated.

        if not description:
            summary = Metadata.get_package_info(self.cli.name).get("summary")
            description = summary if isinstance(summary, str) else ""

        program_command = Metadata.get_program_command(self.cli.name)
        mode_addendum = (
            (is_multi_token := len(tokens) > 1)
            and (" " + self.cli.strings.h_desc_mode.substitute(token=tokens[0]).strip())
        ) or ""
        description = (
            (description and f"  {description.strip()}\n") + "  "
        ) + self.cli.strings.h_desc.substitute(
            program_command=" ".join(program_command), mode_addendum=mode_addendum
        )

        super().__init__(
            prog=(prog := self.cli.colors.primary(program_command[-1])),
            description=description,
            formatter_class=RawTextHelpFormatter,
            add_help=False,
        )

        usage_components = [prog]  # Will later be combined to form the `usage` string.
        abbreviations = self.assign_arg_abbrs(*custom_options)  # Assigns defaults too.

        def add_usage_component(name: str) -> None:
            """Formats the provided name and appends it to the usage_components list."""
            if (component := f"[{name}]") in usage_components:
                raise RuntimeError(f"Duplicate usage component: {component}")
            usage_components.append(component)

        def add_option(key: str, action: str = "store_true", **kwargs: Any) -> None:
            """Adds the option (and its abbr) to the parser and to usage_components."""
            abbr = f"-{abbreviations[key]}" if abbreviations.get(key) else ""
            name = "--" + key.lower().strip("_").replace("_", "-")
            # noinspection PyTypeChecker
            self.add_argument(*[s for s in (abbr, name) if s], action=action, **kwargs)
            add_usage_component(abbr if (abbr and (key != _HELP_KEY)) else name)

        # First, add any/all custom-defined (a.k.a. probably the most relevant) options.
        for option_key, option in custom_options.items():
            option_dict: dict[str, Any] = {
                "action": "store_true" if option.flag else "store",
                "help": _HELP_PATTERN.sub(_HELP_REPLACEMENT, option.help or ""),
            }  # Translating the option to the format expected by add_argument().

            if not option.flag:  # Non-flag options require more information.
                option_dict["default"] = option.default
                option_dict["type"] = (_type := type(option.default))
                option_dict["choices"] = option.choices or None
                option_dict["metavar"] = self.cli.colors.lowlight(f"<{_type.__name__}>")

            # Add the custom option to the CLI and keep track of its key for later use.
            add_option(option_key, **option_dict)
            self._custom_keys.append(option_key)

        # Then add the default options, in order of their usefulness when viewing "-h".
        add_option(_TOKENS_KEY, help=self.cli.strings.h_tokens)  # Add "--tokens" first.

        if version:  # Only add "--version" if a version string was specified.
            h_version = self.cli.strings.h_version
            add_option(_VERSION_KEY, action="version", version=version, help=h_version)

        # Add "--help" as the last option (it won't be abbreviated in the usage string).
        add_option(_HELP_KEY, action="help", help=self.cli.strings.h_help)

        # Finally, add the positional "token id" argument iff there's more than 1 token.
        if is_multi_token:
            joined_uids = self.cli.strings.join_choices(
                token_uids := [token.uid for token in self._tokens],
                conjunction=self.cli.strings.m_conj_and,
            )
            self.add_argument(  # Note that this is "add_argument", not "add_option".
                _TOKEN_KEY,
                nargs="?",
                choices=token_uids,
                default=token_uids[0],
                help=self.cli.strings.h_token_id.substitute(token_ids=joined_uids),
                metavar=(token_metavar := "<token id>"),
            )
            add_usage_component(self.cli.colors.lowlight(token_metavar))

        # Join all the components together to produce the complete usage string.
        self.usage = " ".join(usage_components)

    # noinspection PyMethodMayBeStatic
    def assign_arg_abbrs(self, *custom_keys: str) -> dict[str, Optional[str]]:
        """Returns a dictionary mapping arg/option keys to their possible abbreviations.

        This method is called by the constructor in order to determine which
        command-line args are eligible to be abbreviated, and what those abbrs should
        be. It has no purpose after [`__init__()`][botstrap.internal.Argstrap.__init__]
        is finished, by which point all of the available command-line arguments
        (including abbreviations) will have been set using the superclass method
        [`add_argument()`][1].

        ??? info "Info - Contents of the resulting `dict`"
            The dictionary returned by this method represents a mapping of arg/option
            keys (i.e. names) to their abbreviations. It has the following properties:

            - Each **key** is the "full name" of a command-line argument or option that
              may later be parsed by this `Argstrap` instance. As is the norm for
              `#!py dict` objects, all keys are unique. The [order][2] in which
              they are specified (all default args/options first, then all custom
              options) is not relevant to the user.

            - The **value** for each key will either be a single-character `#!py str`
              containing the first letter of the argument name, or `None` if a
              higher-[priority](./#abbr-priority) argument starting with the same letter
              was previously added to the `#!py dict`.

            - Values that represent abbreviations (i.e. all `#!py str` values) are
              **guaranteed to be unique**.

        ??? note "Note - Determining abbreviation priority"
            <div id="abbr-priority"/>
            Ideally, all command-line arguments/options would all start with different
            letters, and would all be conveniently and intuitively abbreviated.
            Since that won't always be the case, this method reserves letters for
            abbreviations according to the following priority:

            1.  First, `-h` is reserved for the `--help` option. This is an extremely
                common abbreviation for command-line tools, so it is given top priority.

            2.  Then, abbreviations for **custom-defined options** are reserved in the
                same [order][3] in which the keyword arguments were originally passed
                in. For example, with three custom options named `--hoo`, `--bar`, and
                `--baz`, the only resulting new abbreviation would be `-b` for `--bar`.

            3.  Last, if `-t` and/or `-v` have not been reserved yet, they are assigned
                to `--tokens` and `--version` respectively. These are default options
                provided by Botstrap, so they have lower priority than custom options,
                which tend to be more useful for the bots that define them. For example,
                a bot with a custom `--verbose` option would be able to toggle it with
                `-v`, and would have to use the full name of the `--version` option.

            This procedure ensures that all abbreviations are uniquely assigned, and
            that they are (hopefully) delegated to the most useful options for each
            individual bot. :four_leaf_clover:

        [1]: https://docs.python.org/3/library/argparse.html#the-add-argument-method
        [2]: https://docs.python.org/3/whatsnew/3.6.html#new-dict-implementation
        [3]: https://peps.python.org/pep-0468/

        Args:
            *custom_keys:
                All of the keys specified for custom command-line options
                (i.e. the names of the `#!py **custom_options` keyword args).

        Returns:
            A dictionary mapping argument/option names to their possible abbreviations.

        Raises:
            ValueError: If an option key/name is not unique across <u>**all**</u>
                arguments (custom-defined *and* default).
        """
        assigned_options: dict[str, Optional[str]] = {}

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

        # First, assign the keys & abbrs that are strictly reserved by default options.
        add_options(_HELP_KEY, add_abbrs=True)  # "-h" is the only reserved abbr.
        add_options(_TOKEN_KEY, _TOKENS_KEY, _VERSION_KEY)

        # Then, try to assign keys and abbreviations for any/all custom-defined options.
        add_options(*custom_keys, add_abbrs=True)

        # Last, try to add abbrs for default keys that were assigned (above) w/o abbrs.
        add_options(_TOKENS_KEY, _VERSION_KEY, allow_existing_keys=True, add_abbrs=True)

        return assigned_options

    def parse_bot_args(self) -> tuple[Token, Option.Results]:
        """Parses command-line args and returns the results along with the active token.

        Returns:
            A tuple containing the active `Token` and the `Results` for custom options.

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

        This is automatically invoked by
        [`parse_bot_args()`][botstrap.internal.Argstrap.parse_bot_args] when the
        `--tokens` option is specified on the command line (and if neither
        `-h` nor `-v` was specified, because those options take priority).

        ??? note "Note - Exiting from this method"
            Once this method is invoked, there's no `#!py return`ing to the "main"
            program flow. The process is guaranteed to end with exit code `#!py 0`
            (to indicate that this flow finished successfully) when one of the
            following things happens:

            - The user has **no more files** for any of the
              [`tokens`][botstrap.internal.Argstrap.__init__] in the list that was
              provided when this class was instantiated. If the `#!py "default"` token
              wasn't included in that original list, it will be appended for the
              purposes of this method, just in case the user has existing files
              associated with it.

            - The user still has existing token files, but **chooses not to delete**
              any (more) of them.

        Raises:
            SystemExit: When the user cannot (or does not want to) delete any more
                token files.
        """
        ansi_pattern = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]")
        default_token = Token.get_default(self.cli)

        if not any(t for t in self._tokens if t.uid == default_token.uid):
            self._tokens.append(default_token)  # Just in case the user has it stored.

        # Keep looping as long as the list of "tokens with existing files" is not empty.
        while saved_tokens := [t for t in self._tokens if t.file_path.is_file()]:
            self.cli.print_prefixed(self.cli.strings.t_manage_list)
            enumeration = {str(n): t for n, t in enumerate(saved_tokens, start=1)}
            token_width = max(len(ansi_pattern.sub("", str(t))) for t in saved_tokens)

            # Print a numbered line for each token, displaying its name and file path.
            for token_num, token in enumeration.items():
                num = self.cli.colors.highlight(token_num)
                padding = " " * (token_width - len(ansi_pattern.sub("", str(token))))
                index = str(token.file_path).rindex(token.uid) + len(token.uid)
                path = self.cli.colors.lowlight(f"{str(token.file_path)[:index]}.*")
                print(f"  {num}. {token}{padding} ->  {path}")

            # "Would you like to permanently delete any of these tokens?" Yes or exit.
            self.cli.confirm_or_exit(self.cli.strings.t_delete)

            prompt = self.cli.strings.t_delete_cue
            joined_nums = self.cli.strings.join_choices(
                token_nums := enumeration.keys(),
                format_choice=self.cli.colors.highlight,
            )

            # Keep looping until the input is valid, or until the user decides to stop.
            while (token_num := self.cli.get_input(prompt)) not in token_nums:
                invalid_input_text = (
                    self.cli.colors.warning(self.cli.strings.t_delete_mismatch),
                    self.cli.strings.t_delete_hint.substitute(token_nums=joined_nums),
                )
                print(" ".join(invalid_input_text))
                self.cli.confirm_or_exit(self.cli.strings.t_delete_retry)

            enumeration[token_num].clear()  # Token files are permanently deleted.
            print(self.cli.colors.success(self.cli.strings.t_delete_success))

        # The user has no more saved bot tokens (or had none to begin with).
        self.cli.print_prefixed(self.cli.strings.t_manage_none)
        self.cli.exit_process(is_error=False)
