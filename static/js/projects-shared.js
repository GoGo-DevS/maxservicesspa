(function () {
  var catalogNode = document.getElementById("projects-catalog-data");
  var catalog = window.MAXProjectsCatalog || parseCatalog(catalogNode);
  var staticPrefix = (document.documentElement.dataset.staticPrefix || "/static/").replace(/\/?$/, "/");

  function findCategoryLabel(categoryId) {
    var match = catalog.categories.find(function (category) {
      return category.id === categoryId;
    });

    return match ? match.label : "Proyecto";
  }

  function getProjectMediaPath(project, fileName) {
    return staticPrefix + project.asset_dir + "/" + fileName;
  }

  function getProjectReference(project) {
    return project.reference || project.year || "Proyecto ejecutado";
  }

  function buildFallbackMedia(project, variantLabel) {
    var categoryLabel = findCategoryLabel(project.category).toUpperCase();
    var title = project.name.toUpperCase();
    var location = project.location.toUpperCase();
    var reference = getProjectReference(project).toUpperCase();
    var summary = (variantLabel || "REGISTRO DE PROYECTO").toUpperCase();
    var svg = [
      "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1600 1080'>",
      "<defs>",
      "<linearGradient id='bg' x1='0' y1='0' x2='1' y2='1'>",
      "<stop offset='0%' stop-color='#edf4f8' />",
      "<stop offset='60%' stop-color='#dce8f0' />",
      "<stop offset='100%' stop-color='#cfdde8' />",
      "</linearGradient>",
      "<linearGradient id='accent' x1='0' y1='0' x2='1' y2='0'>",
      "<stop offset='0%' stop-color='#1597e5' stop-opacity='0.78' />",
      "<stop offset='100%' stop-color='#d73b3e' stop-opacity='0.68' />",
      "</linearGradient>",
      "</defs>",
      "<rect width='1600' height='1080' fill='url(#bg)' />",
      "<circle cx='1310' cy='180' r='250' fill='#1597e5' fill-opacity='0.08' />",
      "<circle cx='280' cy='840' r='240' fill='#d73b3e' fill-opacity='0.06' />",
      "<rect x='110' y='104' width='1380' height='872' rx='34' fill='rgba(255,255,255,0.38)' stroke='#ffffff' stroke-opacity='0.55' />",
      "<rect x='110' y='104' width='1380' height='872' rx='34' fill='none' stroke='url(#accent)' stroke-opacity='0.26' />",
      "<path d='M1110 132 L1460 132 L1240 352' stroke='#ffffff' stroke-opacity='0.28' stroke-width='2' fill='none' />",
      "<path d='M150 900 L560 900 L350 690' stroke='#ffffff' stroke-opacity='0.2' stroke-width='2' fill='none' />",
      "<text x='168' y='208' fill='#1567b3' font-family='Arial, sans-serif' font-size='34' font-weight='700' letter-spacing='7'>MAX SERVICES SPA</text>",
      "<text x='168' y='294' fill='#0b1f33' font-family='Arial, sans-serif' font-size='72' font-weight='700'>" + escapeXml(title) + "</text>",
      "<text x='168' y='382' fill='#536877' font-family='Arial, sans-serif' font-size='32'>" + escapeXml(location + " | " + reference) + "</text>",
      "<rect x='168' y='444' width='340' height='2' fill='url(#accent)' />",
      "<text x='168' y='520' fill='#d73b3e' font-family='Arial, sans-serif' font-size='28' font-weight='700' letter-spacing='5'>" + escapeXml(categoryLabel) + "</text>",
      "<text x='168' y='580' fill='#0b1f33' font-family='Arial, sans-serif' font-size='32'>" + escapeXml(summary) + "</text>",
      "<text x='168' y='934' fill='#5e6a75' font-family='Arial, sans-serif' font-size='28'>IMAGEN REFERENCIAL DEL PROYECTO</text>",
      "</svg>"
    ].join("");

    return "data:image/svg+xml;charset=UTF-8," + encodeURIComponent(svg);
  }

  function createProjectImage(project, fileName, alt, variantLabel) {
    var image = document.createElement("img");
    image.src = getProjectMediaPath(project, fileName);
    image.alt = alt;
    image.loading = "lazy";
    image.onerror = function () {
      image.onerror = null;
      image.src = buildFallbackMedia(project, variantLabel);
    };
    return image;
  }

  function getProjectsByCategory(categoryId) {
    if (!categoryId || categoryId === "all") {
      return catalog.projects.slice();
    }

    return catalog.projects.filter(function (project) {
      return project.category === categoryId;
    });
  }

  function parseCatalog(node) {
    if (!node) {
      return { categories: [], projects: [] };
    }

    try {
      return JSON.parse(node.textContent);
    } catch (error) {
      return { categories: [], projects: [] };
    }
  }

  function escapeXml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&apos;");
  }

  window.MAXProjectsShared = {
    catalog: catalog,
    findCategoryLabel: findCategoryLabel,
    getProjectReference: getProjectReference,
    getProjectMediaPath: getProjectMediaPath,
    buildFallbackMedia: buildFallbackMedia,
    createProjectImage: createProjectImage,
    getProjectsByCategory: getProjectsByCategory
  };
}());
