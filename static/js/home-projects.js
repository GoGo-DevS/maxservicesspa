(function () {
  var root = document.getElementById("featured-projects-grid");
  var shared = window.MAXProjectsShared;
  var projectsUrl = document.body.dataset.projectsUrl || "/proyectos/";

  if (!root || !shared) {
    return;
  }

  var featuredProjects = shared.catalog.projects.filter(function (project) {
    return project.featured;
  }).slice(0, 3);

  root.innerHTML = "";

  featuredProjects.forEach(function (project) {
    var article = document.createElement("article");
    article.className = "project-card reveal";

    var link = document.createElement("a");
    link.className = "project-card-link";
    // Cada tarjeta va a la ficha propia del proyecto (07-10-2026). Antes las
    // tres apuntaban a /proyectos/ y las fichas no recibian enlaces desde la home.
    link.href = projectsUrl + project.slug + "/";
    link.setAttribute("aria-label", "Ver proyecto " + project.name);

    var figure = document.createElement("div");
    figure.className = "project-card-figure";
    figure.appendChild(shared.createProjectImage(project, project.cover, project.name, "PORTADA"));
    figure.appendChild(createVisualOverlay(project));

    var content = document.createElement("div");
    content.className = "project-content";
    content.innerHTML = [
      "<h3>" + project.name + "</h3>",
      "<p>" + project.summary + "</p>",
      "<p class='project-meta-line'>" + project.sector + "</p>"
    ].join("");

    link.appendChild(figure);
    link.appendChild(content);
    article.appendChild(link);
    root.appendChild(article);
  });

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
}());
