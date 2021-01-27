var DEFAULT_PLOT_RANGE_SAMPLES = 10;
var DEFAULT_CSV_RANGE_SAMPLES = 20;
var PAGE_TITLE = "WizzDev Mobile IoT";

function setupPage () {
    document.title = PAGE_TITLE;
    updateReading()

}

function setLoadTime () {
    var additionalInformationsDiv = document.getElementById("additionalInformationsDiv");

    var currentdate = new Date();
    var datetime = currentdate.toLocaleString();

    additionalInformationsDiv.innerHTML = "<center><small>Page load time: " + datetime + "</small></center>"
}

function setErrorForReading (errorText) {
    var reading_div = document.getElementById("reading_div");
    reading_div.innerHTML = "Something went wrong. <br />" + truncateString(errorText, 200, '...');
}

function setReading (data) {
    console.log(data)

    var reading_div = document.getElementById("reading_div");
    reading_div.innerHTML = "Last sensor reading:" + data["data"]["value"];
    setLoadTime()
}

function updateReading () {
    data = null;

    var xhtmlobj = new XMLHttpRequest();
    xhtmlobj.onreadystatechange = function () {
        if ((this.readyState === 4)) {
            if ((this.status === 200)) {
                data = JSON.parse(this.responseText);
                console.log(data);
                if (data["status"] !== 0)
                    setErrorForReading(data["status_text"]);
                else
                    setReading(data);
            } else {
                setErrorForDevices(xhtmlobj.responseText);
            }
        }
    };
    xhtmlobj.onerror = function () {
        alert("Connection error! Connection probably lost, try to reload page.");
        var reading_div = document.getElementById("reading_div");
        reading_div.innerHTML = "Failed to communicate!";
    };


    xhtmlobj.open("GET", "/measurement", true);
    xhtmlobj.send();
}

function sendWiFiConfiguration () {
    var password = document.getElementById("formPassword").value;
    var ssid = document.getElementById("formSsid").value;

    console.log('Click ' + formPassword);

    var data = JSON.stringify({"wifi": {"ssid": ssid, "password": password}});

    var xhtmlobj = new XMLHttpRequest();
    xhtmlobj.open("POST", '/config', true);
    xhtmlobj.setRequestHeader("Content-Type", "application/json");
    xhtmlobj.onreadystatechange = function () {
        if ((this.readyState === 4)) {
            if ((this.status === 200)) {
                data = JSON.parse(this.responseText);
                if (data["status"] !== 0)
                    alert("Failed to set config for the device! " + data["status_text"]);
                else {
                    alert("SUCCESS! Device configured succesfully!");
                }
            } else {
                alert("Failed to send config to the device! " + xhtmlobj.responseText);
            }
        }
    }
    xhtmlobj.onerror = function () {
        alert("Connection error! Connection probably lost, try to reload page!");
    };
    xhtmlobj.send(data);


}

function truncateString (str, length, ending) {
    str = String(str);
    if (length == null) {
        length = 100;
    }
    if (ending == null) {
        ending = '...';
    }
    if (str.length > length) {
        return str.substring(0, length - ending.length) + ending;
    } else {
        return str;
    }
}


function parseQuery (queryString) {
    var query = {};
    var pairs = (queryString[0] === '?' ? queryString.substr(1) : queryString).split('&');
    for (var i = 0; i < pairs.length; i++) {
        var pair = pairs[i].split('=');
        query[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1] || '');
    }
    return query;
}
