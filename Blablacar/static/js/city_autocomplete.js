export function setupAutocomplete(inputSelector, resultsSelector, coordinateField) {
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    const cache = {};
    let citySelected = false;
    const primaryCities = [
        {
            Description: 'Київ', Latitude: '50.450418000000000', Longitude: '30.523541000000000',
            SettlementTypeDescription: 'м.', AreaDescription: 'Київська'
        },
        {
            Description: 'Львів', Latitude: '49.839678000000000', Longitude: '24.029709000000000',
            SettlementTypeDescription: 'м.', AreaDescription: 'Львівська'
        },
        {
            Description: 'Одеса', Latitude: '46.484579000000000', Longitude: '30.732597000000000',
            SettlementTypeDescription: 'м.', AreaDescription: 'Одеська'
        },
        {
            Description: 'Харків', Latitude: '49.992167000000000', Longitude: '36.231202000000000',
            SettlementTypeDescription: 'м.', AreaDescription: 'Харківська'
        },
        {
            Description: 'Рівне', Latitude: '50.619898000000000', Longitude: '26.251611000000000',
            SettlementTypeDescription: 'м.', AreaDescription: 'Рівненська'
        },
        {
            Description: 'Вінниця', Latitude: '49.233118000000000', Longitude: '28.468231000000000',
            SettlementTypeDescription: 'м.', AreaDescription: 'Вінницька'
        },
        {
            Description: 'Житомир', Latitude: '50.254623000000000', Longitude: '28.658692000000000',
            SettlementTypeDescription: 'м.', AreaDescription: 'Житомирська'
        },
        {
            Description: 'Ізяслав', Latitude: '50.119112400000000', Longitude: '26.828114100000000',
            SettlementTypeDescription: 'м.', AreaDescription: 'Хмельницька'
        }
    ];

    $(inputSelector).on('click', function () {
        citySelected = false;
        $(coordinateField).attr('value', '');
        if (!$(this).val()) {
            displayPrimaryCities(resultsSelector);
        } else {
            debounceAutocomplete($(this).val(), inputSelector, resultsSelector);
        }
    }).on('input', debounce(function () {
        if (!citySelected) {
            $(coordinateField).attr('value', '');
            if (!$(this).val()) {
                displayPrimaryCities(resultsSelector);
            } else {
                debounceAutocomplete($(this).val(), inputSelector, resultsSelector);
            }
        }
    }, 300));

    $(resultsSelector).on('click', 'li', function () {
        const selectedText = $(this).attr('data-city');
        const selectedLatitude = $(this).attr('data-latitude');
        const selectedLongitude = $(this).attr('data-longitude');

        $(inputSelector).val(selectedText).attr('value', selectedText);
        $(coordinateField).attr('value', `${selectedLatitude},${selectedLongitude}`);
        $(resultsSelector).hide();
        citySelected = true;
    });

    $(document).click(function (event) {
        if (!$(event.target).closest(`${inputSelector}, ${resultsSelector}`).length) {
            $(resultsSelector).hide();
        }
    });

    function debounceAutocomplete(query, inputSelector, resultsSelector) {
        if (query.length >= 1) {
            if (cache[query]) {
                displayResults(cache[query], resultsSelector);
            } else {
                $.ajax({
                    url: '/city_autocomplete/',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({query: query}),
                    headers: {
                        'X-CSRFToken': csrfToken
                    },
                    success: function (data) {
                        if (citySelected) return;
                        if (data.success && data.data.length > 0) {
                            cache[query] = data.data;
                            displayResults(data.data, resultsSelector);
                        } else {
                            $(resultsSelector).hide();
                        }
                    }
                });
            }
        } else {
            displayPrimaryCities(resultsSelector);
        }
    }

    function debounce(func, delay) {
        let debounceTimer;
        return function () {
            const context = this;
            const args = arguments;
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => func.apply(context, args), delay);
        };
    }

    function displayResults(data, resultsSelector) {
        $(resultsSelector).empty();
        $(resultsSelector).show();
        $.each(data, function (index, city) {
            $(resultsSelector).append(`<li class="dropdown-item" data-city="${city.Description}" data-latitude="${city.Latitude}" data-longitude="${city.Longitude}">${city.SettlementTypeDescription.substring(0, 1)}. ${city.Description}, ${city.AreaDescription} обл.</li>`);
        });
    }

    function displayPrimaryCities(resultsSelector) {
        $(resultsSelector).empty();
        $(resultsSelector).show();
        $.each(primaryCities, function (index, city) {
            $(resultsSelector).append(`<li class="dropdown-item" data-city="${city.Description}" data-latitude="${city.Latitude}" data-longitude="${city.Longitude}">${city.SettlementTypeDescription.substring(0, 1)}. ${city.Description}, ${city.AreaDescription} обл.</li>`);
        });
    }
}
