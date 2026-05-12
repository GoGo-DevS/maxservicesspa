(function () {
  var regionSelect = document.getElementById("id_region");
  var citySelect = document.getElementById("id_city");
  var communeSelect = document.getElementById("id_commune");
  var mapNode = document.getElementById("contact-location-map");

  if (!regionSelect || !citySelect || !communeSelect) {
    return;
  }

  var citiesEndpoint = regionSelect.getAttribute("data-cities-endpoint");
  var communesEndpoint = citySelect.getAttribute("data-communes-endpoint");
  var initialRegion = regionSelect.value;
  var initialCity = citySelect.value;
  var initialCommune = communeSelect.value;
  var locationMap = {};

  if (mapNode) {
    try {
      locationMap = JSON.parse(mapNode.textContent);
    } catch (error) {
      locationMap = {};
    }
  }

  function buildOption(value, label, selectedValue) {
    var option = document.createElement("option");
    option.value = value;
    option.textContent = label;
    option.selected = value === selectedValue;
    return option;
  }

  function populateSelect(selectNode, results, selectedValue) {
    selectNode.innerHTML = "";
    results.forEach(function (item) {
      selectNode.appendChild(buildOption(item.value, item.label, selectedValue));
    });
    if (!selectNode.value) {
      selectNode.selectedIndex = 0;
    }
  }

  function fetchJson(url) {
    return fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } }).then(function (response) {
      if (!response.ok) {
        throw new Error("Request failed");
      }
      return response.json();
    });
  }

  function loadCities(region, selectedValue) {
    if (!region) {
      populateSelect(citySelect, [{ value: "", label: "Selecciona ciudad" }], "");
      citySelect.disabled = true;
      populateSelect(communeSelect, [{ value: "", label: "Selecciona comuna" }], "");
      communeSelect.disabled = true;
      return Promise.resolve();
    }

    if (locationMap[region]) {
      var localCities = [{ value: "", label: "Selecciona ciudad" }];
      Object.keys(locationMap[region]).forEach(function (city) {
        localCities.push({ value: city, label: city });
      });
      populateSelect(citySelect, localCities, selectedValue || "");
      citySelect.disabled = false;
      return Promise.resolve();
    }

    citySelect.disabled = true;
    return fetchJson(citiesEndpoint + "?region=" + encodeURIComponent(region)).then(function (payload) {
      populateSelect(citySelect, payload.results, selectedValue || "");
      citySelect.disabled = false;
    });
  }

  function loadCommunes(region, city, selectedValue) {
    if (!region || !city) {
      populateSelect(communeSelect, [{ value: "", label: "Selecciona comuna" }], "");
      communeSelect.disabled = true;
      return Promise.resolve();
    }

    if (locationMap[region] && locationMap[region][city]) {
      var localCommunes = [{ value: "", label: "Selecciona comuna" }];
      locationMap[region][city].forEach(function (commune) {
        localCommunes.push({ value: commune, label: commune });
      });
      populateSelect(communeSelect, localCommunes, selectedValue || "");
      communeSelect.disabled = false;
      return Promise.resolve();
    }

    communeSelect.disabled = true;
    return fetchJson(
      communesEndpoint + "?region=" + encodeURIComponent(region) + "&city=" + encodeURIComponent(city)
    ).then(function (payload) {
      populateSelect(communeSelect, payload.results, selectedValue || "");
      communeSelect.disabled = false;
    });
  }

  regionSelect.addEventListener("change", function () {
    loadCities(regionSelect.value, "").then(function () {
      return loadCommunes(regionSelect.value, citySelect.value, "");
    }).catch(function () {
      citySelect.disabled = false;
      communeSelect.disabled = false;
    });
  });

  citySelect.addEventListener("change", function () {
    loadCommunes(regionSelect.value, citySelect.value, "").catch(function () {
      communeSelect.disabled = false;
    });
  });

  loadCities(initialRegion, initialCity).then(function () {
    return loadCommunes(regionSelect.value, citySelect.value, initialCommune);
  }).catch(function () {
    citySelect.disabled = !regionSelect.value;
    communeSelect.disabled = !citySelect.value;
  });
}());
