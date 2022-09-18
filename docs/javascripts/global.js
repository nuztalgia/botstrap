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
  // Clean up headings for all functions and remove parentheses for properties.
  for (const docFunction of document.querySelectorAll(".doc-function")) {
    removeDefaultArgs(docFunction);
    removePropertyParens(docFunction);
  }
  // Remove the 1st anchor link and process source code & console output blocks.
  document.querySelector("h1 a.headerlink")?.remove();
  processSourceCode();
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

/** Adds a GitHub link and removes irrelevant elements in source code blocks. */
function processSourceCode() {
  const repoUrl = document.querySelector(".md-header__source > a").href;
  const getLine = (lineSpan) => lineSpan.id.match(/^line-\d-(\d+)$/)[1];
  for (const element of document.querySelectorAll("details.quote")) {
    const summaryText = element.querySelector("summary").textContent;
    const match = summaryText.match(/^Source code in ([\w\/\\]+\.[a-z]+)$/);
    if (match) {
      const lineSpans = element.querySelectorAll("pre > code > span");
      const button = createElement("button", "md-icon source-link-button");
      button.title = "View source on GitHub";
      const link = createElement("a", "source-link", button);
      link.href =
        `${repoUrl}/tree/main/${encodeURI(match[1].replaceAll("\\", "/"))}#L` +
        `${getLine(lineSpans[0])}-L${getLine(lineSpans[lineSpans.length - 1])}`;
      element.querySelector("pre > :first-child").after(link);
      element.querySelector("span.filename").remove();
      removeSourceCodeDocs(lineSpans);
    }
  }
}

/** Removes redundant docstring lines in source code blocks. */
function removeSourceCodeDocs(lineSpans) {
  let inDocString = false;
  for (const lineSpan of lineSpans) {
    if (lineSpan.textContent.startsWith('    """')) {
      if (lineSpan.textContent.endsWith(".\n")) {
        inDocString = true; // First line of docstring; remove subsequent lines.
      } else {
        return; // End of docstring; all unwanted lines have been removed.
      }
    } else if (inDocString) {
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

/** Adds color to certain strings (defined below) in console output lines. */
function colorConsoleOutput() {
  for (const element of document.querySelectorAll(
    ":is(.language-console, .language-pycon):not(.custom-colors) span.go",
  )) {
    const match = element.textContent.match(/(?:,|:) ([a-z01\.]+|(?:doo ?)+)$/);
    if (match) {
      element.textContent = element.textContent.slice(0, match.index + 2);
      element.after(document.createTextNode(match[1])); // Move user input out.
    }
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
    /^  (\d)\. .+ +-&gt;  ~\/[a-z\/]+\.botstrap_keys\/\.[a-z]+\.\*$/g,
    /^(?:BOT TOKEN|PASSWORD|Enter your password):/g,
    /"(y(?:es)?|\d)"/g,
    /BotstrapBot#1234/g,
  ],
  green: [
    /^Token successfully deleted\.$/g,
    /^Your token has been successfully encrypted and saved\.$/g,
    /production/g,
  ],
  grey: [
    /^  .+\. .+ +-&gt;  (~\/[a-z\/]+\.botstrap_keys\/\.[a-z]+\.\*)$/g,
    /^Received a non-affirmative response\./g,
    / [\*\.]+$/g,
    / Exiting process\.$/g,
    /(&lt;(?:float|int|str|token id)&gt;)\]/g,
  ],
  pink: [/^(?:usage: )?(examplebot)/g],
  red: [/^Just testing the 'exit_process\(\)' function!/g],
  yellow: [
    /^That number doesn't match any of the above tokens\./g,
    /^Your password must be at least \d characters long\./g,
    /development/g,
  ],
});
