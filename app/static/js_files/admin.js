var csrftoken = $('meta[name=csrf-token]').attr('content');

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    }
});

var userIdInput;
var firstNameInput;
var lastNameInput;
var emailInput;

function lookup_user() { //get new users and set document
    $.ajax({
        url: Flask.url_for("admin_lookup_user"), 
        type:'GET',
        data: {
            "userId" : document.getElementById("userid").value,
            "firstName" : document.getElementById("firstname").value,
            "lastName" : document.getElementById("lastname").value,
            "email" : document.getElementById("email").value
        },
        success: new function(data) {
            //do something here based on data
            document.getElementById("user-display").innerHTML = JSON.stringify(data)
        }
    });
}

var businessId;

function selects_info() { //get new users and set document
    $.ajax({
        url: Flask.url_for("admin_selects_info"), 
        type:'GET',
        data: {
            "businessId" : document.getElementById("businessid").value
        },
        success: new function(data) {
            //do something here based on data
            document.getElementById("business-display").innerHTML = JSON.stringify(data)
        }
    });
}


function user_matches() { //get new users and set document
    $.ajax({
        url: Flask.url_for("admin_user_matches"), 
        type:'GET',
        data: {
            "businessId" : document.getElementById("businessid").value
        },
        success: new function(data) {
            //do something here based on data
            document.getElementById("business-display").innerHTML = JSON.stringify(data)
        }
    });
}


function business_query() { //get new users and set document
    $.ajax({
        url: Flask.url_for("admin_lookup_business"), 
        type:'GET',
        data: {
            "businessId" : document.getElementById("businessid").value
        },
        success: function(data) {
            //do something here based on data
            document.getElementById("business-display").innerHTML = JSON.stringify(data)
        }
    });
}

function all_businesses() { //get new users and set document
    $.ajax({
        url: Flask.url_for("admin_all_businesses"), 
        type:'GET',
        dataType: 'json',
        success: function(data) {
            //do something here based on data
            console.log(data);
            // $("#display").html(data);
            document.getElementById("display").innerHTML = JSON.stringify(data[0])
        }
    });
}