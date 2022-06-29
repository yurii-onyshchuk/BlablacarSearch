// Add active link at navbar
$(document).ready(function () {
    $('.nav-item a').each(function () {
        let location = window.location.protocol + '//' + window.location.host + window.location.pathname;
        let link = this.href;
        if (location === link) {
            $(this).addClass('active');
        }
    })
})

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



