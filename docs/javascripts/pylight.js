/**
 * @fileoverview Enhances elements containing Python code (both inline and
 * block) by adding/improving syntax highlighting and automatically creating
 * links for specific pre-defined references. Applies to content on all pages.
 */

document$.subscribe(function () {
  // Add reference links and syntax highlighting to inline code elements.
  for (const codeElement of document.querySelectorAll(
    ".doc-contents :not(.doc-heading, .doc-label, a, pre, summary) > code",
  )) {
    if (codeElement.innerText) {
      codeElement.textContent = codeElement.innerText; // Clear existing markup.
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
    const url =
      (window.location.href.match(/\/en\/latest\//) && rawUrl.match(/^\/.*/)
        ? "/en/latest"
        : "") + rawUrl;
    const isOnPage = window.location.href.match(new RegExp(url + "(#.*)?$"));
    for (const match of element.innerHTML.matchAll(new RegExp(regex, "g"))) {
      const link = document.createElement("a");
      link.appendChild(document.createTextNode(match[0]));
      link.href = isOnPage ? "#" : url;
      element.innerHTML = element.innerHTML.replace(match[0], link.outerHTML);
    }
  }
}

/** Adds syntax highlighting (based on crude regexes) to the given code element.
 *  These regexes are written/edited on an as-needed basis & may be fragile. */
function highlightCodeInline(element) {
  for (const [spanClass, regexPattern] of Object.entries({
    k: /\b(if|return)\b/g,
    kc: /\b(None|True|False)\b/g,
    mi: /^\d+$/g,
    nb: /(^|[^">]{2}|\b)(bool|float|object|str|t.pl?e|p?[dlr]?i[csn]t)\b\]?/g,
    ne: /\b(SystemExit|[A-Z][a-z]+Error)\b/g,
    o: /((\*\*|\|)[^<>]|(=)[^"]|^[a-z_]*(\.))/g,
    p: /(^|<\/[a-z]*>|\b)({}|,|\[+|"?(\]+,?)|\(\)$)/g,
    s2: /('.*'|^".*"$|[^=]("[^<>]*")[^>])/g,
  })) {
    for (const match of element.innerHTML.matchAll(regexPattern)) {
      let matchItem;
      const replacement =
        match.length == 1
          ? `<span class="${spanClass}">${match[0]}</span>`
          : match[0].replace(
              (matchItem = match.filter((item) => item != null).slice(-1)[0]),
              `<span class="${spanClass}">${matchItem}</span>`,
            );
      element.innerHTML = element.innerHTML.replace(match[0], replacement);
    }
  }
}

/** Improves existing syntax highlighting in the given code block element. */
function highlightCodeBlock(element) {
  // Change text to "function" color (pink) if it looks like a function name.
  for (const match of element.innerHTML.matchAll(
    /="(n|fm)"(>[a-z_][a-zA-Z_]*<\/span><span class="p">\()/g,
  )) {
    element.innerHTML = element.innerHTML.replace(match[0], `="nf"${match[2]}`);
  }
  // Properly color string interpolation sequences in Template strings.
  const stringInterpolPattern = /="sx">Template.{23}\(.{24}[^<>]*(\$[a-z_]+)/;
  let match;
  while ((match = element.innerHTML.match(stringInterpolPattern))) {
    element.innerHTML = element.innerHTML.replace(
      match[0],
      match[0].replace(match[1], `<span class="si">${match[1]}</span>`),
    );
  }
  element.innerHTML = element.innerHTML.replaceAll(
    '$</span><span class="si">{',
    '</span><span class="si">${',
  );
  // Recolor class names (explicitly listed below) outside of imports.
  for (const childElement of element.querySelectorAll(".n")) {
    const importNames = childElement.parentElement.querySelectorAll(".kn");
    if (importNames.length != 2 && classNames.has(childElement.innerHTML)) {
      childElement.className = "sx"; // Change to "special" color (red).
    }
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
  "\\bNamedTuple\\b":
      "https://docs.python.org/3/library/typing.html#typing.NamedTuple",
  "(pathlib\\.)?Path\\b":
      "https://docs.python.org/3/library/pathlib.html#concrete-paths",
  "(re\\.)?Pattern":
      "https://docs.python.org/3/library/re.html#regular-expression-objects",
};
