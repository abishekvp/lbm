function notify(code, message) {
    toastr.options = {
        "progressBar": true,
        "positionClass": "toast-top-center"
    };

    if (code === 200) {
        toastr.success(message);
    } else if (code === 403) {
        toastr.warning(message);
    } else {
        toastr.info(message);
    }
}

function api(url, method, data) {
    return new Promise(function(resolve, reject) {
        const form = {
            type: method,
            url: url,
            success: function(response) {
                resolve(response);
            },
            error: function(xhr) {
                reject(xhr.responseJSON || xhr.statusText || 'Request failed');
            },
            // headers: {
            //     'X-CSRFToken': getCSRF()
            // }
        };

        const upperMethod = method.toUpperCase();

        if (data) {
            if (upperMethod === 'GET') {
                form.data = data;
            } else {
                form.data = data;
                form.contentType = 'application/json';
            }
        }
        console.log(data)
        console.log(form)
        $.ajax(form);
    });
}

function request(url, method, formID) {
    const form = document.getElementById(formID);
    const formData = {};

    for (let element of form.elements) {
        if (!element.name) continue;
        formData[element.name] = element.value;
    }

    return api(url, method, formData)
        .then(function(response) {
            if (response.status === 200) {
                if (response.message){
                    notify(response.status, response.message);
                }
                return response.data !== undefined ? response.data : true;
            } else {
                notify(response.status, response.message);
            }
        })
        .catch(function(error) {
            notify(500, error || 'An error occurred');
        });
}

function getCSRF() {
    return $("input[name=csrfmiddlewaretoken]").val();
}

// function addLibrary(event) {
//     event.preventDefault();
//     request('/library', 'POST', 'libraryForm')
// }

function addLibrary() {
    $.ajax({
        type: "POST",
        url: "/library",
        data: {
            library_name: $('#library-name').val(),
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
            if (response.status && response.message){
                notify(response.status, response.message)
            }
        },
        error: function (error) {
            notify(500, error);
        }
    });
}

function addDepartment() {
        $.ajax({
        type: "POST",
        url: "/add-department",
        data: {
            department_name: $('#department-name').val(),
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
            if (response.status && response.message){
                notify(response.status, response.message)
            }
        },
        error: function (error) {
            notify(500, error);
        }
    });
}

function addRack() {
        $.ajax({
        type: "POST",
        url: "/add-rack",
        data: {
            rack_name: $('#rack-name').val(),
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
            if (response.status && response.message){
                notify(response.status, response.message)
            }
        },
        error: function (error) {
            notify(500, error);
        }
    });
}

function test() {
    alert("ok")
    toastr.options = {
  "closeButton": true,
  "debug": false,
  "progressBar": true,
  "preventDuplicates": false,
  "positionClass": "toast-top-right",
  "onclick": null,
  "showDuration": "400",
  "hideDuration": "1000",
  "timeOut": "7000",
  "extendedTimeOut": "1000",
  "showEasing": "swing",
  "hideEasing": "linear",
  "showMethod": "fadeIn",
  "hideMethod": "fadeOut"
}
toastr.info("YeAAA");
}