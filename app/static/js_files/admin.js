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
        success: function(data) {
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
        dataType: 'json',
        data: {
            "businessId" : document.getElementById("businessid").value
        },
        success: function(data) {
            //alert(JSON.stringify(data))
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
        success: function(data) {
            //do something here based on data)
            document.getElementById("business-display").innerHTML = JSON.stringify(data)
        }
    });
}


function feed_for_user() { //get new users and set document
    $.ajax({
        url: Flask.url_for("admin_lookup_user_feed"), 
        type:'GET',
        data: {
            "userid" : document.getElementById("userid").value
        },
        success: function(data) {
            //do something here based on data)
            document.getElementById("user-display").innerHTML = JSON.stringify(data)
        }
    });
}


function get_all_user_matches() { //get new users and set document
    $.ajax({
        url: Flask.url_for("admin_lookup_user_feed_all"), 
        type:'GET',
        data: {
            "userid" : document.getElementById("userid").value
        },
        success: function(data) {
            //do something here based on data)
            document.getElementById("user-display").innerHTML = JSON.stringify(data)
        }
    });
}


function unmatch_users() { //unmatch two users
    $.ajax({
        url: Flask.url_for("admin_delete_match"), 
        type:'POST',
        data: {
            "menteeId" : document.getElementById("menteeid").value,
            "mentorId" : document.getElementById("mentorid").value
        },
        success: function(data) {
            //do something here based on data)
            document.getElementById("match-display").innerHTML = JSON.stringify(data)
        }
    });
}


function get_excel_sheet() { //get new users and set document

    fetch(Flask.url_for("admin_get_business_excel") + 
            `?businessId=${document.getElementById("businessid").value}`)
        .then(res=>{
            return res.blob();
            //return new Blob(res, { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
        }).then(blob=>{

            console.log(blob);
            //download(blob)
            let el = document.createElement("a"); 
            // creates anchor element but doesn't add it to the DOM
            el.setAttribute("download", ["user-statuses.xslx"]) 

            // make the link downloadable on click
            let url = window.URL.createObjectUrl(blob); 
            // creates a url to the retrieved file

            el.href = url; // set the href attribute attribute
            el.click(); 
        }).catch(err=>console.log(err));
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
        success: function(data) {
            //do something here based on data
            console.log(data);
            // $("#display").html(data);
            document.getElementById("display").innerHTML = JSON.stringify(data)
        }
    });
}

function users_in_business() {
    $.ajax({
        url: Flask.url_for("admin_lookup_users_in_business"), 
        type:'GET',
        data: {
            "businessId" : document.getElementById("businessid").value
        },
        success: function(data) {
            //do something here based on data
            console.log(data);
            // $("#display").html(data);
            document.getElementById("display").innerHTML = JSON.stringify(data)
        }
    });
}


/*
"Actions" - the number assigned to each event logged
Exceptions (16)
Edit profile picture failure (18)
Csrf error (17)
Feed info (13)
Chosen person feed info (14)
Uploading file to s3 (8)
Number of users per day (logins - 4 - must separate by timestamp, so this may require its own function).
*/
function get_events() {
    $.ajax({
        url: Flask.url_for("admin_get_events"), 
        type:'GET',
        data: {
            "action" : document.getElementById("eventAction").value,
            "startTime" : document.getElementById("startDate").value + " " + document.getElementById("startTime").value,
            "endTime" : document.getElementById("endDate").value + " " + document.getElementById("endTime").value
        },
        success: function(data) {
            //do something here based on data
            // $("#display").html(data);
            parent = document.getElementById("events-table")
            document.getElementById("events-display").innerHTML = "Total data count: " + data.length
            parent.innerHTML = ""
            for(let i = 0; i < data.length; i++){
                row = document.createElement("tr")
                for(const key of Object.keys(data[i])){
                    column = document.createElement("td")
                    text = document.createTextNode(data[i][key])
                    column.appendChild(text)
                    row.appendChild(column)
                }
                parent.appendChild(row)
            }
        }
    });
}