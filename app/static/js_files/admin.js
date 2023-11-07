var csrftoken = $('meta[name=csrf-token]').attr('content');

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
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
        type: 'GET',
        data: {
            "userId": document.getElementById("userid").value,
            "firstName": document.getElementById("firstname").value,
            "lastName": document.getElementById("lastname").value,
            "email": document.getElementById("email").value
        },
        success: function (data) {
            //do something here based on data
            json = data[0]
            parent = document.getElementById("user-display")
            username = `Name: ${json.name} <br /> `
            email = `Email: ${json.email} <br /> `
            userid = `ID: ${json.id} <br /> `
            parent.innerHTML = username + email + userid
        }
    });
}

var businessId;

function selects_info() { //get new users and set document
    $.ajax({
        url: Flask.url_for("admin_selects_info"),
        type: 'GET',
        dataType: 'json',
        data: {
            "businessId": document.getElementById("businessid").value
        },
        success: function (data) {
            //alert(JSON.stringify(data))
            //do something here based on data

            document.getElementById("business-display").innerHTML = "Unmatched users: <br/>"
            let ul = document.createElement("ul")
            for (let i = 0; i < data.unmatchedUsers.length; i++) {
                let user_json = data.unmatchedUsers[i]
                let li = document.createElement("li")
                let output = ""
                output += "Name: " + user_json.name + "<br/>"
                output += "Email: " + user_json.email + "<br/>"
                output += "ID: " + user_json.id + "<br/>"
                output += "Position: " + user_json.mentor_or_mentee + "<br/>"
                li.innerHTML = output
                ul.appendChild(li)
            }
            document.getElementById("business-display").appendChild(ul)
            document.getElementById("business-display").innerHTML += "Matches: <br/>"
            ul.innerHTML = ""
            for (let i = 0; i < data.matchesInfo.length; i++) {
                let li = document.createElement("li")
                let matches = data.matchesInfo[i]

                let match_output = ""
                match_output += "Meeting ID: " + matches.Select.id + " ("
                match_output += "Mentee's Current Meeting #: " + matches.Select.current_meeting_number_mentee + ", "
                match_output += "Mentor's Current Meeting #: " + matches.Select.current_meeting_number_mentor + ")"
                li.innerHTML = match_output

                let li2 = document.createElement("li")
                li2.style.marginLeft = "36px"
                li2.innerHTML = "Mentee: "

                // I will have disappointed my forefathers with this
                let li3 = document.createElement("li")
                li3.style.marginLeft = "36px"
                let mentee = matches.mentee
                let mentee_output = "Name: " + mentee.name + "<br/>"
                mentee_output += "Email: " + mentee.email + "<br/>"
                mentee_output += "ID: " + mentee.id + "<br/>"
                li3.innerHTML = mentee_output
                li2.appendChild(li3)
                li.appendChild(li2)

                li2 = document.createElement("li")
                li2.style.marginLeft = "36px"
                li2.innerHTML = "Mentor:"

                li3 = document.createElement("li")
                li3.style.marginLeft = "36px"
                let mentor = matches.mentee
                let mentor_output = "Name: " + mentor.name + "<br/>"
                mentor_output += "Email: " + mentor.email + "<br/>"
                mentor_output += "ID: " + mentor.id + "<br/>"
                li3.innerHTML = mentor_output
                li2.appendChild(li3)

                li.appendChild(li2)

                ul.appendChild(li)
            }
            document.getElementById("business-display").appendChild(ul)
        }
    });
}


function user_matches() { //get new users and set document
    $.ajax({
        url: Flask.url_for("admin_user_matches"),
        type: 'GET',
        data: {
            "businessId": document.getElementById("businessid").value
        },
        success: function (data) {
            //do something here based on data)
            document.getElementById("business-display").innerHTML = ""
            let ul = document.createElement("ul")
            for (let i = 0; i < data.length; i++) {
                let mentee_json = data[i]
                let li = document.createElement("li")
                let output = ""
                output += "Mentee email: " + mentee_json.mentee_email + "<br/>"
                output += "Mentee ID: " + mentee_json.mentee_id + "<br/>"
                output += "Mentors: " + "<br/>"
                li.innerHTML = output
                for (let i = 0; i < mentee_json.mentors.length; i++) {
                    let li2 = document.createElement("li")
                    li2.style.marginLeft = "36px"
                    let mentor = mentee_json.mentors[i]
                    let mentor_output = "Email: " + mentor.mentor_email + "<br/>"
                    mentor_output += "ID: " + mentor.mentor_id + "<br/>"
                    li2.innerHTML = mentor_output
                    li.appendChild(li2)
                }
                ul.appendChild(li)
            }
            document.getElementById("business-display").appendChild(ul)
        }
    });
}


function feed_for_user() { //get new users and set document
    $.ajax({
        url: Flask.url_for("admin_lookup_user_feed"),
        type: 'GET',
        data: {
            "userid": document.getElementById("userid").value
        },
        success: function (data) {
            //do something here based on data)
            document.getElementById("user-display").innerHTML = JSON.stringify(data)
        }
    });
}


function get_all_user_feed() { //get new users and set document
    $.ajax({
        url: Flask.url_for("admin_lookup_user_feed_all"),
        type: 'GET',
        data: {
            "userid": document.getElementById("userid").value
        },
        success: function (data) {
            //do something here based on data)
            document.getElementById("user-display").innerHTML = JSON.stringify(data)
        }
    });
}


function unmatch_users() { //unmatch two users
    $.ajax({
        url: Flask.url_for("admin_delete_match"),
        type: 'POST',
        data: {
            "menteeId": document.getElementById("menteeid").value,
            "mentorId": document.getElementById("mentorid").value
        },
        success: function (data) {
            //do something here based on data)
            document.getElementById("match-display").innerHTML = JSON.stringify(data)
        }
    });
}


function get_excel_sheet() { //get new users and set document

    fetch(Flask.url_for("admin_get_business_excel") +
        `?businessId=${document.getElementById("businessid").value}`)
        .then(res => {
            return res.blob();
            //return new Blob(res, { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
        }).then(blob => {

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
        }).catch(err => console.log(err));
}


function business_query() { //get new users and set document
    $.ajax({
        url: Flask.url_for("admin_lookup_business"),
        type: 'GET',
        data: {
            "businessId": document.getElementById("businessid").value
        },
        success: function (data) {
            //do something here based on data
            let output = ""
            output += "Name: " + data.name + "<br/>"
            output += "ID: " + data.id + "<br/>"
            output += "# Employees: " + data.number_employees_currently_registered + "<br/>"
            output += "# Max Employees: " + data.number_employees_maximum + "<br/>"
            document.getElementById("business-display").innerHTML = output
        }
    });
}

// function all_businesses() { //get new users and set document
//     $.ajax({
//         url: Flask.url_for("admin_all_businesses"), 
//         type:'GET',
//         success: function(data) {
//             //do something here based on data
//             console.log(data);
//             // $("#display").html(data);
//             document.getElementById("display").innerHTML = JSON.stringify(data)
//         }
//     });
// }

function users_in_business() {
    $.ajax({
        url: Flask.url_for("admin_lookup_users_in_business"),
        type: 'GET',
        data: {
            "businessId": document.getElementById("businessid").value
        },
        success: function (data) {
            //do something here based on data
            document.getElementById("business-display").innerHTML = ""
            let ul = document.createElement("ul")
            for (let i = 0; i < data.length; i++) {
                let user_json = data[i]
                let li = document.createElement("li")
                let output = ""
                output += "Name: " + user_json.name + "<br/>"
                output += "Email: " + user_json.email + "<br/>"
                output += "ID: " + user_json.id + "<br/>"
                output += "Position: " + user_json.mentor_or_mentee + "<br/>"
                li.innerHTML = output
                ul.appendChild(li)
            }
            document.getElementById("business-display").appendChild(ul)
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
        type: 'GET',
        data: {
            "action": document.querySelector('input[name="events"]:checked').value,
            "startTime": document.getElementById("startDate").value + " " + document.getElementById("startTime").value,
            "endTime": document.getElementById("endDate").value + " " + document.getElementById("endTime").value
        },
        success: function (data) {
            //do something here based on data
            // $("#display").html(data);
            parent = document.getElementById("events-table")
            document.getElementById("events-display").innerHTML = "Total data count: " + data.length
            parent.innerHTML = `<tr>
                                    <th>
                                        ID
                                    </th>
                                    <th>
                                        Message
                                    </th>
                                    <th>
                                        Timestamp
                                    </th>
                                    <th>
                                        User ID
                                    </th>
                                </tr>`
            for (let i = 0; i < data.length; i++) {
                row = document.createElement("tr")
                for (const key of Object.keys(data[i])) {
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