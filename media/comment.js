/**
 * Created by Artem Kraynev on 22.05.16.
 */

(function () {
    var request = new XMLHttpRequest();
    request.open('GET', '/comment/json');
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

    var setVal = function (elId, elVal) {
        var doc = document;
        doc.getElementById(elId).innerHTML = elVal;
    };


    request.jsonParse = function () {
       var response = JSON.parse(this.responseText),
           region = response.region,
           city = response.city;
        setVal("firstRegion", region[1]);
        setVal("secondRegion", region[2]);
        setVal("thirdRegion", region[3]);
        setVal("firstCity", city[1][0]);
        setVal("secondCity", city[1][1]);
        setVal("thirdCity", city[1][2]);
    };

    var doc = document,
        regionSelect = doc.getElementById("region");

    request.changeSelect = function () {
        var selectText = regionSelect.options[regionSelect.selectedIndex].text,
            response = JSON.parse(request.responseText),
            region = response.region,
            city = response.city;
        if (selectText == region[1]){
            setVal("firstCity", city[1][0]);
            setVal("secondCity", city[1][1]);
            setVal("thirdCity", city[1][2]);
        }
        if (selectText == region[2]){
            setVal("firstCity", city[2][0]);
            setVal("secondCity", city[2][1]);
            setVal("thirdCity", city[2][2]);
        } if (selectText == region[3]) {
            setVal("firstCity", city[3][0]);
            setVal("secondCity", city[3][1]);
            setVal("thirdCity", city[3][2]);
        }
    };

    regionSelect.addEventListener("change", request.changeSelect);
})();

