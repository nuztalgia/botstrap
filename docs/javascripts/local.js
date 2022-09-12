/**
 * @fileoverview Executes logic that is tailored to a specific page. May include
 * visual and behavioral changes. Only applies when the URL of the current page
 * matches a regex corresponding to a custom handler function (defined below).
 */

document$.subscribe(function () {
  // Run custom logic if the url matches the pattern for a specific page.
  for (const [urlPattern, customHandler] of [
    ["/(api|internal)/$", handleReferencePage],
    ["/api/cli-strings/", handleStringsPage],
    ["/api/color/", handleColorPage],
    ["/api/option/", handleOptionPage],
  ]) {
    if (window.location.href.match(urlPattern)) {
      customHandler();
    }
  }
});

/** Executes custom logic to complete the example on the "Color" page. */
function handleColorPage() {
  const outputSpan = document
    .querySelector(".admonition.example code")
    .appendChild(document.createElement("span"))
    .appendChild(createElement("span", "go"));
  // prettier-ignore
  const outputCharacters = Object.entries({
    pink: "P", red: "R", yellow: "I", green: "D", cyan: "E", blue: "!",
  });
  // Add the colorful "PRIDE!" console output to the end of the example.
  for (const [colorClass, outputCharacter] of outputCharacters) {
    outputSpan.appendChild(createElement("span", colorClass, outputCharacter));
  }
}

/** Executes custom logic to improve clarity on the "Option" page. */
function handleOptionPage() {
  for (const heading of document.querySelectorAll("h3.doc-heading > code")) {
    if (!heading.textContent.match(/^[a-z_]*: /)) {
      // This is a constant or inner class heading. Prepend the main class name.
      const classNameNode = document.createTextNode("Option.");
      heading.insertBefore(classNameNode, heading.firstChild);
    }
    // Additional processing for constant headings: Remove the default value.
    if (heading.textContent.match(/^Option.[A-Z_]*: /)) {
      heading.innerHTML = heading.innerHTML.replace(/ <span class="o">=.*/, "");
    }
  }
  document // Standardize numeric argument coloring in the "Results" example.
    .querySelectorAll("h2#nested-classes ~ .example .language-console code > *")
    .forEach((lineSpan) => insertSpans(lineSpan, "m", /\$ .*?(-\d|\.\d+)/g));
}

/** Executes custom logic on "API Reference" and "Internal Reference" pages. */
function handleReferencePage() {
  document // Remove all header anchor links.
    .querySelectorAll(".md-typeset a.headerlink")
    .forEach((linkElement) => linkElement.remove());
  document // Follow the first link when a card in a clickable grid is clicked.
    .querySelectorAll(".clickable.grid :is(.card, li)")
    .forEach((clickableCardElement) => {
      const onClick = () => clickableCardElement.querySelector("a")?.click();
      clickableCardElement.addEventListener("click", onClick);
    });
}

/** Executes custom logic to create a dynamic table on the "CliStrings" page. */
function handleStringsPage() {
  const tableData = []; // First, populate this list by parsing the source code.
  const sourceContent = document.querySelector(".note pre > code").textContent;
  const groupMatches = Array.from(
    sourceContent.matchAll(/#(?: -)*\n\n((?:.*\n?)*?)(?:\n#(?: -)*|$)/g),
  );
  for (let i = 0; i < groupMatches.length; i++) {
    const groupNumber = i + 1;
    // Match individual fields by a regex depending on the current group number.
    for (const fieldMatch of groupMatches[i][1].matchAll(
      groupNumber === groupMatches.length
        ? /([a-z_]+): (tuple)\[.*\] = (\(".*"\))/g // Last group is tuples only.
        : /([a-z_]+): (T?[a-z]+) = .*\(?\n?((?:\n? *(?:".*")|(?:\n? *'.*'))+)/g,
    )) {
      // Add the information for each field to the list holding all of the data.
      const fieldValue = fieldMatch[3].trim().replaceAll('"\n    "', "");
      tableData.push([groupNumber, fieldMatch[1], fieldMatch[2], fieldValue]);
    }
  }
  // After the data is ready, prepare the table and then plug it all in.
  const tableRoot = document.querySelector(".note .md-typeset__table table");
  const tableBody = tableRoot.querySelector("tbody");
  tableBody.querySelector("tr").remove(); // Remove the placeholder table row.
  for (const rowData of tableData) {
    const tableRow = document.createElement("tr");
    rowData.forEach(addStringsTableCell, tableRow);
    tableBody.appendChild(tableRow);
  }
  new Tablesort(tableRoot); // Make the entire table sortable.
  document // Minor footnote - highlight Template placeholders in the example.
    .querySelectorAll(".example > .language-py code span.s2")
    .forEach((stringSpan) => insertSpans(stringSpan, "si", /\$[a-z_]+/g));
}

/** Creates a table cell with the given data and appends it to the bound row. */
function addStringsTableCell(cellData, cellIndex) {
  const tableCell = document.createElement("td");
  const textNode = document.createTextNode(cellData);
  if (cellIndex === 0) {
    tableCell.appendChild(textNode); // No code formatting for the group number.
  } else {
    const codeElement = document.createElement("code");
    if (cellIndex === 1) {
      codeElement.appendChild(textNode); // No need to highlight the field name.
    } else {
      codeElement.className = "highlight no-pylight";
      const spanElement = createElement("span", "s", textNode);
      if (cellIndex === 2) {
        // Simple highlighting for the field type (class name or built-in name).
        spanElement.className = cellData === "Template" ? "nc" : "nb";
      } else {
        // More complex highlighting (using regex matching) for the field value.
        Object.entries({
          m: /[^>]((?:\\n)+)/g, // Newline characters.
          p: /(?:^\(|\)$|\${[a-z_]+})/g, // Tuple/placeholder containers.
          n: /\${([a-z_]+)}/g, // Placeholder names.
          o: /(?:[^^]")(,)(?: "[^$])/g, // Commas in tuples.
        }).forEach((entry) => insertSpans(spanElement, ...entry));
      }
      codeElement.appendChild(spanElement);
    }
    tableCell.appendChild(codeElement);
  }
  this.appendChild(tableCell); // Append the table cell to the bound table row.
}
