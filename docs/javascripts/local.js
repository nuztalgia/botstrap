/**
 * @fileoverview Executes logic that is tailored to a specific page. May include
 * visual and behavioral changes. Only applies when the URL of the current page
 * matches a regex corresponding to a custom handler function (defined below).
 */

document$.subscribe(function () {
  // Run custom logic if the url matches the pattern for a specific page.
  for (const [urlPattern, customHandler] of Object.entries({
    "/(api|internal)/$": handleReferencePage,
    "/api/cli-strings/": handleStringsPage,
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

/** Executes custom logic to create a dynamic table on the "CliStrings" page. */
function handleStringsPage() {
  const tableData = []; // First, populate this data by parsing the source code.
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
    for (let i = 0; i < rowData.length; i++) {
      const tableCell = document.createElement("td");
      tableCell.appendChild(getStringsCellContent(i, rowData[i]));
      tableRow.appendChild(tableCell);
    }
    tableBody.appendChild(tableRow);
  }
  new Tablesort(tableRoot); // Make the entire table sortable.
}

/** Returns a node/element to put in a table cell for the "CliStrings" class. */
function getStringsCellContent(cellIndex, cellData) {
  const textNode = document.createTextNode(cellData);
  if (cellIndex === 0) {
    return textNode; // No special formatting for the group number.
  }
  const codeElement = document.createElement("code");
  if (cellIndex === 1) {
    codeElement.appendChild(textNode); // No need to highlight the field name.
  } else {
    codeElement.classList.add("highlight"); // Highlight the field type & value.
    const spanElement = document.createElement("span");
    spanElement.appendChild(textNode);
    if (cellIndex === 2) {
      // Simple highlighting for the field type (class name or built-in name).
      spanElement.classList.add(cellData === "Template" ? "nc" : "nb");
    } else {
      // More complex highlighting based on regex matching for the field value.
      spanElement.classList.add("s");
      insertSpans(spanElement, "m", /[^>]((?:\\n)+)/g);
      insertSpans(spanElement, "o", /\${[a-z_]+}/g);
      insertSpans(spanElement, "p", /(?:^\(|\)$)/g);
      insertSpans(spanElement, "p", /(?:[^^]")(,)(?: "[^$])/g);
    }
    codeElement.appendChild(spanElement);
  }
  return codeElement;
}

/** Wraps each string that matches the regex in a <span> of the given class. */
function insertSpans(containerElement, spanClassName, regexPattern) {
  for (const match of containerElement.innerHTML.matchAll(regexPattern)) {
    const newSpan = document.createElement("span");
    newSpan.classList.add(spanClassName);
    let newHTML;
    if (match.length === 1) {
      newSpan.appendChild(document.createTextNode(match[0]));
      newHTML = newSpan.outerHTML;
    } else {
      newSpan.appendChild(document.createTextNode(match[1]));
      newHTML = match[0].replace(match[1], newSpan.outerHTML);
    }
    newHTML = containerElement.innerHTML.replace(match[0], newHTML);
    containerElement.innerHTML = newHTML;
  }
}
