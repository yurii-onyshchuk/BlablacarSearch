export function initializeIsotope() {
    let fromCityInput = $("input[id='id_from_city']")[0];
    let toCityInput = $("input[id='id_to_city']")[0];

    // Cities from searching form
    if (fromCityInput && toCityInput) {
        fromCityInput = fromCityInput['value'].trim();
        toCityInput = toCityInput['value'].trim();
    } else {
        fromCityInput = $(".detail-task-card .from_city").text().trim();
        toCityInput = $(".detail-task-card .to_city").text().trim();
    }

    // Store filter for each group
    let filters = {};

    // Function for update filter trip count
    function updateFilterCount() {
        let trip_count = iso.filteredItems.length;
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
                filter = filterFns[filter] || filter;
                if (filter) {
                    isMatched = isMatched && $this.is(filter);
                }
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
    updateFilterCount();

    // Bind filter button click
    $('.filters').on('click', 'button', function () {
        let $this = $(this);
        let $buttonGroup = $this.parents('.button-group');
        let filterGroup = $buttonGroup.attr('data-filter-group');
        filters[filterGroup] = $this.attr('data-filter');
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

    // Filters toggle for mobile view
    if (window.innerWidth < 768) {
        $('.filters-area #heading-filters button').addClass('collapsed');
        $('.filters-area #collapse-filters').addClass('collapse').removeClass('show');
    } else {
        $('.filters-area #heading-filters button').removeClass('collapsed');
        $('.filters-area #collapse-filters').removeClass('collapse').addClass('show');
    }
}
