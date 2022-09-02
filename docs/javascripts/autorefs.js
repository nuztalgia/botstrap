/** Adds links to specific references (defined at the bottom of this file). */
function addReferenceLinks(element) {
  for (const [regex, url] of Object.entries(referenceMap)) {
    for (const match of element.innerHTML.matchAll(new RegExp(regex, "g"))) {
      const onPage = window.location.href.match(new RegExp(url + "(#.*)?$"));
      const replacement = `<a href="${onPage ? "#" : url}">${match[0]}</a>`;
      element.innerHTML = element.innerHTML.replace(match[0], replacement);
    }
  }
}

/** Adds syntax highlighting to text matched by a regex in the bound element. */
function addSyntaxHighlighting(spanClass, regexPattern, replacementIndex = 1) {
  for (const match of this.innerHTML.matchAll(new RegExp(regexPattern, "g"))) {
    const replacement =
      match.length === 1
        ? `<span class="${spanClass}">${match[0]}</span>`
        : match[0].replace(
            match[replacementIndex],
            `<span class="${spanClass}">${match[replacementIndex]}</span>`,
          );
    this.innerHTML = this.innerHTML.replace(match[0], replacement);
  }
}

/** Adds reference links and syntax highlighting to the given `code` element. */
function processCodeElement(codeElement) {
  const highlight = addSyntaxHighlighting.bind(codeElement);
  codeElement.classList.add("highlight");
  codeElement.innerHTML = codeElement.innerText;
  addReferenceLinks(codeElement);
  highlight("kc", /\b(None|True|False)\b/);
  highlight("mi", /^\d+$/);
  highlight("nb", /\b(bool|dict|float|int|list|str|tuple|type)\b([^<>]|$)/);
  highlight("ne", /\b(SystemExit|[A-Z][a-z]+Error)\b/);
  highlight("o", /(\*\*|\|)[^<>]/);
  highlight("p", /(^|<\/[a-z]*>)({}|,|\[+|\]+)/, 2);
  highlight("s2", /('.*'|^".*"$)/);
}

// Wait until the page is ready, then go through and process all relevant code.
window.addEventListener("DOMContentLoaded", (event) => {
  for (const table of document.querySelectorAll(".md-typeset__table")) {
    if (table.querySelector("thead tr").innerText.match(/Type\tDescription/)) {
      // This is a "Parameters", "Returns", or "Raises" table. Select all code.
      for (const codeElement of table.querySelectorAll("code")) {
        processCodeElement(codeElement);
      }
    }
  }
});

// A mapping of regex patterns (as strings) to the URLs they should link to.
const referenceMap = {
  "^Botstrap$": "/api/botstrap/",
  "^CliColors$": "/api/cli-colors/",
  "^CliStrings$": "/api/cli-strings/",
  "^Color$": "/api/color/",
  "^Option$": "/api/option/",
  "^CliSession$": "/internal/cli-session/",
  "\\bToken\\b": "/internal/token/",

  "^CliColors\\.default\\(\\)$": "/api/cli-colors/#botstrap.colors.CliColors.default",
  "^CliColors\\.off\\(\\)$": "/api/cli-colors/#botstrap.colors.CliColors.off",
  "^CliStrings\\.default\\(\\)$":
    "/api/cli-strings/#botstrap.strings.CliStrings.default",
  "^CliStrings\\.compact\\(\\)$":
    "/api/cli-strings/#botstrap.strings.CliStrings.compact",
  "(^Results$|\\bOption\\.Results\\b)": "/api/option/#botstrap.options.Option.Results",

  "\\bAny\\b": "https://docs.python.org/3/library/typing.html#typing.Any",
  "\\bCallable\\b": "https://docs.python.org/3/library/typing.html#typing.Callable",
  "\\bPath\\b": "https://docs.python.org/3/library/pathlib.html#concrete-paths",
  "(re\\.)?Pattern":
    "https://docs.python.org/3/library/re.html#regular-expression-objects",
};
