/**
 * Created by Artem Kraynev on 24.05.16.
 */

function count_prop(obj) {
    var count = 0;
    for(var i in obj) {
        count++;
    }
    return count;
}

(function () {
    var path = document.location.pathname + "/json",
        request = new XMLHttpRequest();
    request.open('GET', path);
    request.onreadystatechange = function() {
        if (this.readyState = 4) {
            if (this.status == 200) {
                this.jsonParse();
            }
            else {
                console.log("json error!")
            }
        }
    };
    request.send(null);

    request.jsonParse = function () {
        var response = JSON.parse(this.responseText),
            doc = document,
            length = count_prop(response),
            tabEl = doc.getElementById("tableCity"), i;
        for (i = 0; i < length; i++){
            var trEl = doc.createElement("tr"),
                tdElOne = doc.createElement("td"),
                tdElTwo = doc.createElement("td");
            tdElOne.innerHTML = response[i][2];
            tdElTwo.innerHTML = response[i][3];
            tabEl.appendChild(trEl);
            trEl.appendChild(tdElOne);
            trEl.appendChild(tdElTwo);
        }

    };
})();