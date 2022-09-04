/** Adds color to console output text on the current page, if applicable. */
function colorConsoleOutput() {
  // Add color to certain strings that appear in console output (defined below).
  for (const element of document.querySelectorAll(
    ":is(.language-console, .language-pycon):not(.custom-colors) span.go",
  )) {
    for (const [colorName, regexPatterns] of Object.entries(colorPatterns)) {
      for (const regexPattern of regexPatterns) {
        addColorByRegex(element, colorName, regexPattern);
      }
    }
  }
  // Same as above, but only for output blocks with the "custom-colors" class.
  for (const element of document.querySelectorAll(".custom-colors span.go")) {
    addColorByRegex(element, "cyan", /^cyan-bot/g);
    addColorByRegex(element, "pink", /"(y(es)?)"/g);
  }
  // Add the "PRIDE!" console output to the example on the `Color` page.
  if (window.location.href.match(/\/api\/color\//)) {
    document.querySelector(".admonition.example code").innerHTML +=
      '<span class="pink">P</span><span class="red">R</span>' +
      '<span class="yellow">I</span><span class="green">D</span>' +
      '<span class="cyan">E</span><span class="blue">!</span>';
  }
}

/** Adds color to all text matched by the regex pattern in the bound element. */
function addColorByRegex(element, colorName, regexPattern) {
  for (const match of element.innerHTML.matchAll(regexPattern)) {
    const colorSpan = `<span class="${colorName}">`;
    const replacement =
      match.length == 1
        ? `${colorSpan}${match[0]}</span>`
        : match[0].replace(match[1], `${colorSpan}${match[1]}</span>`);
    element.innerHTML = element.innerHTML.replace(match[0], replacement);
  }
}

/** A mapping of color names to the regex patterns for text to be colored. */
const colorPatterns = {
  cyan: [
    /^  (\d)\. .*-&gt;  .*\.\*$/g,
    /^(BOT TOKEN:|PASSWORD:|Enter your password:)/g,
    /"(y(es)?|\d)"/g,
    /BotstrapBot#1234/g,
  ],
  green: [
    /^Token successfully deleted\.$/g,
    /^Your token has been .* saved\.$/g,
    /production/g,
  ],
  grey: [
    /^  .*\. .*-&gt;  (.*\.\*)$/g,
    /^Received a [^\.]*\./g,
    / [\*\.]*$/g,
    / Exiting process\.$/g,
    /(&lt;(float|int|str|token id)&gt;)]/g,
  ],
  pink: [/^(?:usage: )?(examplebot)/g],
  red: [/^.* 'exit_process\(\)' function!/g],
  yellow: [
    /^That number doesn't match .* tokens\./g,
    /^Your password must be .* characters long\./g,
    /development/g,
  ],
};

// Call the main function for this file.
colorConsoleOutput();
