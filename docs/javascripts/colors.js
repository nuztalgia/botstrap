/** Adds color to all text matched by the regex pattern in the bound element. */
function colorElementText(colorName, regexPattern, replacementIndex = 1) {
  for (const match of this.innerHTML.matchAll(new RegExp(regexPattern, "g"))) {
    const replacement =
      match.length === 1
        ? `<span class="${colorName}">${match[0]}</span>`
        : match[0].replace(
            match[replacementIndex],
            `<span class="${colorName}">${match[replacementIndex]}</span>`,
          );
    this.innerHTML = this.innerHTML.replace(match[0], replacement);
  }
}

// Add color to strings that commonly appear in console output.
const selector = ":is(.language-console, .language-pycon):not(.custom-colors)";
for (const element of document.querySelectorAll(selector + " span.go")) {
  const colorText = colorElementText.bind(element);
  colorText("cyan", /^  (\d)\. .*-&gt;  .*\.\*$/);
  colorText("cyan", /^(BOT TOKEN|PASSWORD|Enter your password):/, 0);
  colorText("cyan", /"(y(es)?|\d)"/);
  colorText("cyan", /BasicBot#1234/);
  colorText("green", /^Token successfully deleted\.$/);
  colorText("green", /^Your token has been .* saved\.$/);
  colorText("green", /production/);
  colorText("grey", /^  .*\. .*-&gt;  (.*\.\*)$/);
  colorText("grey", /^Received a [^\.]*\./);
  colorText("grey", / [\*\.]*$/);
  colorText("grey", / Exiting process\.$/);
  colorText("grey", /(&lt;(float|int|str|token id)&gt;)]/);
  colorText("pink", /^(usage: )?(examplebot)/, 2);
  colorText("red", /^.* 'exit_process\(\)' function!/);
  colorText("yellow", /^That number doesn't match .* tokens\./);
  colorText("yellow", /^Your password must be .* characters long\./);
  colorText("yellow", /development/);
}

// Same as above, but only for output blocks with the "custom-colors" class.
for (const element of document.querySelectorAll(".custom-colors span.go")) {
  const colorText = colorElementText.bind(element);
  colorText("cyan", /^cyan-bot/);
  colorText("pink", /"(y(es)?)"/);
}

// Add the colorful "PRIDE!" console output to the example on the `Color` page.
if (window.location.href.match(/\/api\/color\//)) {
  const prideExample = document.querySelector(".admonition.example code");
  prideExample.innerHTML += "<span class='go'>PRIDE!</span>";
  const colorText = colorElementText.bind(prideExample.querySelector(".go"));
  colorText("pink", /P/);
  colorText("red", /R/);
  colorText("yellow", /I/);
  colorText("green", /D/);
  colorText("cyan", /E/);
  colorText("blue", /!/);
}
