/** Clarifies constant and inner class headings. No effect on field headings. */
function processHeading(heading) {
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

/** Standardizes numeric (int/float) option coloring in console code spans. */
function processCodeSpan(codeSpan) {
  const match = codeSpan.innerHTML.match(/\$.*?(-\d|\.\d+)/);
  if (match) {
    const replacement = `<span class="m">${match[1]}</span>`;
    codeSpan.innerHTML = codeSpan.innerHTML.replace(match[1], replacement);
  }
}

// Process member headings & code spans to improve clarity on the `Option` page.
if (window.location.href.match(/\/api\/option\//)) {
  for (const heading of document.querySelectorAll("h3.doc-heading > code")) {
    processHeading(heading);
  }
  for (const codeSpan of document.querySelectorAll(
    ".doc-class ~ .doc-class + .example .language-console code > span",
  )) {
    processCodeSpan(codeSpan);
  }
}
