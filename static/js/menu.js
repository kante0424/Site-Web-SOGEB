// Ouverture et fermeture du menu sur mobile
(function () {
  var bouton = document.querySelector(".menu-bouton");
  var menu = document.getElementById("menu-principal");
  if (!bouton || !menu) return;
  bouton.addEventListener("click", function () {
    var ouvert = bouton.getAttribute("aria-expanded") === "true";
    bouton.setAttribute("aria-expanded", String(!ouvert));
    menu.classList.toggle("menu--ouvert", !ouvert);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && menu.classList.contains("menu--ouvert")) {
      bouton.setAttribute("aria-expanded", "false");
      menu.classList.remove("menu--ouvert");
      bouton.focus();
    }
  });
})();
