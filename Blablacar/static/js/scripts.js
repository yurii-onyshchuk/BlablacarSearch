const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

document.onclick = function () {
    var elem = window.event.srcElement;

    if (elem.className.includes("btn-exchange")) {
        var from_city = document.getElementById('from_city').value;
        document.getElementById('from_city').value = document.getElementById('to_city').value;
        document.getElementById('to_city').value = from_city;
    }
};

