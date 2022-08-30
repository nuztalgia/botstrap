/** Adds color to text matched by the regex pattern in the given element. */
function colorText(element, color, pattern, index = 1) {
  const match = element.innerHTML.match(pattern);
  if (match) {
    const replacement =
      match.length === 1
        ? `<span class="${color}">${match[0]}</span>`
        : match[0].replace(
            match[index],
            `<span class="${color}">${match[index]}</span>`,
          );
    element.innerHTML = element.innerHTML.replace(match[0], replacement);
  }
}

// Add color to strings that commonly appear in console output.
let outputSpans = document.querySelectorAll(
  ":is(.language-console, .language-pycon):not(.custom-colors) span.go",
);
for (let i = 0; i < outputSpans.length; i++) {
  const span = outputSpans[i];
  colorText(span, "cyan", /^  (\d)\. .*-&gt;  .*\.\*$/);
  colorText(span, "cyan", /^BOT TOKEN:/);
  colorText(span, "cyan", /^Enter your password:/);
  colorText(span, "cyan", /^PASSWORD:/);
  colorText(span, "cyan", /"(yes)"/);
  colorText(span, "cyan", /"(y)"/);
  colorText(span, "cyan", /BasicBot#1234/);
  colorText(span, "cyan", /Expected "(1)" or "2"\.\)$/);
  colorText(span, "cyan", /Expected ".*" or "(2)"\.\)$/);
  colorText(span, "green", /^Token successfully deleted\.$/);
  colorText(span, "green", /^Your token has been .* saved\.$/);
  colorText(span, "green", /production/);
  colorText(span, "grey", /^  .*\. .*-&gt;  (.*\.\*)$/);
  colorText(span, "grey", /^Received a [^\.]*\./);
  colorText(span, "grey", / [\*\.]*$/);
  colorText(span, "grey", / Exiting process\.$/);
  colorText(span, "grey", /(&lt;float&gt;)]/);
  colorText(span, "grey", /(&lt;int&gt;)]/);
  colorText(span, "grey", /(&lt;str&gt;)]/);
  colorText(span, "grey", /(&lt;token id&gt;)]/);
  colorText(span, "pink", /^(usage: )?(examplebot)/, 2);
  colorText(span, "red", /^.* 'exit_process\(\)' function!/);
  colorText(span, "yellow", /^That number doesn't match .* tokens\./);
  colorText(span, "yellow", /^Your password must be .* characters long\./);
  colorText(span, "yellow", /development/);
}

// Same as above, but only for output blocks with the "custom-colors" class.
let customColorSpans = document.querySelectorAll(".custom-colors span.go");
for (let i = 0; i < customColorSpans.length; i++) {
  const span = customColorSpans[i];
  colorText(span, "cyan", /^cyan-bot/);
  colorText(span, "pink", /"(yes)"/);
  colorText(span, "pink", /"(y)"/);
}

// Add the colorful "PRIDE!" console output to the example on the `Color` page.
if (window.location.href.match(/\/api\/color\/$/)) {
  const colorExample = document.querySelector(".admonition.example code");
  colorExample.innerHTML += "<span class='go'>PRIDE!</span>";
  const span = colorExample.querySelector(".go:last-child");
  colorText(span, "pink", /P/);
  colorText(span, "red", /R/);
  colorText(span, "yellow", /I/);
  colorText(span, "green", /D/);
  colorText(span, "cyan", /E/);
  colorText(span, "blue", /!/);
}
