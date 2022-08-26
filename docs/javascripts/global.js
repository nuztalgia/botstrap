// Always expand the "API Reference" nav section.
var navItems = document.querySelectorAll(
  ".md-nav--primary .md-nav__item--nested:not(.md-nav__item--active)",
);
for (var i = 0; i < navItems.length; i++) {
  var navUrl = navItems[i].querySelector("a").getAttribute("href");
  if (navUrl.includes("api/")) {
    navItems[i].querySelector("input.md-toggle").checked = true;
  }
}

// Make clickable grid cards actually work.
var cardItems = document.querySelectorAll(".clickable.grid :is(.card, li)");
for (var i = 0; i < cardItems.length; i++) {
  cardItems[i].addEventListener("click", function (event) {
    var cardDest = event.target.querySelector("h3 > img + a");
    if (cardDest) {
      window.location.href = cardDest.getAttribute("href");
    }
  });
}

// Hide parentheses in property headings.
var docFunctions = document.querySelectorAll(".doc-function");
for (var i = 0; i < docFunctions.length; i++) {
  if (docFunctions[i].querySelector(".doc-label-property")) {
    var docHeading = docFunctions[i].querySelector(".doc-heading");
    docHeading.querySelector("code > .p").style.display = "none";
  }
}

// Returns whether the given element is a source code block.
function isSourceCodeBlock(quoteBlock) {
  var sourceCodeRegex = /Source code in .*\.py/;
  return quoteBlock.querySelector("summary").textContent.match(sourceCodeRegex);
}

// Hide source code blocks containing entire classes.
var docClasses = document.querySelectorAll(".doc-class");
for (var i = 0; i < docClasses.length; i++) {
  var quoteBlocks = docClasses[i].querySelectorAll(".doc-contents.first > .quote");
  for (var j = 0; j < quoteBlocks.length; j++) {
    if (isSourceCodeBlock(quoteBlocks[j])) {
      quoteBlocks[j].style.display = "none";
    }
  }
}

// Hide redundant docstrings and "noinspection" comments in source code blocks.
var quoteBlocks = document.querySelectorAll("details.quote");
for (var i = 0; i < quoteBlocks.length; i++) {
  if (isSourceCodeBlock(quoteBlocks[i])) {
    var lineSpans = quoteBlocks[i].querySelectorAll("pre code > *");
    var inDocString = false;
    for (var j = 0; j < lineSpans.length; j++) {
      var lineText = lineSpans[j].textContent;
      if (lineText.match(/ {4}"{3}(.*\.)?\n/)) {
        inDocString = !inDocString;
      } else if (inDocString || lineText.match(/ *# noinspection /)) {
        lineSpans[j].style.display = "none";
      }
    }
  }
}
