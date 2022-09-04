/**
 * @fileoverview Executes logic that is tailored to a specific page. May include
 * visual and behavioral changes. Only applies when the URL of the current page
 * matches a regex corresponding to a custom handler function (defined below).
 */

document$.subscribe(function () {
  // Run custom logic if the url matches the pattern for a specific page.
  for (const [urlPattern, customHandler] of Object.entries({
    "/(api|internal)/$": handleReferencePage,
    "/api/color/": handleColorPage,
    "/api/option/": handleOptionPage,
  })) {
    if (window.location.href.match(urlPattern)) {
      customHandler();
    }
  }
});

/** Executes custom logic on "API Reference" and "Internal Reference" pages. */
function handleReferencePage() {
  // Remove all header anchor links.
  for (const link of document.querySelectorAll(".md-typeset a.headerlink")) {
    link.remove();
  }
  // Follow the first detected link when a card in a clickable grid is clicked.
  for (const cardElement of document.querySelectorAll(
    ".clickable.grid :is(.card, li)",
  )) {
    cardElement.addEventListener("click", function () {
      cardElement.querySelector("a")?.click();
    });
  }
}

/** Executes custom logic to complete the example on the "Color" page. */
function handleColorPage() {
  // Append the colorful "PRIDE!" console output to the end of the example.
  document.querySelector(".admonition.example code").innerHTML +=
    '<span class="pink">P</span><span class="red">R</span>' +
    '<span class="yellow">I</span><span class="green">D</span>' +
    '<span class="cyan">E</span><span class="blue">!</span>';
}

/** Executes custom logic to improve clarity on the "Option" page. */
function handleOptionPage() {
  for (const heading of document.querySelectorAll("h3.doc-heading > code")) {
    processOptionHeading(heading);
  }
  // Standardize numeric (int/float) option coloring in console code spans.
  for (const codeSpan of document.querySelectorAll(
    ".doc-class ~ .doc-class + .example .language-console code > span",
  )) {
    if ((match = codeSpan.innerHTML.match(/\$.*?(-\d|\.\d+)/))) {
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
