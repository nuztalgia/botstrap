/** Adds color to text matched by the regex pattern in the given element. */
function colorText(element, color, pattern) {
  let matches = element.innerHTML.match(pattern);
  if (matches) {
    let replacement =
      matches.length === 1
        ? `<span class="${color}">${matches[0]}</span>`
        : matches[0].replace(matches[1], `<span class="${color}">${matches[1]}</span>`);
    element.innerHTML = element.innerHTML.replace(matches[0], replacement);
  }
}

// Add color to strings that commonly appear in console output.
var outputSpans = document.querySelectorAll(
  ":is(.language-console, .language-pycon):not(.custom-colors) span.go",
);
for (let i = 0; i < outputSpans.length; i++) {
  let span = outputSpans[i];
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
for (let i = 0; i < customColorSpans.length; i++) {
  let span = customColorSpans[i];
  if (span.innerHTML.includes('If so, type "yes" or "y":')) {
    colorText(span, "pink", /"(yes)"/);
    colorText(span, "pink", /"(y)"/);
  }
  colorText(span, "cyan", /^cyan-bot/);
}

// Add the colorful "PRIDE!" console output to the example on the Color page.
if (window.location.href.match(/\/api\/color\/$/)) {
  let colorExample = document.querySelector(".admonition.example code");
  colorExample.innerHTML += "<span class='go'>PRIDE!</span>";
  let span = colorExample.querySelector(".go:last-child");
  colorText(span, "pink", /P/);
  colorText(span, "red", /R/);
  colorText(span, "yellow", /I/);
  colorText(span, "green", /D/);
  colorText(span, "cyan", /E/);
  colorText(span, "blue", /!/);
}
