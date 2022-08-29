/** Returns `true` if the given element is a source code block. */
function isSourceCodeBlock(element) {
  const pattern = /^Source code in <code>botstrap.*\.py<\/code>$/;
  return element.querySelector("summary").innerHTML.match(pattern);
}

// Remove redundant docstrings and irrelevant comments in source code blocks.
let quoteBlocks = document.querySelectorAll("details.quote");
for (let i = 0; i < quoteBlocks.length; i++) {
  if (isSourceCodeBlock(quoteBlocks[i])) {
    const lineSpans = quoteBlocks[i].querySelectorAll("pre code > *");
    let inDocString = false;
    for (let j = 0; j < lineSpans.length; j++) {
      const lineText = lineSpans[j].textContent;
      if (lineText.match(/ {4}"{3}(.*\.)?\n/)) {
        inDocString = !inDocString;
      } else if (inDocString || lineText.match(/ *# noinspection /)) {
        lineSpans[j].remove();
      }
    }
  }
}

// Remove parentheses for properties in page navigation links and headings.
let docFunctions = document.querySelectorAll(".doc-function");
for (let i = 0; i < docFunctions.length; i++) {
  if (docFunctions[i].querySelector(".doc-label-property")) {
    const pageNavLink = document.querySelector(
      `.md-nav__link[href="#${docFunctions[i].querySelector("h2").id}"]`,
    );
    pageNavLink.innerHTML = pageNavLink.innerHTML.replace(/\(\)/, "");
    const docHeading = docFunctions[i].querySelector(".doc-heading");
    docHeading.querySelector("code > .p").remove();
  }
}

// Remove the title header anchor link on every page.
let titleHeaderLink = document.querySelector("h1 a.headerlink");
if (titleHeaderLink) {
  titleHeaderLink.remove();
}

// Remove all header anchor links on reference index pages.
if (window.location.href.match(/\/(api|internal)\/$/)) {
  const headerLinks = document.querySelectorAll(".md-typeset a.headerlink");
  for (let i = 0; i < headerLinks.length; i++) {
    headerLinks[i].remove();
  }
}

// Follow the first detected link when a card in a clickable grid is clicked.
let cardElements = document.querySelectorAll(".clickable.grid :is(.card, li)");
for (let i = 0; i < cardElements.length; i++) {
  cardElements[i].addEventListener("click", function (event) {
    const cardTargetLink = event.target.querySelector("a");
    if (cardTargetLink) {
      window.location.href = cardTargetLink.getAttribute("href");
    }
  });
}
