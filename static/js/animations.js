// Animations du site : carte du Backbone, chiffres qui défilent, apparition des cartes.
// Sans JavaScript, ou si le visiteur a demandé à réduire les animations, tout reste affiché normalement.
(function () {
  "use strict";

  var reduire = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduire || !("IntersectionObserver" in window)) return;

  var hauteurEcran = window.innerHeight || document.documentElement.clientHeight;
  function sousLaLigneDeFlottaison(el) {
    return el.getBoundingClientRect().top > hauteurEcran * 0.92;
  }

  // ---------- Chiffres qui défilent ----------
  var formatNombre = new Intl.NumberFormat("fr-FR");

  function animerCompteur(el) {
    var texteFinal = el.getAttribute("data-compteur");
    var cible = parseInt(texteFinal.replace(/[^\d]/g, ""), 10);
    if (!cible) return;
    var noeud = el.firstChild; // le nombre, avant l'éventuelle unité
    var duree = 1600;
    var debut = null;
    function etape(t) {
      if (debut === null) debut = t;
      var p = Math.min((t - debut) / duree, 1);
      var adouci = 1 - Math.pow(1 - p, 3);
      noeud.nodeValue = p < 1 ? formatNombre.format(Math.round(cible * adouci)) : texteFinal;
      if (p < 1) window.requestAnimationFrame(etape);
    }
    window.requestAnimationFrame(etape);
  }

  // ---------- Observateur commun ----------
  var observateur = new IntersectionObserver(function (entrees) {
    entrees.forEach(function (entree) {
      if (!entree.isIntersecting) return;
      var el = entree.target;
      observateur.unobserve(el);
      if (el.hasAttribute("data-compteur")) {
        animerCompteur(el);
      } else if (el.classList.contains("carte-guinee")) {
        el.classList.remove("carte-guinee--attente");
        el.classList.add("carte-guinee--animee");
      } else {
        el.classList.add("revele");
        // Une fois apparue, la carte retrouve son comportement normal (effet de survol compris)
        el.addEventListener("transitionend", function fin(e) {
          if (e.target !== el || e.propertyName !== "opacity") return;
          el.removeEventListener("transitionend", fin);
          el.classList.remove("anime--attente", "revele");
          el.style.removeProperty("--retard");
        });
      }
    });
  }, { threshold: 0.2, rootMargin: "0px 0px -40px 0px" });

  // Carte : le tracé démarre dès qu'elle est visible
  document.querySelectorAll(".carte-guinee").forEach(function (carte) {
    carte.classList.add("carte-guinee--attente");
    observateur.observe(carte);
  });

  // Chiffres : on n'anime que ceux qui ne sont pas encore à l'écran, pour éviter un saut visible
  document.querySelectorAll("[data-compteur]").forEach(function (el) {
    if (el.firstChild && el.firstChild.nodeType === 3) {
      el.firstChild.nodeValue = "0";
      observateur.observe(el);
    }
  });

  // Cartes et blocs : apparition en fondu, décalée pour les éléments d'une même grille
  document.querySelectorAll(".anime").forEach(function (el) {
    if (!sousLaLigneDeFlottaison(el)) return;
    var freres = el.parentElement ? Array.prototype.indexOf.call(el.parentElement.children, el) : 0;
    el.style.setProperty("--retard", Math.min(freres, 5) * 90 + "ms");
    el.classList.add("anime--attente");
    observateur.observe(el);
  });
})();
