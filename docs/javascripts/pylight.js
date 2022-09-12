/**
 * @fileoverview Enhances elements containing Python code (both inline and
 * block) by adding/improving syntax highlighting and automatically creating
 * links for specific pre-defined references. Applies to content on all pages.
 */

document$.subscribe(function () {
  // Add reference links and syntax highlighting to inline code elements.
  const refLinkBuilders = getReferenceLinkBuilders();
  for (const element of document.querySelectorAll(
    ":not(.doc-heading, .doc-label, a, pre, summary) > code:not(.no-pylight)",
  )) {
    element.textContent = element.textContent; // Clear existing markup.
    refLinkBuilders.forEach((refLinkBuilder) => refLinkBuilder(element));
    const oldInnerHTML = element.innerHTML;
    for (const [highlightClass, regexPattern] of highlightPatterns) {
      insertSpans(element, highlightClass, regexPattern);
    }
    if (element.innerHTML !== oldInnerHTML) {
      element.classList.add("highlight");
    }
  }
  // Improve syntax highlighting in Python examples and source code blocks.
  document
    .querySelectorAll(":is(.language-py, .language-pycon, .quote) code")
    .forEach((element) => highlightCodeBlock(element));
});

/** Returns a list of functions that add reference links to a given element. */
function getReferenceLinkBuilders() {
  const refLinkBuilders = [];
  const isOnline = window.location.href.includes(".io/en/latest/");
  // Regexes and raw URLs for references are defined at the bottom of this file.
  for (const [regexPattern, rawUrl] of referenceLinkUrls) {
    const isLocal = rawUrl.startsWith("/");
    let url = (isOnline && isLocal ? "/en/latest" : "") + rawUrl;
    if (isLocal && window.location.href.includes(url) && !url.includes("#")) {
      url = "#"; // Jump to the top of the current page instead of reloading it.
    }
    // Each list item is a function that modifies the provided element in-place.
    refLinkBuilders.push((element) => {
      for (const match of element.innerHTML.matchAll(regexPattern)) {
        const link = document.createElement("a");
        link.href = url; // Closure.
        link.appendChild(document.createTextNode(match[0]));
        element.innerHTML = element.innerHTML.replace(match[0], link.outerHTML);
      }
    });
  }
  return refLinkBuilders; // Applicable until `window.location.href` changes.
}

/** Improves existing syntax highlighting in the given code block element. */
function highlightCodeBlock(element) {
  // Add color to elements that match the position and text of function names.
  for (const punctuationSpan of element.querySelectorAll("span.p")) {
    if (punctuationSpan.textContent.startsWith("(")) {
      const prevSpan = punctuationSpan.previousElementSibling;
      const isName = prevSpan.className === "n" || prevSpan.className === "fm";
      if (isName && prevSpan.textContent.match(/^[a-z_][a-zA-Z_]*$/)) {
        prevSpan.className = "nf"; // Change to "function" color (pink).
      }
    }
  }
  // Properly color string interpolation characters in Template strings.
  element.innerHTML = element.innerHTML.replaceAll(
    '$</span><span class="si">{',
    '</span><span class="si">${',
  );
  // Recolor class names (explicitly listed below) outside of imports.
  for (const nameSpan of element.querySelectorAll("span.n")) {
    const importSpans = nameSpan.parentElement.querySelectorAll(".kn").length;
    if (importSpans !== 2 && nameSpan.textContent.match(/^(?:[A-Z][a-z]+)+$/)) {
      nameSpan.className = "sx"; // Change to "special" color (red).
    }
  }
}

/** A list of pairs of highlight classes and the regexes they should apply to.
 *  These regexes are written/edited on an as-needed basis & may be fragile.
 */
const highlightPatterns = [
  ["k", /\b(if|return)\b/g],
  ["kc", /\b(None|False|True)\b/g],
  ["m", /^\d+$/g],
  ["nb", /\b(bool|dict|float|list|object|p?r?int|str|t.pl?e)\b(?:[^<]|\]|$)/g],
  ["nb", /^([a-z_][a-zA-Z_]*)\(\)$/g],
  ["nc", /^((?:[A-Z][a-z]+)+)$/g],
  ["o", /(\*+|\|)[^<>]/g],
  ["o", /(=)[^"]/g],
  ["o", /(?:^|\(|, |=)[a-zA-Z_]+(\.)(?!(?:key|py)$)/g],
  ["p", /(?:^|<\/[a-z]+>|\b)({}|,|: |\[+|\]+,?|\(?\)$|}$)/g],
  ["p", /^[a-zA-Z_]+(\().*\)/g],
  ["p", /^(\${).*}/g],
  ["s", /^(?:'.*'|".*")$/g],
  ["s", /[^=]("[^<>]*")[^>]/g],
];

/** A list of pairs of class reference regexes and the URLs they should link to.
 *  These regexes are written/edited on an as-needed basis & may be fragile.
 */ // prettier-ignore
const referenceLinkUrls = [
  // Top-level pages in the Botstrap library documentation.
  [/^Botstrap$/g, "/api/botstrap/"],
  [/^CliColors$/g, "/api/cli-colors/"],
  [/^CliStrings$/g, "/api/cli-strings/"],
  [/^Color$/g, "/api/color/"],
  [/^Option$/g, "/api/option/"],
  [/^Argstrap$/g, "/internal/argstrap/"],
  [/^CliSession$/g, "/internal/cli-session/"],
  [/^Secret$/g, "/internal/secret/"],
  [/\bToken\b/g, "/internal/token/"],
  // Anchors within pages in the Botstrap library documentation.
  [/^CliColors\.default\(\)$/g, "/api/cli-colors/#botstrap.colors.CliColors.default"],
  [/^CliColors\.off\(\)$/g, "/api/cli-colors/#botstrap.colors.CliColors.off"],
  [/^CliStrings\.default\(\)$/g, "/api/cli-strings/#botstrap.strings.CliStrings.default"],
  [/^CliStrings\.compact\(\)$/g, "/api/cli-strings/#botstrap.strings.CliStrings.compact"],
  [/(^Results$|\bOption\.Results\b)/g, "/api/option/#botstrap.options.Option.Results"],
  // Pages and/or anchors in the official Python documentation.
  [/\bAny\b/g, "https://docs.python.org/3/library/typing.html#typing.Any"],
  [/\bCallable\b/g, "https://docs.python.org/3/library/typing.html#typing.Callable"],
  [/\bNamedTuple\b/g, "https://docs.python.org/3/library/typing.html#typing.NamedTuple"],
  [/(pathlib\.)?Path\b/g, "https://docs.python.org/3/library/pathlib.html#concrete-paths"],
  [/(re\.)?Pattern\b/g, "https://docs.python.org/3/library/re.html#regular-expression-objects"],
];
