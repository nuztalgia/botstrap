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
var cardItems = document.querySelectorAll(".clickable.grid .card");
for (var i = 0; i < cardItems.length; i++) {
  cardItems[i].addEventListener("click", function (e) {
    var cardDest = e.target.querySelector("h3 > img + a");
    if (cardDest) {
      window.location.href = cardDest.getAttribute("href");
    }
  });
}
