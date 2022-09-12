/**
 * @fileoverview Performs a number of visual improvements that are designed to
 * improve clarity, such as removing redundant/irrelevant pieces of code and
 * adding color to example console output. Applies to content on all pages.
 */

document$.subscribe(function () {
  // Remove the "#" comment characters preceding annotations in code blocks.
  for (const comment of document.querySelectorAll(".annotate code span.c1")) {
    if (comment.textContent.match(/# .*?\(\d\)$/)) {
      comment.textContent = comment.textContent.replace(/# .*?\(/, "(");
    }
  }
  // Remove redundant docstrings and irrelevant comments in source code blocks.
  for (const quote of document.querySelectorAll("details.quote")) {
    const summaryText = quote.querySelector("summary").textContent;
    if (summaryText.match(/^Source code in botstrap.*\.py$/)) {
      cleanUpSourceCode(quote.querySelectorAll("pre code > span"));
    }
  }
  // Clean up headings for all functions and remove parentheses for properties.
  for (const docFunction of document.querySelectorAll(".doc-function")) {
    removeDefaultArgs(docFunction);
    removePropertyParens(docFunction);
  }
  // Remove the primary header anchor link and add color to console output text.
  document.querySelector("h1 a.headerlink")?.remove();
  colorConsoleOutput();
});

/** Returns a new element with a class, optionally appending a child node. */
function createElement(tagName, className, content = null) {
  const element = document.createElement(tagName);
  element.className = className;
  if (content) {
    element.appendChild(
      typeof content === "string" ? document.createTextNode(content) : content,
    );
  }
  return element;
}

/** Wraps each string that matches the regex in a <span> of the given class. */
function insertSpans(element, className, regexPattern, unescapeText = false) {
  const getSpanReplacement = (content) => {
    if (unescapeText) {
      content = content.replaceAll("&gt;", ">").replaceAll("&lt;", "<");
    }
    return createElement("span", className, content).outerHTML;
  };
  for (const match of element.innerHTML.matchAll(regexPattern)) {
    const replacement =
      match.length === 1
        ? getSpanReplacement(match[0])
        : match[0].replace(match[1], getSpanReplacement(match[1]));
    element.innerHTML = element.innerHTML.replace(match[0], replacement);
  }
}

/** Removes redundant docstrings & irrelevant comments in source code blocks. */
function cleanUpSourceCode(lineSpans) {
  let inDocString = false;
  for (const lineSpan of lineSpans) {
    if (lineSpan.textContent.match(/ {4}"{3}(.*\.)?\n/)) {
      if (inDocString) {
        return; // End of docstring; all unwanted lines have been hidden.
      } else {
        inDocString = true; // Start hiding unwanted lines at the next line.
      }
    } else if (inDocString || lineSpan.textContent.match(/ *# noinspection /)) {
      lineSpan.remove();
    }
  }
}

/** Removes default arguments in function signature headings. */
function removeDefaultArgs(docFunction) {
  const heading = docFunction.querySelector(".doc-heading code");
  for (const match of heading.innerHTML.matchAll(
    / ?<span class="o">=<\/span>.*?<span class="p">(?:\(\))?(,|\))<\/span>/g,
  )) {
    const replacement = createElement("span", "p", match[1]).outerHTML;
    heading.innerHTML = heading.innerHTML.replace(match[0], replacement);
  }
}

/** Removes parentheses for properties in page nav links and headings. */
function removePropertyParens(docFunction) {
  if (docFunction.querySelector(".doc-label-property")) {
    const navLink = document.querySelector(
      `.md-nav__link[href="#${docFunction.querySelector("h2").id}"]`,
    );
    navLink.textContent = navLink.textContent.replace("()", "");
    docFunction.querySelector(".doc-heading code > .p")?.remove();
  }
}

/** Adds color to certain strings (defined below) in console output elements. */
function colorConsoleOutput() {
  for (const element of document.querySelectorAll(
    ":is(.language-console, .language-pycon):not(.custom-colors) span.go",
  )) {
    for (const [colorName, regexPatterns] of colorPatterns) {
      const unescapeText = colorName === "grey";
      for (const regexPattern of regexPatterns) {
        insertSpans(element, colorName, regexPattern, unescapeText);
      }
    }
  }
  for (const element of document.querySelectorAll(".custom-colors span.go")) {
    insertSpans(element, "cyan", /^cyan-bot/g);
    insertSpans(element, "pink", /"(y(?:es)?)"/g);
  }
}

/** A mapping of color names to regex patterns capturing text to be colored. */
const colorPatterns = Object.entries({
  cyan: [
    /^  (\d)\. .*-&gt;  .*\.\*$/g,
    /^(BOT TOKEN:|PASSWORD:|Enter your password:)/g,
    /"(y(?:es)?|\d)"/g,
    /BotstrapBot#1234/g,
  ],
  green: [
    /^Token successfully deleted\.$/g,
    /^Your token has been .* saved\.$/g,
    /production/g,
  ],
  grey: [
    /^  .*\. .*-&gt;  (.*\.\*)$/g,
    /^Received a [^\.]*\./g,
    / [\*\.]*$/g,
    / Exiting process\.$/g,
    /(&lt;(float|int|str|token id)&gt;)]/g,
  ],
  pink: [/^(?:usage: )?(examplebot)/g],
  red: [/^.* 'exit_process\(\)' function!/g],
  yellow: [
    /^That number doesn't match .* tokens\./g,
    /^Your password must be .* characters long\./g,
    /development/g,
  ],
});
