// Tooltip
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

// Exchange of city fields
document.onclick = function () {
    let elem = window.event.srcElement;

    if (elem.className.includes("btn-exchange")) {
        let from_city = document.getElementById('from_city').value;
        document.getElementById('from_city').value = document.getElementById('to_city').value;
        document.getElementById('to_city').value = from_city;
    }
};

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

    // City from search form
    const fromCityInput = $("input[id='from_city']")[0]['value']
    const toCityInput = $("input[id='to_city']")[0]['value']

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
        itemSelector: '.trip-item',
        layoutMode: 'fitRows',
        getSortData: {
            price: function (itemElem) {
                var price = $(itemElem).find('.price').text();
                return parseFloat(price.replace(/[\(\)]/g, ''));
            }
        },
        filter: function () {

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
    $('.sort-by-button-group').on('click', 'button', function () {
        let sortByValue = $(this).attr('data-sort-by');
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



