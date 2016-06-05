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
    var request = new XMLHttpRequest();
    request.open('GET', '/view/json');
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
            divEl = doc.getElementById("comments"), i;
        for (i = 0; i < length; i++){
            var pEl = doc.createElement("p"),
                link = doc.createElement("a");
            if (response[i][1] !== null){
               pEl.innerHTML = response[i][1];
                link.innerHTML = "Удалить комментарий";
                link.href = "/del_com=" + response[i][0];
                divEl.appendChild(pEl);
                divEl.appendChild(link);
            }
        }
    };
})();