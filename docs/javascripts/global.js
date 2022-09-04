document$.subscribe(function () {
  // Remove the "#" comment characters preceding annotations in code blocks.
  for (const comment of document.querySelectorAll(".annotate code span.c1")) {
    if (comment.innerHTML.match(/# .*?\(\d\)$/)) {
      comment.innerHTML = comment.innerHTML.replace(/# .*?\(/, "(");
    }
  }
  // Remove redundant docstrings and irrelevant comments in source code blocks.
  const sourceCodeSummary = /^Source code in <code>botstrap.*\.py<\/code>$/;
  for (const quote of document.querySelectorAll("details.quote")) {
    if (quote.querySelector("summary").innerHTML.match(sourceCodeSummary)) {
      cleanUpSourceCode(quote.querySelectorAll("pre code > span"));
    }
  }
  // Clean up headings for all functions and remove parentheses for properties.
  for (const docFunction of document.querySelectorAll(".doc-function")) {
    removeDefaultArgs(docFunction);
    removePropertyParens(docFunction);
  }
  // Run custom logic for specific pages if the current location matches up.
  if (window.location.href.match(/\/(api|internal)\/$/)) {
    handleReferencePage();
  }
  if (window.location.href.match(/\/api\/option\//)) {
    handleOptionPage();
  }
  // Remove the title header anchor link on every page.
  document.querySelector("h1 a.headerlink")?.remove();
});

/** Removes redundant docstrings & irrelevant comments in source code blocks. */
function cleanUpSourceCode(lineSpans) {
  let inDocString = false;
  for (const lineSpan of lineSpans) {
    if (lineSpan.textContent.match(/ {4}"{3}(.*\.)?\n/)) {
      inDocString = !inDocString;
    } else if (inDocString || lineSpan.textContent.match(/ *# noinspection /)) {
      lineSpan.remove();
    }
  }
}

/** Removes default arguments in function signature headings. */
function removeDefaultArgs(docFunction) {
  const heading = docFunction.querySelector(".doc-heading code");
  for (const match of heading.innerHTML.matchAll(
    / ?<span class="o">=<\/span>.*?<span class="p">(\(\))?(,|\))<\/span>/g,
  )) {
    const replacement = `<span class="p">${match[2]}</span>`;
    heading.innerHTML = heading.innerHTML.replace(match[0], replacement);
  }
}

/** Removes parentheses for properties in page nav links and headings. */
function removePropertyParens(docFunction) {
  if (docFunction.querySelector(".doc-label-property")) {
    const navLink = document.querySelector(
      `.md-nav__link[href="#${docFunction.querySelector("h2").id}"]`,
    );
    navLink.innerHTML = navLink.innerHTML.replace(/\(\)/, "");
    docFunction.querySelector(".doc-heading code > .p")?.remove();
  }
}

/** Execute special logic on "API Reference" and "Internal Reference" pages. */
function handleReferencePage() {
  // Remove all header anchor links.
  for (const link of document.querySelectorAll(".md-typeset a.headerlink")) {
    link.remove();
  }
  // Follow the first detected link when a card in a clickable grid is clicked.
  for (const cardElement of document.querySelectorAll(
    ".clickable.grid :is(.card, li)",
  )) {
    cardElement.addEventListener("click", function (event) {
      const destination = event.target.querySelector("a")?.getAttribute("href");
      window.location.href = destination ?? window.location.href;
    });
  }
}

/** Execute special logic to improve clarity on the "Option" page. */
function handleOptionPage() {
  for (const heading of document.querySelectorAll("h3.doc-heading > code")) {
    processOptionHeading(heading);
  }
  // Standardize numeric (int/float) option coloring in console code spans.
  for (const codeSpan of document.querySelectorAll(
    ".doc-class ~ .doc-class + .example .language-console code > span",
  )) {
    const match = codeSpan.innerHTML.match(/\$.*?(-\d|\.\d+)/);
    if (match) {
      const replacement = `<span class="m">${match[1]}</span>`;
      codeSpan.innerHTML = codeSpan.innerHTML.replace(match[1], replacement);
    }
  }
}

/** Clarifies constant and inner class headings for the "Option" class. */
function processOptionHeading(heading) {
  if (heading.innerText.match(/^[a-z_]*: /)) {
    // This is a field heading. No need for special processing.
    return;
  }
  // This is a constant or inner class heading. Prepend the outer class name.
  heading.innerHTML = `Option.${heading.innerHTML}`;
  // Additional processing for constant headings: Remove the default value.
  if (heading.innerText.match(/^Option.[A-Z_]*: /)) {
    heading.innerHTML = heading.innerHTML.replace(/ <span class="o">=.*$/, "");
  }
}
