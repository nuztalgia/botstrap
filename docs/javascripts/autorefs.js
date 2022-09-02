/** Adds links to specific references (defined at the bottom of this file). */
function addReferenceLinks(element) {
  for (const [regex, url] of Object.entries(referenceMap)) {
    for (const match of element.innerHTML.matchAll(new RegExp(regex, "g"))) {
      const onPage = window.location.href.match(new RegExp(url + "(#.*)?$"));
      let replacement = `<a href="${onPage ? "#" : url}">${match[0]}</a>`;
      if (window.location.href.match(/\/en\/latest\//)) {
        replacement = "/en/latest" + replacement;
      }
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

/** Adds syntax highlighting (based on crude regexes) to the given element. */
function highlightCodeElement(element) {
  const highlight = addSyntaxHighlighting.bind(element);
  // These regexes are written/edited on an as-needed basis and may be fragile.
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

// Wait until the page is ready, then go through and process all relevant code.
window.addEventListener("DOMContentLoaded", (event) => {
  for (const codeElement of document.querySelectorAll(
    ".doc-contents :not(.doc-heading, .doc-label, a, pre, summary) > code",
  )) {
    if (codeElement.innerText) {
      codeElement.innerHTML = codeElement.innerText; // Clear existing markup.
    }
    addReferenceLinks(codeElement);
    codeElement.classList.add("highlight");
    highlightCodeElement(codeElement);
  }
});

/* A mapping of regex patterns (as strings) to the URLs they should link to.
 * These regexes are written/edited on an as-needed basis and may be fragile.
 */ // prettier-ignore
const referenceMap = {
  // Top-level pages in the Botstrap library documentation.
  "^Botstrap$": "/api/botstrap/",
  "^CliColors$": "/api/cli-colors/",
  "^CliStrings$": "/api/cli-strings/",
  "^Color$": "/api/color/",
  "^Option$": "/api/option/",
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
