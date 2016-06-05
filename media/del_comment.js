/**
 * Created by Artem Kraynev on 24.05.16.
 */


(function () {
    var path = document.location.pathname + "/json";
    var request = new XMLHttpRequest();
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
           myForm = document.form;
        myForm.surname.value = response[0][1];
        myForm.nameF.value = response[0][2];
        myForm.middle_name.value = response[0][3];
        myForm.phone.value = response[0][8];
        myForm.email.value = response[0][6];
        myForm.comment.value = response[0][7];
        myForm.idVal.value = response[0][0];
    };
})();