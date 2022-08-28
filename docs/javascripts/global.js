/** Returns `true` if the given element is a source code block. */
function isSourceCodeBlock(element) {
  let pattern = /^Source code in <code>botstrap.*\.py<\/code>$/;
  return element.querySelector("summary").innerHTML.match(pattern);
}

// Hide redundant docstrings and "noinspection" comments in source code blocks.
var quoteBlocks = document.querySelectorAll("details.quote");
for (let i = 0; i < quoteBlocks.length; i++) {
  if (isSourceCodeBlock(quoteBlocks[i])) {
    let lineSpans = quoteBlocks[i].querySelectorAll("pre code > *");
    let inDocString = false;
    for (let j = 0; j < lineSpans.length; j++) {
      let lineText = lineSpans[j].textContent;
      if (lineText.match(/ {4}"{3}(.*\.)?\n/)) {
        inDocString = !inDocString;
      } else if (inDocString || lineText.match(/ *# noinspection /)) {
        lineSpans[j].style.display = "none";
      }
    }
  }
}

// Hide source code blocks that contain *entire* classes.
var docClasses = document.querySelectorAll(".doc-class");
for (let i = 0; i < docClasses.length; i++) {
  let quoteBlocks = docClasses[i].querySelectorAll(".doc-contents.first > .quote");
  for (let j = 0; j < quoteBlocks.length; j++) {
    if (isSourceCodeBlock(quoteBlocks[j])) {
      quoteBlocks[j].style.display = "none";
    }
  }
}

// Hide parentheses in "function" headings for properties.
var docFunctions = document.querySelectorAll(".doc-function");
for (let i = 0; i < docFunctions.length; i++) {
  if (docFunctions[i].querySelector(".doc-label-property")) {
    let docHeading = docFunctions[i].querySelector(".doc-heading");
    docHeading.querySelector("code > .p").style.display = "none";
  }
}

// Make clickable grid cards actually work.
var cardElements = document.querySelectorAll(".clickable.grid :is(.card, li)");
for (let i = 0; i < cardElements.length; i++) {
  cardElements[i].addEventListener("click", function (event) {
    let cardTargetLink = event.target.querySelector("h3 > img + a");
    if (cardTargetLink) {
      window.location.href = cardTargetLink.getAttribute("href");
    }
  });
}
