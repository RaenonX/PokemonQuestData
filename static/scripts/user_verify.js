function onSignInHandle(googleUser, token, email, post_url, redir_url) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', post_url);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.send('token=' + token + '&email=' + email);
    xhr.onload = function () {
        if (xhr.responseText === "PASS") {
            window.location.replace(redir_url);
        } else {
            $("#msg").removeClass("hide").text(" " + xhr.responseText);
        }
    }
}

function getUrlRedirect(default_url) {
    let url = getUrlParam('prev', '');
    if (url == "") {
        url = default_url;
    }
    return url
}

function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function (m, key, value) {
        vars[key] = value;
    });
    return vars;
}

function getUrlParam(parameter, defaultvalue) {
    var urlparameter = defaultvalue;
    if (window.location.href.indexOf(parameter) > -1) {
        urlparameter = getUrlVars()[parameter];
    }
    return urlparameter;
}