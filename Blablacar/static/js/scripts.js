// script.js

import { initializeIsotope } from './trip_filter_sorting.js';
import { setupAutocomplete } from './city_autocomplete.js';

// Tooltip
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

$(document).ready(function () {
    // Add active link at navbar
    $('.nav-item a').each(function () {
        let location = window.location.protocol + '//' + window.location.host + window.location.pathname;
        let link = this.href;
        if (location === link) {
            $(this).addClass('active');
        }
    });

    // Exchange of city fields
    $(document).on('click', '#city-exchange', function () {
        let from_city = document.getElementById('id_from_city').value;
        document.getElementById('id_from_city').value = document.getElementById('id_to_city').value;
        document.getElementById('id_to_city').value = from_city;

        let from_coordinate = document.getElementById('id_from_coordinate').value;
        document.getElementById('id_from_coordinate').value = document.getElementById('id_to_coordinate').value;
        document.getElementById('id_to_coordinate').value = from_coordinate;
    });

    // Initialize Isotope if the filter-sorting element exists
    if ($('#filter-sorting').length) {
        initializeIsotope();
    }

    // Setup autocomplete for #id_from_city and #id_to_city
    setupAutocomplete('#id_from_city', '#id_from_city_results', '#id_from_coordinate');
    setupAutocomplete('#id_to_city', '#id_to_city_results', '#id_to_coordinate');
});