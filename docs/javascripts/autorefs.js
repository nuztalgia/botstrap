window.addEventListener("DOMContentLoaded", (event) => {
  // Add reference links and syntax highlighting to inline code elements.
  for (const codeElement of document.querySelectorAll(
    ".doc-contents :not(.doc-heading, .doc-label, a, pre, summary) > code",
  )) {
    if (codeElement.innerText) {
      codeElement.innerHTML = codeElement.innerText; // Clear existing markup.
    }
    codeElement.classList.add("highlight");
    addReferenceLinks(codeElement);
    highlightCodeInline(codeElement);
  }
  // Improve syntax highlighting in Python examples and source code blocks.
  for (const codeElement of document.querySelectorAll(
    ":is(.language-py, .language-pycon, .quote) code",
  )) {
    highlightCodeBlock(codeElement);
  }
});

/** Adds links to specific references (defined at the bottom of this file). */
function addReferenceLinks(element) {
  for (const [regex, rawUrl] of Object.entries(referenceMap)) {
    for (const match of element.innerHTML.matchAll(new RegExp(regex, "g"))) {
      const url =
        (window.location.href.match(/\/en\/latest\//) && rawUrl.match(/^\/.*/)
          ? "/en/latest"
          : "") + rawUrl;
      const isOnPage = window.location.href.match(new RegExp(url + "(#.*)?$"));
      const replacement = `<a href="${isOnPage ? "#" : url}">${match[0]}</a>`;
      element.innerHTML = element.innerHTML.replace(match[0], replacement);
    }
  }
}

/** Adds syntax highlighting to text matched by a regex in the bound element. */
function addSyntaxHighlighting(spanClass, regexPattern) {
  for (const match of this.innerHTML.matchAll(new RegExp(regexPattern, "g"))) {
    const replacement =
      match.length === 1
        ? `<span class="${spanClass}">${match[0]}</span>`
        : match[0].replace(
            (matchItem = match.filter((item) => item != null).slice(-1)[0]),
            `<span class="${spanClass}">${matchItem}</span>`,
          );
    this.innerHTML = this.innerHTML.replace(match[0], replacement);
  }
}

/** Adds syntax highlighting (based on crude regexes) to the given element.
 *  These regexes are written/edited on an as-needed basis & may be fragile. */
function highlightCodeInline(element) {
  const highlight = addSyntaxHighlighting.bind(element);
  highlight("k", /\b(if|return)\b/);
  highlight("kc", /\b(None|True|False)\b/);
  highlight("mi", /^\d+$/);
  highlight(
    "nb",
    /(^|[^">]{2}|\b)(bool|dict|float|int|list|object|print|str|tuple|type)\b\]?/,
  );
  highlight("ne", /\b(SystemExit|[A-Z][a-z]+Error)\b/);
  highlight("o", /((\*\*|\|)[^<>]|(=)[^"]|^[a-z_]*(\.))/);
  highlight("p", /(^|<\/[a-z]*>|\b)({}|,|\[+|"?(\]+,?)|\(\)$)/);
  highlight("s2", /('.*'|^".*"$|[^=]("[^<>]*")[^>])/);
}

/** Improve existing syntax highlighting & color usage in the given element. */
function highlightCodeBlock(element) {
  for (const match of element.innerHTML.matchAll(
    /="(n|fm)"(>[a-z_][a-zA-Z_]*<\/span><span class="p">\()/g,
  )) {
    // Change text to "function" color (pink) if it looks like a function name.
    element.innerHTML = element.innerHTML.replace(match[0], `="nf"${match[2]}`);
  }
  for (const stringElement of element.querySelectorAll(":is(.sa, .se)")) {
    // Recolor existing string affixes (.sa) and string escapes (.se).
    stringElement.className = "s1"; // Change to "string" color (green).
  }
  for (const nameElement of element.querySelectorAll(":is(.nc, .ne)")) {
    // Recolor existing class names (.nc) and exception names (.ne).
    nameElement.className = "se"; // Change to "special" color (red).
  }
  for (const nameElement of element.querySelectorAll(".n")) {
    // Recolor class names (explicitly listed below) outside of imports.
    const importNames = nameElement.parentElement.querySelectorAll(".kn");
    if (importNames.length != 2 && classNames.has(nameElement.innerHTML)) {
      nameElement.className = "se"; // Change to "special" color (red).
    }
  }
  for (const keywordConstant of element.querySelectorAll(".kc")) {
    keywordConstant.className = "mi"; // Change to "number" color (orange).
  }
  for (const operatorWord of element.querySelectorAll(".ow")) {
    operatorWord.className = "k"; // Change to "keyword" color (blue).
  }
  for (const stringInterpol of element.querySelectorAll(".si")) {
    stringInterpol.className = "p"; // Change to "punctuation" color (grey).
  }
}

/** A set of class names to highlight with the "special" color in code blocks.
 */ // prettier-ignore
const classNames = new Set([
  // Class names from the Botstrap library.
  "Botstrap", "CliColors", "CliStrings", "Color", "Option", "Results",
  "Argstrap", "CliSession", "Metadata", "Secret", "Token",
  // Class names from the "discord" package.
  "Activity", "ActivityType", "AllowedMentions", "Bot",
  // Class names from the "typing" package.
  "Any", "Callable", "ClassVar", "Final",
  "Iterable", "Iterator", "Literal", "TypeAlias",
  // Class names from miscellaneous packages/libs.
  "AlphaBot", "ArgumentParser", "Fernet", "Fore", "Path",
  "Pattern", "RawTextHelpFormatter", "Style", "Template",
  // Error names from various packages/libs.
  "MessageError", "PackageNotFoundError", "InvalidToken",
]);

/** A mapping of regex patterns (as strings) to the URLs they should link to.
 *  These regexes are written/edited on an as-needed basis & may be fragile.
 */ // prettier-ignore
const referenceMap = {
  // Top-level pages in the Botstrap library documentation.
  "^Botstrap$": "/api/botstrap/",
  "^CliColors$": "/api/cli-colors/",
  "^CliStrings$": "/api/cli-strings/",
  "^Color$": "/api/color/",
  "^Option$": "/api/option/",
  "^Argstrap$": "/internal/argstrap/",
  "^CliSession$": "/internal/cli-session/",
  "^Secret$": "/internal/secret/",
  "\\bToken\\b": "/internal/token/",

  // Anchors within pages in the Botstrap library documentation.
  "^CliColors\\.default\\(\\)$":
      "/api/cli-colors/#botstrap.colors.CliColors.default",
  "^CliColors\\.off\\(\\)$":
      "/api/cli-colors/#botstrap.colors.CliColors.off",
  "^CliStrings\\.default\\(\\)$":
      "/api/cli-strings/#botstrap.strings.CliStrings.default",
  "^CliStrings\\.compact\\(\\)$":
      "/api/cli-strings/#botstrap.strings.CliStrings.compact",
  "(^Results$|\\bOption\\.Results\\b)":
      "/api/option/#botstrap.options.Option.Results",

  // Pages and/or anchors in the official Python documentation.
  "\\bAny\\b":
      "https://docs.python.org/3/library/typing.html#typing.Any",
  "\\bCallable\\b":
      "https://docs.python.org/3/library/typing.html#typing.Callable",
  "(pathlib\\.)?Path\\b":
      "https://docs.python.org/3/library/pathlib.html#concrete-paths",
  "(re\\.)?Pattern":
      "https://docs.python.org/3/library/re.html#regular-expression-objects",
};
