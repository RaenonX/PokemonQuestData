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

function onSignIn(googleUser) {
    var id_token = googleUser.getAuthResponse().id_token;
    var email = googleUser.getBasicProfile().getEmail();

    var xhr = new XMLHttpRequest();
    xhr.open('POST', Flask.url_for('frontend.user_verify_post'));
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.send('id=' + id_token + '&email=' + email);
    xhr.onload = function () {
        if (xhr.responseText === "PASS") {
            window.location.replace(getUrlParam('prev', '').replace('%2F', ''));
        } else {
            $("#msg").removeClass("hide").text(xhr.responseText);
        }
    }
}
