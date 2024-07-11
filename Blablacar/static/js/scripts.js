// Tooltip
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

// Exchange of city fields
$(document).on('click', '#city-exchange', function () {
    let from_city = document.getElementById('id_from_city').value;
    document.getElementById('id_from_city').value = document.getElementById('id_to_city').value;
    document.getElementById('id_to_city').value = from_city;

    let from_coordinate = document.getElementById('id_from_coordinate').value;
    document.getElementById('id_from_coordinate').value = document.getElementById('id_to_coordinate').value;
    document.getElementById('id_to_coordinate').value = from_coordinate;
});

$(document).ready(function () {

    // Add active link at navbar
    $('.nav-item a').each(function () {
        let location = window.location.protocol + '//' + window.location.host + window.location.pathname;
        let link = this.href;
        if (location === link) {
            $(this).addClass('active');
        }
    });

//  ISOTOPE FILTER AND SORTING  //

    let fromCityInput = $("input[id='id_from_city']")[0]
    let toCityInput = $("input[id='id_to_city']")[0]

    // Cities from searching form
    if (fromCityInput && toCityInput) {
        fromCityInput = fromCityInput['value'].trim()
        toCityInput = toCityInput['value'].trim()
        // Cities from task
    } else {
        fromCityInput = $(".detail-task-card .from_city").text().trim()
        toCityInput = $(".detail-task-card .to_city").text().trim()
    }

    // Store filter for each group
    let filters = {};

    // Function for update filter trip count
    function updateFilterCount() {
        let trip_count = iso.filteredItems.length
        $filterCount.text(trip_count);
        if (trip_count > 0) {
            $('#empty-trip-list').addClass('d-none');
        } else {
            $('#empty-trip-list').removeClass('d-none');
        }
    }

    // Filter functions
    let filterFns = {
        from_city: function () {
            const fromCity = $(this).find('.from-city').text();
            return fromCity.match(fromCityInput);
        },

        to_city: function () {
            const toCity = $(this).find('.to-city').text();
            return toCity.match(toCityInput);
        },

        from_to_city: function () {
            const fromCity = $(this).find('.from-city').text();
            const toCity = $(this).find('.to-city').text();
            return fromCity.match(fromCityInput) && toCity.match(toCityInput);
        },

        with_vehicle: function () {
            return $(this).find('.vehicle').text();
        },
    };

    // Init Isotope
    let $grid = $('.grid').isotope({
        itemSelector: '.trip-item', layoutMode: 'fitRows', getSortData: {
            price: function (itemElem) {
                var price = $(itemElem).find('.price').text();
                return parseFloat(price.replace(/[\(\)]/g, ''));
            }
        }, filter: function () {

            let isMatched = true;
            let $this = $(this);

            for (let prop in filters) {

                let filter = filters[prop];
                // use function if it matches
                filter = filterFns[filter] || filter;
                // test each filter
                if (filter) {
                    isMatched = isMatched && $this.is(filter);
                }
                // break if not matched
                if (!isMatched) {
                    break;
                }
            }
            return isMatched;
        }
    });

    // Store trips count
    let iso = $grid.data('isotope');
    let $filterCount = $('.filter-count');
    updateFilterCount()

    // Bind filter button click
    $('.filters').on('click', 'button', function () {
        let $this = $(this);
        // get group key
        let $buttonGroup = $this.parents('.button-group');
        let filterGroup = $buttonGroup.attr('data-filter-group');
        // set filter for group
        filters[filterGroup] = $this.attr('data-filter');
        // arrange, and use filter fn
        $grid.isotope();
        updateFilterCount();
    });

    // Sort items on button click
    $('.sort-by-button-group').change(function () {
        let sortByValue = $('option:selected', this).attr('data-sort-by');
        $grid.isotope({sortBy: sortByValue});
    });

    // Change is-checked class on buttons
    $('.button-group').each(function (i, buttonGroup) {
        let $buttonGroup = $(buttonGroup);
        $buttonGroup.on('click', 'button', function () {
            $buttonGroup.find('.is-checked').removeClass('is-checked');
            $(this).addClass('is-checked');
        });
    });
    //  END ISOTOPE FILTER AND SORTING  //
});


$(document).ready(function () {
    if (window.innerWidth < 768) {
        $('.filters-area #heading-filters button').addClass('collapsed');
        $('.filters-area #collapse-filters').addClass('collapse').removeClass('show');
    } else {
        $('.filters-area #heading-filters button').removeClass('collapsed');
        $('.filters-area #collapse-filters').removeClass('collapse').addClass('show');
    }
});

// Autocomplete
$(document).ready(function () {
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    // Autocomplete function
    function setupAutocomplete(inputSelector, resultsSelector, coordinateField) {
        $(inputSelector).on('click', function () {
            $(coordinateField).attr('value', '')
            autocompleteFunction($(this).val(), inputSelector, resultsSelector);
        })
            .on('input', function () {
                autocompleteFunction($(this).val(), inputSelector, resultsSelector);
            });

        $(resultsSelector).on('click', 'li', function () {
            const selectedText = $(this).attr('data-city');
            const selectedLatitude = $(this).attr('data-latitude');
            const selectedLongitude = $(this).attr('data-longitude');

            $(inputSelector).val(selectedText).attr('value', selectedText);
            $(coordinateField).attr('value', `${selectedLatitude},${selectedLongitude}`)
            $(resultsSelector).hide();
        });

        $(document).click(function (event) {
            if (!$(event.target).closest(`${inputSelector}, ${resultsSelector}`).length) {
                $(resultsSelector).hide();
            }
        });
    }

    // Setup autocomplete for #id_from_city
    setupAutocomplete('#id_from_city', '#id_from_city_results', '#id_from_coordinate');

    // Setup autocomplete for #id_to_city
    setupAutocomplete('#id_to_city', '#id_to_city_results', '#id_to_coordinate');

    function autocompleteFunction(query, inputSelector, resultsSelector) {
        if (query.length >= 1) {
            $.ajax({
                url: '/city_autocomplete/',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({query: query}),
                headers: {
                    'X-CSRFToken': csrfToken
                },
                success: function (data) {
                    $(resultsSelector).empty();
                    if (data.success && data.data.length > 0) {
                        
                        data.data.sort(function (a, b) {
                            if (a.SettlementTypeDescription === 'місто' && b.SettlementTypeDescription === 'село') {
                                return -1;
                            }
                            if (a.SettlementTypeDescription === 'село' && b.SettlementTypeDescription === 'місто') {
                                return 1;
                            }
                            return 0;
                        });

                        $(resultsSelector).show();
                        $.each(data.data.slice(0, 10), function (index, city) {
                            $(resultsSelector).append(`<li class="dropdown-item" data-city="${city.Description}" data-latitude="${city.Latitude}" data-longitude="${city.Longitude}">${city.SettlementTypeDescription.substring(0, 1)}. ${city.Description}, ${city.AreaDescription} обл.</li>`);
                        });
                    } else {
                        $(resultsSelector).hide();
                    }
                }
            });
        } else {
            $(resultsSelector).hide();
        }
    }
});