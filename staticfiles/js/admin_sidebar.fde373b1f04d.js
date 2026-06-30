/**
 * admin_sidebar.js
 *
 * Améliorations UI/UX de la sidebar d'administration :
 * - Filtre de recherche dynamique des modules
 * - Mise en surbrillance du lien actif selon l'URL courante
 * - Gestion ARIA (sections dépliables)
 *
 * Sécurité : ce script n'accède qu'au DOM et au localStorage du navigateur.
 * Aucune requête réseau, aucun eval. Le contenu utilisateur n'est jamais
 * inséré via innerHTML (seulement via textContent).
 */

(function () {
  "use strict";

  /**
   * Normalise une chaîne pour la recherche insensible aux accents et à la casse.
   * @param {string} str
   * @returns {string}
   */
  function normalize(str) {
    if (!str) return "";
    return str
      .toString()
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
  }

  /**
   * Filtre les sections de la sidebar en fonction du texte saisi.
   * - Cache les sections dont aucun lien ne correspond.
   * - Déplie automatiquement les sections qui contiennent des correspondances.
   * - Restaure l'état initial lorsque le champ est vide.
   */
  function initSidebarFilter() {
    const input = document.getElementById("sidebar-filter");
    if (!input) return;

    const sidebar = document.getElementById("sidebar");
    if (!sidebar) return;

    const sections = Array.from(sidebar.querySelectorAll(".nav-section"));
    const linksBySection = sections.map(function (section) {
      return Array.from(section.querySelectorAll(".nav-link")).map(function (
        link
      ) {
        return {
          link: link,
          text: normalize(link.textContent || ""),
        };
      });
    });

    function applyFilter() {
      const query = normalize(input.value);
      let visibleCount = 0;

      sections.forEach(function (section, index) {
        const links = linksBySection[index];
        let sectionHasMatch = !query;

        links.forEach(function (entry) {
          const match = !query || entry.text.indexOf(query) !== -1;
          entry.link.style.display = match ? "" : "none";
          if (match && query) sectionHasMatch = true;
        });

        const content = section.querySelector(".nav-section-content");
        const button = section.querySelector(".nav-section-header");

        if (query && sectionHasMatch) {
          section.style.display = "";
          if (content) content.classList.add("open");
          if (button) button.setAttribute("aria-expanded", "true");
          section.classList.add("open");
          visibleCount += 1;
        } else if (query) {
          section.style.display = "none";
        } else {
          section.style.display = "";
        }
      });

      let empty = document.getElementById("sidebar-filter-empty");
      if (query && visibleCount === 0) {
        if (!empty) {
          empty = document.createElement("p");
          empty.id = "sidebar-filter-empty";
          empty.className =
            "px-3 py-2 text-sm text-gray-500 dark:text-gray-400";
          empty.textContent = "Aucun module ne correspond à votre recherche.";
          sidebar.querySelector("nav").appendChild(empty);
        }
        empty.style.display = "";
      } else if (empty) {
        empty.style.display = "none";
      }
    }

    input.addEventListener("input", applyFilter);
  }

  /**
   * Met en surbrillance le lien correspondant à l'URL courante.
   * Utilise data-url-name pour matcher sans dépendre du texte du lien.
   * Fallback : compare les chemins href.
   */
  function initActiveLink() {
    const sidebar = document.getElementById("sidebar");
    if (!sidebar) return;

    const currentPath = window.location.pathname.replace(/\/$/, "");
    const links = Array.from(sidebar.querySelectorAll("a.nav-link"));

    let bestMatch = null;
    let bestMatchLength = -1;

    links.forEach(function (link) {
      const href = link.getAttribute("href");
      if (!href || href.startsWith("#") || href.startsWith("http")) return;
      const linkPath = href.split("?")[0].replace(/\/$/, "");
      if (
        currentPath === linkPath ||
        (linkPath && currentPath.indexOf(linkPath) === 0)
      ) {
        if (linkPath.length > bestMatchLength) {
          bestMatch = link;
          bestMatchLength = linkPath.length;
        }
      }
    });

    if (bestMatch) {
      bestMatch.classList.add("active");
      bestMatch.setAttribute("aria-current", "page");
      const section = bestMatch.closest(".nav-section");
      if (section) {
        section.classList.add("open");
        const content = section.querySelector(".nav-section-content");
        const button = section.querySelector(".nav-section-header");
        if (content) content.classList.add("open");
        if (button) button.setAttribute("aria-expanded", "true");
      }
    }
  }

  /**
   * Initialise l'attribut aria-expanded sur les sections repliables.
   * Au chargement, toutes les sections sont fermées (false).
   */
  function initAriaDefaults() {
    const sidebar = document.getElementById("sidebar");
    if (!sidebar) return;
    sidebar.querySelectorAll(".nav-section-header").forEach(function (btn) {
      if (!btn.hasAttribute("aria-expanded")) {
        btn.setAttribute("aria-expanded", "false");
      }
    });
  }

  function init() {
    initAriaDefaults();
    initSidebarFilter();
    initActiveLink();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
