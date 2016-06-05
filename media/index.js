/**
 * Created by Artem Kraynev on 23.05.16.
 */


function count_prop(obj) {
    var count = 0;
    for(var i in obj) {
        count++;
    }
    return count;
}

(function () {
    var request = new XMLHttpRequest();
    request.open('GET', '/json');
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
       var response = JSON.parse(this.responseText);
        var doc = document,
            length = count_prop(response),
            ulEl = doc.getElementById("list"), i;
        for (i = 1; i < length; i++){
            var link = doc.createElement("a"),
                liEl = doc.createElement("li");
            link.innerHTML = "Форма" + " " + response[i][0].toString();
            link.href = "/form=" + response[i][0].toString();
            ulEl.appendChild(liEl);
            liEl.appendChild(link);
        }
    };
})();

