(function () {
  var body = document.body;
  if (!body) {
    return;
  }

  var homeUrl = body.dataset.homeUrl || "/";
  var pendingSectionKey = "maxservices:pending-home-section";
  var currentPath = normalizePath(window.location.pathname);
  var homePath = normalizePath(new URL(homeUrl, window.location.origin).pathname);
  var homeNavLinks = Array.prototype.slice.call(document.querySelectorAll("[data-nav-target]"));

  if ("scrollRestoration" in window.history) {
    window.history.scrollRestoration = "manual";
  }

  bindHomeSectionLinks();
  bindLocalScrollLinks();
  handleInitialHomeState();
  bindHomeActiveState();

  function bindHomeSectionLinks() {
    document.querySelectorAll("[data-home-section]").forEach(function (link) {
      link.addEventListener("click", function (event) {
        var targetId = link.dataset.homeSection;
        if (!targetId) {
          return;
        }

        if (currentPath === homePath) {
          event.preventDefault();
          clearHomeHash();
          scrollToTarget(targetId);
          setActiveHomeNav(targetId);
          collapseNavbar();
          return;
        }

        window.sessionStorage.setItem(pendingSectionKey, targetId);
      });
    });
  }

  function bindLocalScrollLinks() {
    document.querySelectorAll("[data-scroll-target]").forEach(function (link) {
      link.addEventListener("click", function (event) {
        var targetId = link.dataset.scrollTarget;
        if (!targetId) {
          return;
        }

        var target = document.getElementById(targetId);
        if (!target) {
          return;
        }

        event.preventDefault();
        var href = link.getAttribute("href") || window.location.pathname;
        window.history.replaceState(null, "", href);
        scrollToElement(target);
        collapseNavbar();
      });
    });
  }

  function handleInitialHomeState() {
    if (currentPath !== homePath) {
      return;
    }

    var pendingSection = window.sessionStorage.getItem(pendingSectionKey);
    var focusSection = new URLSearchParams(window.location.search).get("focus");
    var hashSection = window.location.hash ? window.location.hash.slice(1) : "";
    clearHomeHash();

    if (pendingSection) {
      window.sessionStorage.removeItem(pendingSectionKey);
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(function () {
          scrollToTarget(pendingSection);
          setActiveHomeNav(pendingSection);
        });
      });
      return;
    }

    if (focusSection) {
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(function () {
          scrollToTarget(focusSection);
          setActiveHomeNav(focusSection);
          window.history.replaceState(null, "", homeUrl);
        });
      });
      return;
    }

    if (hashSection) {
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(function () {
          scrollToTarget(hashSection === "contacto" ? "formulario" : hashSection);
          setActiveHomeNav(hashSection === "formulario" ? "contacto" : hashSection);
        });
      });
      return;
    }

    if (isReloadNavigation()) {
      window.scrollTo({ top: 0, behavior: "auto" });
    }
  }

  function bindHomeActiveState() {
    if (currentPath !== homePath || !homeNavLinks.length) {
      return;
    }

    updateActiveHomeSection();
    window.addEventListener("scroll", updateActiveHomeSection, { passive: true });
    window.addEventListener("resize", updateActiveHomeSection);
  }

  function updateActiveHomeSection() {
    var header = document.querySelector(".site-header");
    var headerOffset = header ? header.getBoundingClientRect().height : 0;
    var threshold = window.scrollY + headerOffset + 36;
    var activeTarget = "inicio";

    homeNavLinks.forEach(function (link) {
      var sectionId = link.dataset.navTarget;
      var section = document.getElementById(sectionId);
      if (!section) {
        return;
      }

      if (section.offsetTop <= threshold) {
        activeTarget = sectionId;
      }
    });

    setActiveHomeNav(activeTarget);
  }

  function setActiveHomeNav(targetId) {
    homeNavLinks.forEach(function (link) {
      link.classList.toggle("active", link.dataset.navTarget === targetId);
    });
  }

  function scrollToTarget(targetId) {
    var target = document.getElementById(targetId);
    if (!target) {
      return;
    }

    scrollToElement(target);
  }

  function scrollToElement(element) {
    var header = document.querySelector(".site-header");
    var headerOffset = header ? header.getBoundingClientRect().height : 0;
    var targetTop = element.getBoundingClientRect().top + window.scrollY - headerOffset - 18;
    window.scrollTo({
      top: Math.max(targetTop, 0),
      behavior: "smooth"
    });
  }

  function clearHomeHash() {
    if (window.location.hash && currentPath === homePath) {
      window.history.replaceState(null, "", homeUrl);
    }
  }

  function collapseNavbar() {
    var navbar = document.querySelector(".navbar-collapse.show");
    if (!navbar || !window.bootstrap || !window.bootstrap.Collapse) {
      return;
    }

    window.bootstrap.Collapse.getOrCreateInstance(navbar).hide();
  }

  function isReloadNavigation() {
    if (window.performance && typeof window.performance.getEntriesByType === "function") {
      var entries = window.performance.getEntriesByType("navigation");
      if (entries.length) {
        return entries[0].type === "reload";
      }
    }

    if (window.performance && window.performance.navigation) {
      return window.performance.navigation.type === 1;
    }

    return false;
  }

  function normalizePath(path) {
    return (path || "/").replace(/\/+$/, "") || "/";
  }
}());
