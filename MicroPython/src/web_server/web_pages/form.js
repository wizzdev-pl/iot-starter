var DEFAULT_PLOT_RANGE_SAMPLES = 10;
var DEFAULT_CSV_RANGE_SAMPLES = 20;
var PAGE_TITLE = "WizzDev Mobile IoT";

function setupPage() {
    document.title = PAGE_TITLE;
    updateReading()

}

function setLoadTime() {
    var additionalInformationsDiv = document.getElementById("additionalInformationsDiv");

    var currentdate = new Date();
    var datetime = currentdate.toLocaleString();

    additionalInformationsDiv.innerHTML = "<center><small>Page load time: " + datetime + "</small></center>"
}

function setErrorForReading(errorText) {
    var reading_div = document.getElementById("reading_div");
    reading_div.innerHTML = "Something went wrong. <br />" + truncateString(errorText, 200, '...');
}

function setReading(data) {
    console.log(data)

    var reading_div = document.getElementById("reading_div");
    reading_div.innerHTML = "Last sensor reading:" + data["data"]["value"];
    setLoadTime()
}

function updateReading() {
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

document.querySelector("#setup_form").addEventListener("submit", (e) => {
    e.preventDefault();

    const loadingIndicator = document.getElementsByClassName("full-page-div")[0];
    loadingIndicator.style.display = "flex";
    loadingIndicator.style.opacity = "0.8";

    const submitButton = document.getElementsByClassName("setup_form__submit")[0];
    submitButton.textContent = "Connecting...";

    sendWiFiConfiguration();
})

function sendWiFiConfiguration() {
    const accessPointCredentials = [];

    const setupFormEntriesArray = document.querySelectorAll(".setup_form__entries");

    setupFormEntriesArray.forEach((entry) => {
        const credentials = entry.querySelectorAll("input");
        accessPointCredentials.push({ssid: credentials[0].value, password: credentials[1].value})
    });

    var data = JSON.stringify({"wifi": accessPointCredentials});

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

// Generate new entry section on "Add new AP" button click
// Unique id is required for each label & input pair hence the "newElementsGenerated" variable
let newElementsGenerated = 0;
document.querySelector("#add-new-ap-button").addEventListener("click", () => {
    newElementsGenerated++;

    const newNode = document.querySelector(".setup_form__entries").cloneNode(true);

    const newLabels = newNode.getElementsByTagName("label");
    newLabels[0].setAttribute("for", "ssid" + newElementsGenerated);
    newLabels[1].setAttribute("for", "password" + newElementsGenerated);

    const newInputFields = newNode.getElementsByTagName("input");
    newInputFields[0].setAttribute("id", "ssid" + newElementsGenerated);
    newInputFields[1].setAttribute("id", "password" + newElementsGenerated);
    newInputFields[0].value = "";
    newInputFields[1].value = "";

    // Insert element after last delete button or after the first entry field if no delete button exists
    const allDeleteButtons = document.getElementsByClassName("delete-button");
    if (allDeleteButtons.length !== 0) {
        const lastDeleteButton = allDeleteButtons[allDeleteButtons.length - 1];
        lastDeleteButton.insertAdjacentElement("afterend", newNode);
    } else {
        // There is only one entry section in the DOM if this code section is reached
        const entrySection = document.getElementsByClassName("setup_form__entries")[0];
        entrySection.insertAdjacentElement("afterend", newNode);
    }

    const deleteButton = document.createElement("div");
    deleteButton.setAttribute("class", "delete-button");

    const deleteButtonIcon = document.createElement("img");
    deleteButtonIcon.setAttribute("src", "delete_icon.png");
    deleteButtonIcon.setAttribute("alt", "delete-icon");
    deleteButtonIcon.setAttribute("height", "14");

    const deleteButtonText = document.createElement("p");
    const deleteButtonTextContent = document.createTextNode("Delete");
    deleteButtonText.appendChild(deleteButtonTextContent);

    deleteButton.appendChild(deleteButtonIcon);
    deleteButton.appendChild(deleteButtonText);

    newNode.insertAdjacentElement("afterend", deleteButton);

    deleteButton.addEventListener("click", (e) => {
        const previousEntrySection = e.currentTarget.previousElementSibling;
        previousEntrySection.remove();
        e.currentTarget.remove();
    })
});

function truncateString(str, length, ending) {
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


function parseQuery(queryString) {
    var query = {};
    var pairs = (queryString[0] === '?' ? queryString.substr(1) : queryString).split('&');
    for (var i = 0; i < pairs.length; i++) {
        var pair = pairs[i].split('=');
        query[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1] || '');
    }
    return query;
}
