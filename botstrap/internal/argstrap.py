"""This module contains the `Argstrap` class, which parses arguments for a bot's CLI."""
import re
from argparse import ArgumentParser, RawTextHelpFormatter
from typing import Any, Callable, Final, Optional

from botstrap.internal.clisession import CliSession
from botstrap.internal.metadata import Metadata
from botstrap.internal.tokens import Token
from botstrap.options import Option

_HELP_KEY: Final[str] = "help"
_TOKEN_KEY: Final[str] = "token"
_TOKENS_KEY: Final[str] = "tokens"
_VERSION_KEY: Final[str] = "version"

_TOKEN_METAVAR: Final[str] = "token id"

_HELP_PATTERN: Final[re.Pattern] = re.compile(r"(^|[^%])(%)([^%(]|$)")
_HELP_REPLACEMENT: Final[str] = r"\1\2\2\3"  # Escape the "%" by including it twice.


class Argstrap(ArgumentParser):
    """Parses command-line args and provides a CLI framework for bots that use Botstrap.

    This class extends
    [`ArgumentParser`](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser)
    and can operate similarly, but its primary use is to automatically handle both
    Botstrap-specific and custom-defined command-line options.
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
        self._custom_callbacks: Final[dict[str, Callable[[Any], None]]] = {}

        program_command = Metadata.get_program_command(self.cli.name)
        # The last item on the command line is (usually?) the file/module/script name.
        program_name = self.cli.colors.primary(program_command[-1])

        super().__init__(
            prog=program_name,
            description=self._build_description_string(program_command, description),
            formatter_class=RawTextHelpFormatter,
            add_help=False,
        )  # "usage" wasn't specified because it will be built & set during this method.

        usage_components = [program_name]  # Will be combined to form the usage string.
        abbreviations = self.assign_arg_abbrs(*custom_options)  # Includes defaults too.

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
            add_option(option_key, **self._process_custom_option(option_key, option))

        # Then add the default options, in order of their usefulness when viewing "-h".
        add_option(_TOKENS_KEY, help=self.cli.strings.h_tokens)  # Add "--tokens" first.

        if version:  # Only add "--version" if a version string was specified.
            h_version = self.cli.strings.h_version
            add_option(_VERSION_KEY, action="version", version=version, help=h_version)

        # Add "--help" as the last option (it won't be abbreviated in the usage string).
        add_option(_HELP_KEY, action="help", help=self.cli.strings.h_help)

        # Finally, add the positional "token id" argument iff there's more than 1 token.
        if len(self._tokens) > 1:
            self.add_argument(  # Note that this is "add_argument", not "add_option".
                _TOKEN_KEY,
                nargs="?",
                choices=(token_uids := [token.uid for token in self._tokens]),
                default=token_uids[0],
                help=self.cli.strings.h_token_id.substitute(token_ids=token_uids),
                metavar=self._format_metavar(_TOKEN_METAVAR, lowlight=False),
            )
            add_usage_component(self._format_metavar(_TOKEN_METAVAR))  # Lowlight on.

        # Join all the components together to produce the complete usage string.
        self.usage = " ".join(usage_components)

    def _format_metavar(self, placeholder_text: str, lowlight: bool = True) -> str:
        """Returns the placeholder text, surrounded by chevrons & optionally colored."""
        metavar = f"<{placeholder_text}>"
        return self.cli.colors.lowlight(metavar) if lowlight else metavar

    def _build_description_string(
        self,
        program_command: list[str],
        original_description: Optional[str],
        indentation: str = "  ",
    ) -> str:
        """Returns a str describing the bot and how to run it with its default token."""
        default_token = self._tokens[0] if (len(self._tokens) > 1) else None
        desc = original_description or ""

        if (not desc) and (info := Metadata.get_package_info(self.cli.name)):
            desc = summary if isinstance(summary := info.get("summary"), str) else ""

        indented_desc = (f"{indentation}{desc.strip()}\n" if desc else "") + indentation
        format_mode_text = self.cli.strings.h_desc_mode.substitute
        mode_addendum = (default_token and format_mode_text(token=default_token)) or ""

        return indented_desc + self.cli.strings.h_desc.substitute(
            program_command=" ".join(program_command),
            mode_addendum=f" {mode_addendum.strip()}" if mode_addendum else "",
        )

    def _process_custom_option(self, option_key: str, option: Option) -> dict[str, Any]:
        """Registers a callback and returns the Option in add_argument **kwargs form."""
        option_kwargs: dict[str, Any] = {
            "action": "store_true" if option.flag else "store",
            "help": _HELP_PATTERN.sub(_HELP_REPLACEMENT, option.help or ""),
        }
        if not option.flag:  # Non-flag options require more information.
            option_kwargs["default"] = option.default
            option_kwargs["type"] = (option_type := type(option.default))
            option_kwargs["choices"] = option.choices or None
            option_kwargs["metavar"] = self._format_metavar(option_type.__name__)

        def fallback_callback(option_value: Any) -> None:
            """Raises a nicely-formatted RuntimeError for options without a callback."""
            indentation = " " * len(f"{RuntimeError.__name__}: ")
            raise RuntimeError(
                f"Custom option '{option_key}' did not set a callback.\n"
                f"{indentation}Option type:  '{type(option_value).__name__}'\n"
                f"{indentation}Parsed value: '{option_value}'"
            )

        self._custom_callbacks[option_key] = (
            option.callback if (option.callback != print) else fallback_callback
        )
        return option_kwargs

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
              "higher-priority" argument starting with the same letter was previously
              added to the `#!py dict`. Values that represent abbreviations (i.e. all
              `#!py str` values) are **guaranteed to be unique**.

        ??? note "Note - Determining abbreviation priority"
            Ideally, all command-line arguments/options would all start with different
            letters, and would all be conveniently and intuitively abbreviated.
            Since that won't always be the case, this method reserves letters for
            abbreviations according to the following priority:

            1.  First, `-h` is reserved for the `--help` option. This is an extremely
                common abbreviation for command-line tools, so it is given top priority.

            2.  Then, abbreviations for **custom-defined options** are reserved in the
                same order in which the keyword arguments were originally passed in. For
                example, with three custom options named `--hoo`, `--bar`, and `--baz`,
                the only resulting new abbreviation would be `-b` for `--bar`.

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

    def parse_bot_args(self) -> Token:
        """Parses command-line args, calls option callbacks, & returns the token to use.

        Returns:
            The token that should be decrypted and then plugged in to run the bot.

        Raises:
            RuntimeError: If a custom-defined [`Option`](../../api/option) was parsed,
                but it did not properly set its `callback` attribute.
            SystemExit: If a parsed option calls for an alternate program flow that
                exits on completion (e.g. `--tokens`).
        """
        args = vars(super().parse_args())

        # Invoke the callbacks for any/all custom-defined options.
        for option_name, callback in self._custom_callbacks.items():
            callback(args.get(option_name))  # Pass in the value of the parsed arg.

        # Check whether to switch to the token mgmt flow, which will exit on completion.
        if args.get(_TOKENS_KEY):
            self.manage_tokens()

        # Return the token to use, based on command-line args (if present) or defaults.
        if token_uid := args.get(_TOKEN_KEY):
            return next(t for t in self._tokens if t.uid == token_uid)
        elif len(self._tokens) == 1:
            return self._tokens[0]
        else:
            return Token.get_default(self.cli)

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
        default_token = Token.get_default(self.cli)
        if not any(t for t in self._tokens if t.uid == default_token.uid):
            self._tokens.append(default_token)

        while saved_tokens := [t for t in self._tokens if t.file_path.is_file()]:
            self.cli.print_prefixed(self.cli.strings.t_manage_list)

            for count, token in enumerate(saved_tokens, start=1):
                index = str(token.file_path).rindex(token.uid) + len(token.uid)
                path = self.cli.colors.lowlight(f"{str(token.file_path)[:index]}.*")
                print(f"  {count}) {self.cli.colors.highlight(token.uid)} -> {path}")

            self.cli.confirm_or_exit(self.cli.strings.t_delete)

            uids = [token.uid for token in saved_tokens]
            prompt = self.cli.strings.t_delete_cue

            while (uid := self.cli.get_input(prompt)) not in uids:
                print(self.cli.colors.warning(self.cli.strings.t_delete_mismatch))
                print(self.cli.strings.t_delete_hint.substitute(token_ids=uids))
                self.cli.confirm_or_exit(self.cli.strings.t_delete_retry)

            next(t for t in self._tokens if t.uid == uid).clear()
            print(self.cli.colors.success(self.cli.strings.t_delete_success))

        self.cli.print_prefixed(self.cli.strings.t_manage_none)
        raise SystemExit(0)  # Successful exit.
