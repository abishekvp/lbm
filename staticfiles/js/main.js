function notify(code, message) {
    var position = "toast-top-center";
    if (window.location.pathname === "/sign" || window.location.pathname === "/signup") {
        position = "toast-top-right";
    }
    var position = "toast-top-center";
    toastr.options = {
        "closeButton": true,
        "debug": false,
        "progressBar": true,
        "preventDuplicates": true,
        "positionClass": position,
        "onclick": null,
        "showDuration": "400",
        "hideDuration": "1000",
        "timeOut": "7000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "slideDown",
        "hideMethod": "slideUp"
    }
    if (code === 200) {
        toastr.success("", message);
    } else if (code === 407) {
        toastr.warning("", message);
    } else if (code === 500){
        toastr.error("", message);
    } else {
        toastr.info("", message);
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

$('#top-search').on('input', function() {
    var query = $(this).val();
    if (!query || query.length < 3) {
        $('#books-search-result').empty().hide();
        $('#books-result').removeClass('show');
        return;
    }
    $.ajax({
        type: "GET",
        url: "/search-books?query=" + query,
        success: function (response) {
            // Clear previous results
            $('#books-search-result').empty();
            $('#books-result').addClass('show')
            $('#books-search-result').css({
                'display': 'block',
                'position': 'absolute',
                'transform': 'translate3d(-276px, 74px, 0px)',
                'top': '0px',
                'left': '0px',
                'will-change': 'transform'
            });
            // Check if books exist
            if (response.books && response.books.length > 0) {
                response.books.forEach(function(book) {
                    const bookHtml = `
                        <li class="search-book-in-result" id="/library/${book.library}/${book.department}/${book.rack}/${book.id}">
                            <img src="${book.image}" alt="${book.name}">
                            <div class="message-row">
                                <small>${book.release || ''}</small>
                                <a>
                                    <span class="message-user">${book.name}</span><br>
                                    ${book.author ? `Author: ${book.author}` : ''}
                                </a>
                            </div>
                        </li>
                    `;
                    console.log(book.name)
                    $('#books-search-result').append(bookHtml);
                });
            } else {
                $('#books-search-result').html('<p class="m-2">No books found.</p>');
            }
        },
        error: function (error) {
            notify(500, error);
        }
    });
});

$(document).on('click', '.search-book-in-result', function() {
    const targetUrl = $(this).attr('id');
    if (targetUrl) {
        window.location.href = targetUrl;
    }
});

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

function notify_info(message) {
    notify(null, message);
}
function notify_success(message) {
    notify(200, message);
}
function notify_warning(message) {
    notify(407, message);
}
function notify_error(message) {
    notify(500, message);
}