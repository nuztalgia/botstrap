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

// Adds color to text matched by the regex pattern in the given element.
function colorText(element, color, pattern) {
  var matches = element.innerHTML.match(pattern);
  if (matches && matches.length == 1) {
    element.innerHTML = element.innerHTML.replace(
      matches[0],
      `<span class="${color}">${matches[0]}</span>`,
    );
  } else if (matches && matches.length == 2) {
    element.innerHTML = element.innerHTML.replace(
      matches[0],
      matches[0].replace(matches[1], `<span class="${color}">${matches[1]}</span>`),
    );
  }
}

// Add color to strings that commonly appear in console output.
var outputSpans = document.querySelectorAll(
  ":is(.language-console, .language-pycon):not(.custom-colors) span.go",
);
for (var i = 0; i < outputSpans.length; i++) {
  var span = outputSpans[i];
  if (span.innerHTML.includes('If so, type "yes" or "y":')) {
    colorText(span, "cyan", /"(yes)"/);
    colorText(span, "cyan", /"(y)"/);
  }
  colorText(span, "cyan", /^  (\d)\. .*-&gt;  .*\.\*$/);
  colorText(span, "cyan", /^BOT TOKEN:/);
  colorText(span, "cyan", /^Enter your password:/);
  colorText(span, "cyan", /BasicBot#1234/);
  colorText(span, "cyan", /Expected "(1)" or "2"\.\)$/);
  colorText(span, "cyan", /Expected ".*" or "(2)"\.\)$/);
  colorText(span, "green", /^Token successfully deleted\.$/);
  colorText(span, "green", /^Your token has been .* saved\.$/);
  colorText(span, "grey", /^  .*\. .*-&gt;  (.*\.\*)$/);
  colorText(span, "grey", /^Received a [^\.]*\./);
  colorText(span, "grey", / Exiting process\.$/);
  colorText(span, "grey", /(&lt;float&gt;)]/);
  colorText(span, "grey", /(&lt;int&gt;)]/);
  colorText(span, "grey", /(&lt;str&gt;)]/);
  colorText(span, "grey", /(&lt;token id&gt;)]/);
  colorText(span, "pink", /^example-bot/);
  colorText(span, "pink", /^usage: (\S*) /);
  colorText(span, "red", /^.* 'exit_process\(\)' function!/);
  colorText(span, "yellow", /^That number doesn't match .* tokens\./);
  colorText(span, "yellow", /development/);
}

// Same as above, but only for output blocks with the "custom-colors" class.
var customColorSpans = document.querySelectorAll(".custom-colors span.go");
for (var i = 0; i < customColorSpans.length; i++) {
  var span = customColorSpans[i];
  if (span.innerHTML.includes('If so, type "yes" or "y":')) {
    colorText(span, "pink", /"(yes)"/);
    colorText(span, "pink", /"(y)"/);
  }
  colorText(span, "cyan", /cyan-bot/);
}
