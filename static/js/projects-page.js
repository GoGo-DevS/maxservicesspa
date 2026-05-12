(function () {
  var shared = window.MAXProjectsShared;
  var homeUrl = document.body.dataset.homeUrl || "/";
  var pendingProjectKey = "maxservices:pending-project-slug";

  if (!shared) {
    return;
  }

  var state = {
    category: "all",
    selectedSlug: "",
    selectedMediaIndex: 0
  };

  var filterRoot = document.getElementById("projects-filter-bar");
  var gridRoot = document.getElementById("projects-grid");
  var detailRoot = document.getElementById("project-detail");
  var totalCount = document.getElementById("projects-total-count");
  var totalCategories = document.getElementById("projects-total-categories");
  var resultCopy = document.getElementById("projects-result-copy");
  var modalRoot = null;

  if (!filterRoot || !gridRoot || !detailRoot || !totalCount || !totalCategories || !resultCopy || !shared.catalog.projects.length) {
    return;
  }

  state.selectedSlug = getInitialSlug() || shared.catalog.projects[0].slug;
  if (!getSelectedProject()) {
    state.selectedSlug = shared.catalog.projects[0].slug;
  }

  clearProjectHash();

  renderSummary();
  renderFilters();
  renderGrid();
  renderDetail();

  function renderSummary() {
    totalCount.textContent = String(shared.catalog.projects.length);

    var activeCategories = shared.catalog.categories.filter(function (category) {
      return category.id !== "all" && shared.getProjectsByCategory(category.id).length > 0;
    });

    totalCategories.textContent = String(activeCategories.length);
  }

  function renderFilters() {
    filterRoot.innerHTML = "";

    shared.catalog.categories.forEach(function (category) {
      var button = document.createElement("button");
      var count = category.id === "all" ? shared.catalog.projects.length : shared.getProjectsByCategory(category.id).length;
      button.className = "projects-filter-chip" + (state.category === category.id ? " is-active" : "");
      button.type = "button";
      button.innerHTML = category.label + " <span class='projects-filter-chip-count'>" + count + "</span>";
      button.addEventListener("click", function () {
        state.category = category.id;
        ensureVisibleSelection();
        renderFilters();
        renderGrid();
        renderDetail();
      });
      filterRoot.appendChild(button);
    });
  }

  function renderGrid() {
    var projects = getVisibleProjects();
    gridRoot.innerHTML = "";
    resultCopy.textContent = projects.length + " proyectos disponibles";

    if (!projects.length) {
      gridRoot.innerHTML = [
        "<div class='project-empty-state'>",
        "<h3>No hay proyectos cargados en esta especialidad.</h3>",
        "<p>Puedes revisar otra categoría o consultar directamente por un trabajo similar al que necesitas.</p>",
        "</div>"
      ].join("");
      return;
    }

    projects.forEach(function (project) {
      var card = document.createElement("article");
      card.className = "project-list-card" + (project.slug === state.selectedSlug ? " is-active" : "");
      card.id = "project-" + project.slug;

      var button = document.createElement("button");
      button.className = "project-list-button";
      button.type = "button";
      button.addEventListener("click", function () {
        state.selectedSlug = project.slug;
        state.selectedMediaIndex = 0;
        updateHash(project.slug);
        renderGrid();
        renderDetail();
      });

      var figure = document.createElement("div");
      figure.className = "project-list-figure";
      figure.appendChild(shared.createProjectImage(project, project.cover, project.name, "PORTADA"));
      figure.appendChild(createVisualOverlay(project));

      var content = document.createElement("div");
      content.className = "project-list-content";
      content.innerHTML = [
        "<h3>" + project.name + "</h3>",
        "<p>" + project.summary + "</p>",
        "<p class='project-meta-line'>" + project.sector + "</p>"
      ].join("");

      var tags = document.createElement("div");
      tags.className = "project-meta-tags";
      tags.appendChild(createChip(project.location));
      tags.appendChild(createChip(shared.getProjectReference(project)));

      content.appendChild(tags);
      button.appendChild(figure);
      button.appendChild(content);
      card.appendChild(button);
      gridRoot.appendChild(card);
    });
  }

  function renderDetail() {
    var project = getSelectedProject();
    if (!project) {
      detailRoot.innerHTML = "";
      return;
    }

    var gallery = getUniqueGallery(project);
    var selectedMedia = gallery[state.selectedMediaIndex] || project.cover;

    detailRoot.innerHTML = "";

    var figure = document.createElement("div");
    figure.className = "project-detail-figure";
    var mainImageButton = document.createElement("button");
    mainImageButton.className = "project-detail-image-button";
    mainImageButton.type = "button";
    mainImageButton.setAttribute("aria-label", "Ampliar imagen del proyecto");
    mainImageButton.appendChild(shared.createProjectImage(project, selectedMedia, project.name, "GALERÍA " + (state.selectedMediaIndex + 1)));
    mainImageButton.addEventListener("click", function () {
      openProjectImageModal(project, selectedMedia);
    });
    figure.appendChild(mainImageButton);

    var figureHint = document.createElement("span");
    figureHint.className = "project-detail-image-hint";
    figureHint.textContent = "Toca la imagen para verla más grande";
    figure.appendChild(figureHint);

    var head = document.createElement("div");
    head.className = "project-detail-head";
    head.innerHTML = [
      "<p class='project-kicker'>" + shared.findCategoryLabel(project.category) + "</p>",
      "<h3>" + project.name + "</h3>",
      "<p>" + project.description + "</p>",
      "<p class='project-detail-summary-line'>" + project.location + " | " + shared.getProjectReference(project) + "</p>"
    ].join("");

    var metadata = document.createElement("div");
    metadata.className = "project-detail-metadata";
    metadata.appendChild(createMetaCard("Ubicación", project.location));
    metadata.appendChild(createMetaCard("Sector", project.sector));
    metadata.appendChild(createMetaCard("Categoría", shared.findCategoryLabel(project.category)));
    metadata.appendChild(createMetaCard(project.reference ? "Referencia" : "Año", shared.getProjectReference(project)));

    var services = document.createElement("div");
    services.className = "project-services";
    project.services.forEach(function (service) {
      services.appendChild(createChip(service));
    });

    var thumbs = document.createElement("div");
    thumbs.className = "project-thumb-row";
    gallery.forEach(function (fileName, index) {
      var button = document.createElement("button");
      button.className = "project-thumb" + (state.selectedMediaIndex === index ? " is-active" : "");
      button.type = "button";
      button.setAttribute("aria-label", "Ver imagen " + (index + 1) + " del proyecto");
      button.addEventListener("click", function () {
        state.selectedMediaIndex = index;
        renderDetail();
      });
      button.appendChild(shared.createProjectImage(project, fileName, project.name + " imagen " + (index + 1), "GALERÍA " + (index + 1)));
      thumbs.appendChild(button);
    });

    var actions = document.createElement("div");
    actions.className = "project-detail-actions";
    actions.innerHTML = [
      "<a class='btn btn-brand-primary' href='" + homeUrl + "' data-home-section='contacto'>Consultar proyecto similar</a>",
      "<a class='btn btn-brand-outline' href='" + homeUrl + "' data-home-section='servicios'>Ver servicios</a>"
    ].join("");

    detailRoot.appendChild(figure);
    detailRoot.appendChild(head);
    detailRoot.appendChild(metadata);
    detailRoot.appendChild(services);
    if (gallery.length > 1) {
      detailRoot.appendChild(thumbs);
    }
    detailRoot.appendChild(actions);
  }

  function getUniqueGallery(project) {
    var seen = {};
    return [project.cover].concat(project.gallery || []).filter(function (fileName) {
      if (!fileName || seen[fileName]) {
        return false;
      }
      seen[fileName] = true;
      return true;
    });
  }

  function ensureModal() {
    if (modalRoot) {
      return modalRoot;
    }

    modalRoot = document.createElement("div");
    modalRoot.className = "project-image-modal";
    modalRoot.setAttribute("hidden", "hidden");
    modalRoot.innerHTML = [
      "<div class='project-image-modal-backdrop' data-close='true'></div>",
      "<div class='project-image-modal-dialog' role='dialog' aria-modal='true' aria-label='Imagen ampliada del proyecto'>",
      "<button class='project-image-modal-close' type='button' aria-label='Cerrar imagen ampliada' data-close='true'>&times;</button>",
      "<img class='project-image-modal-media' alt='Imagen ampliada del proyecto'>",
      "</div>"
    ].join("");

    modalRoot.addEventListener("click", function (event) {
      if (event.target && event.target.getAttribute("data-close") === "true") {
        closeProjectImageModal();
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        closeProjectImageModal();
      }
    });

    document.body.appendChild(modalRoot);
    return modalRoot;
  }

  function openProjectImageModal(project, fileName) {
    var modal = ensureModal();
    var image = modal.querySelector(".project-image-modal-media");
    image.src = shared.getProjectMediaPath(project, fileName);
    image.alt = project.name;
    modal.hidden = false;
    document.body.classList.add("project-image-modal-open");
  }

  function closeProjectImageModal() {
    var modal = ensureModal();
    modal.hidden = true;
    document.body.classList.remove("project-image-modal-open");
  }

  function createVisualOverlay(project) {
    var overlay = document.createElement("div");
    overlay.className = "project-visual-overlay";
    overlay.innerHTML = [
      "<div class='project-visual-top'>",
      "<span class='project-visual-chip'>" + shared.findCategoryLabel(project.category) + "</span>",
      "<span class='project-visual-year'>" + shared.getProjectReference(project) + "</span>",
      "</div>",
      "<div class='project-visual-bottom'>",
      "<p class='project-visual-location'>" + project.location + "</p>",
      "</div>"
    ].join("");
    return overlay;
  }

  function createChip(label) {
    var chip = document.createElement("span");
    chip.className = "project-chip";
    chip.textContent = label;
    return chip;
  }

  function createMetaCard(label, value) {
    var article = document.createElement("article");
    article.innerHTML = "<span>" + label + "</span><strong>" + value + "</strong>";
    return article;
  }

  function getVisibleProjects() {
    return shared.getProjectsByCategory(state.category);
  }

  function getSelectedProject() {
    return shared.catalog.projects.find(function (project) {
      return project.slug === state.selectedSlug;
    });
  }

  function ensureVisibleSelection() {
    var projects = getVisibleProjects();
    if (!projects.length) {
      state.selectedSlug = "";
      state.selectedMediaIndex = 0;
      return;
    }

    var selectedIsVisible = projects.some(function (project) {
      return project.slug === state.selectedSlug;
    });

    if (!selectedIsVisible) {
      state.selectedSlug = projects[0].slug;
      state.selectedMediaIndex = 0;
      updateHash(state.selectedSlug);
    }
  }

  function getInitialSlug() {
    var pendingSlug = window.sessionStorage.getItem(pendingProjectKey);
    if (pendingSlug) {
      window.sessionStorage.removeItem(pendingProjectKey);
      return pendingSlug;
    }

    var hash = window.location.hash || "";
    if (hash.indexOf("#project-") !== 0) {
      return "";
    }

    return hash.replace("#project-", "");
  }

  function updateHash(slug) {
    clearProjectHash();
  }

  function clearProjectHash() {
    if (window.location.hash) {
      window.history.replaceState(null, "", window.location.pathname);
    }
  }
}());
