// Add active link at navbar
$(document).ready(function () {
    $('.nav-item a').each(function () {
        let location = window.location.protocol + '//' + window.location.host + window.location.pathname;
        let link = this.href;
        if (location === link) {
            $(this).addClass('active');
        }
    });

    // Init Isotope
    let $grid = $('.grid').isotope({
        itemSelector: '.trip-item',
        layoutMode: 'fitRows'
    });

    // Store trips count
    let iso = $grid.data('isotope');
    let $filterCount = $('.filter-count');

    function updateFilterCount() {
        let trip_count = iso.filteredItems.length
        $filterCount.text(trip_count);
        if (trip_count === 0){
            $('#empty-trip-list').removeClass('d-none');
        }
        else {
            $('#empty-trip-list').addClass('d-none');
        }
    }

    // City from search form
    const fromCityInput = $("input[id='from_city']")[0]['value']
    const toCityInput = $("input[id='to_city']")[0]['value']

    // Filter functions
    let FilterFns = {
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
    };

    // Bind filter button click
    $('.filters-button-group').on('click', 'button', function () {
        var filterValue = $(this).attr('data-filter'); // -> from_city, to_city, from_to_city, with_vehicle
        filterValue = FilterFns[filterValue] || filterValue; // -> FUNC: from_city, to_city, from_to_city, with_vehicle
        $grid.isotope({filter: filterValue});
        updateFilterCount();
    });

    updateFilterCount();

    // Change is-checked class on buttons
    $('.button-group').each(function (i, buttonGroup) {
        var $buttonGroup = $(buttonGroup);
        $buttonGroup.on('click', 'button', function () {
            $buttonGroup.find('.is-checked').removeClass('is-checked');
            $(this).addClass('is-checked');
        });
    });
});

// Exchange of city fields
document.onclick = function () {
    var elem = window.event.srcElement;

    if (elem.className.includes("btn-exchange")) {
        var from_city = document.getElementById('from_city').value;
        document.getElementById('from_city').value = document.getElementById('to_city').value;
        document.getElementById('to_city').value = from_city;
    }
};

// Tooltip
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))



