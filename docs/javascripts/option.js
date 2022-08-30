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

// Process class member headings to improve clarity on the `Option` page.
if (window.location.href.match(/\/api\/option\//)) {
  const memberHeadings = document.querySelectorAll("h3.doc-heading > code");
  for (let i = 0; i < memberHeadings.length; i++) {
    processHeading(memberHeadings[i]);
  }
}
