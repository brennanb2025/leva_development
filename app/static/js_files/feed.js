var userArr = [];
var userDictUsefulInfo = [];
var csrftoken = $('meta[name=csrf-token]').attr('content');
var isStudent;


function init(isStudentSet) {
    isStudent = isStudentSet;
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    }
});

function remove_loading() {
    document.getElementById("loadingText").style.display = "none"; //hide loading message
}

function get_new_users(callback) { //get new users and set document
    $.get(Flask.url_for("getFeed"), function(data) {
        userArr = data['userArr'];
        userDictUsefulInfo = data['userDictUsefulInfo']
        callback();
    });
}


// new stuff:
function ready_document() { //will check if userArr length == 0 (no matches) and then add the next new user (userArr[0]) to the feed
    if(userArr.length == 0) {
        noFound = document.createElement("p");
        noFound.setAttribute("id", "noFound");
        if(isStudent === "True") {
            noFound.appendChild(document.createTextNode("No mentor matches found."));
        } else {
            noFound.appendChild(document.createTextNode("Please wait until you are selected by a mentee!"));
        }
        document.getElementById("noMatchDiv").appendChild(noFound);
    } else if(isStudent === "False") {
        noFound = document.createElement("p");
        noFound.setAttribute("id", "noFound");
        noFound.appendChild(document.createTextNode("Please wait until you are selected by a mentee!"));
        document.getElementById("noMatchDiv").appendChild(noFound);
    } else {
        for(let i = 0; i < 10; i++) {
            
            if(i >= userArr.length) {
                break;
            }


            mentorCard = document.createElement("div");
            mentorCard.className = "mentor-card";

            pictureCard = document.createElement("div");
            pictureCard.setAttribute("class", "picture-card");
            mentorCard.appendChild(pictureCard);

            circleBorder = document.createElement("div");
            circleBorder.setAttribute("class", "circle-border");
            pictureCard.appendChild(circleBorder);

            profPic = document.createElement("img");
            profPic.setAttribute("class", "profile_picture_small");
            profPic.setAttribute("alt", "profile_picture");
            circleBorder.appendChild(profPic);
            if(userDictUsefulInfo[userArr[i]]['userProfilePicture'] === null) {
                profPic.setAttribute("src", Flask.url_for("static", {"filename": "blank-profile-picture.png"}));
            } else {
                profPic.setAttribute("src", userDictUsefulInfo[userArr[i]]['userProfilePicture']);
            }

            firstName = document.createElement("div");
            firstName.setAttribute("class", "head2");
            firstName.appendChild(document.createTextNode(userDictUsefulInfo[userArr[i]]['userFn']));
            pictureCard.appendChild(firstName);

            lastName = document.createElement("div");
            lastName.setAttribute("class", "head2");
            lastName.appendChild(document.createTextNode(userDictUsefulInfo[userArr[i]]['userLn']));
            pictureCard.appendChild(lastName);

            purpleLine = document.createElement("div");
            purpleLine.setAttribute("class", "purple-line");
            pictureCard.appendChild(purpleLine);

            currOccupation = document.createElement("div");
            currOccupation.setAttribute("class", "division");
            currOccupation.appendChild(document.createTextNode(userDictUsefulInfo[userArr[i]]['userCurrentOccupation']));
            pictureCard.appendChild(currOccupation);



            infoCard = document.createElement("div");
            infoCard.setAttribute("class", "info-card");
            mentorCard.appendChild(infoCard);

            matchNum = document.createElement("div");
            matchNum.setAttribute("class", "head2");
            matchNum.appendChild(document.createTextNode("Match #" + (i+1)));
            infoCard.appendChild(matchNum);

            buttonContainer = document.createElement("div");
            buttonContainer.setAttribute("class", "button-container");
            infoCard.appendChild(buttonContainer);


            if(userDictUsefulInfo[userArr[i]]['resumeURL'] != null) { //only add resume button if they entered a resume.
                resumeBtnContainer = document.createElement("div");
                resumeBtnContainer.className = "rounded-button button1";
                resumeBtn = document.createElement("button");
                resumeBtn.appendChild(document.createTextNode("RESUME"));
                resumeBtn.onclick= function() {window.open(userDictUsefulInfo[userArr[i]]['resumeURL'], '_blank')};
                resumeBtnContainer.appendChild(resumeBtn);
                buttonContainer.appendChild(resumeBtnContainer);

                profileLinkContainer = document.createElement("div");
                profileLinkContainer.className = "rounded-button button2"; //add the button2 (normal)
                profileLink = document.createElement("button");
                profileLink.appendChild(document.createTextNode("FULL PROFILE"));
                profileLink.onclick= function() {location.href = Flask.url_for("view", {"id": userArr[i]})};
                profileLinkContainer.appendChild(profileLink);
                buttonContainer.appendChild(profileLinkContainer);
            } else { //need to change the spacing if no resume was entered
                profileLinkContainer = document.createElement("div");
                profileLinkContainer.className = "rounded-button button2-push-left"; //add the button2 (altered version)
                profileLink = document.createElement("button");
                profileLink.appendChild(document.createTextNode("FULL PROFILE"));
                profileLink.onclick= function() {location.href = Flask.url_for("view", {"id": userArr[i]})};
                profileLinkContainer.appendChild(profileLink);
                buttonContainer.appendChild(profileLinkContainer);
            }


            bio = document.createElement("div");
            bio.setAttribute("class", "text1");
            bio.appendChild(document.createTextNode(userDictUsefulInfo[userArr[i]]['userBio']));
            infoCard.appendChild(bio);

            matchesDiv = document.createElement("div");
            matchesDiv.setAttribute("class", "centerThin");
            infoCard.appendChild(matchesDiv);

            matchingInterests = document.createElement("div");
            matchingInterests.appendChild(document.createTextNode("Matching interests"));
            matchingInterests.setAttribute("class", "headerText");
            matchesDiv.appendChild(matchingInterests);

            whiteContainer1 = document.createElement("div");
            whiteContainer1.setAttribute("class", "whiteContainer");
            regText1 = document.createElement("div");
            regText1.setAttribute("class", "regText");
            if(userDictUsefulInfo[userArr[i]]['interest matches'].length == 0) {
                regText1.appendChild(document.createTextNode("None"));
                regText1.appendChild(document.createElement("br"));
            } else {
                for(let j = 0; j < userDictUsefulInfo[userArr[i]]['interest matches'].length; j++) {
                    regText1.appendChild(document.createTextNode(userDictUsefulInfo[userArr[i]]['interest matches'][j]));
                    regText1.appendChild(document.createElement("br"));
                }
            }
            whiteContainer1.appendChild(regText1);
            matchesDiv.appendChild(whiteContainer1);
            //line break
            // matchesDiv.appendChild(document.createElement("br"));
            // matchesDiv.appendChild(document.createElement("br"));
            // matchesDiv.appendChild(document.createElement("br"));
            //matching career interests
            matchingCareerInterests = document.createElement("div");
            matchingCareerInterests.appendChild(document.createTextNode("Matching career interests"));
            matchingCareerInterests.setAttribute("class", "headerText");
            matchesDiv.appendChild(matchingCareerInterests);

            whiteContainer2 = document.createElement("div");
            whiteContainer2.setAttribute("class", "whiteContainer");
            regText2 = document.createElement("div");
            regText2.setAttribute("class", "regText");
            if(userDictUsefulInfo[userArr[i]]['career matches'].length == 0) {
                regText2.appendChild(document.createTextNode("None"));
                regText2.appendChild(document.createElement("br"));
            } else {
                for(let j = 0; j < userDictUsefulInfo[userArr[i]]['career matches'].length; j++) {
                    regText2.appendChild(document.createTextNode(userDictUsefulInfo[userArr[i]]['career matches'][j]));
                    regText2.appendChild(document.createElement("br"));
                }
            }
            whiteContainer2.appendChild(regText2);
            matchesDiv.appendChild(whiteContainer2);
            //line break
            // matchesDiv.appendChild(document.createElement("br"));
            // matchesDiv.appendChild(document.createElement("br"));
            // matchesDiv.appendChild(document.createElement("br"));
            //matching schools
            matchingEducation = document.createElement("div");
            matchingEducation.appendChild(document.createTextNode("Matching education"));
            matchingEducation.setAttribute("class", "headerText");
            matchesDiv.appendChild(matchingEducation);

            whiteContainer3 = document.createElement("div");
            whiteContainer3.setAttribute("class", "whiteContainer");
            regText3 = document.createElement("div");
            regText3.setAttribute("class", "regText");
            if(userDictUsefulInfo[userArr[i]]['school matches'].length == 0) {
                regText3.appendChild(document.createTextNode("None"));
                regText3.appendChild(document.createElement("br"));
            } else {
                for(let j = 0; j < userDictUsefulInfo[userArr[i]]['school matches'].length; j++) {
                    regText3.appendChild(document.createTextNode(userDictUsefulInfo[userArr[i]]['school matches'][j]));
                    regText3.appendChild(document.createElement("br"));
                }
            }
            whiteContainer3.appendChild(regText3);
            matchesDiv.appendChild(whiteContainer3);


            //submit form stuff

            let surroundingForm = document.createElement("form");
            surroundingForm.setAttribute("id", "form" + i);
            surroundingForm.setAttribute("action", "/mentor");
            surroundingForm.setAttribute("method", "POST"); 
            surroundingForm.setAttribute("enctype", "multipart/form-data");
            inputCSRF = document.createElement("input");
            inputCSRF.type = "hidden";
            inputCSRF.name = "csrf_token";
            inputCSRF.value = csrftoken;
            surroundingForm.appendChild(inputCSRF);

            userID = document.createElement("input");
            userID.setAttribute("name", "userID");
            userID.value = userArr[i];
            userID.type = "hidden";
            surroundingForm.appendChild(userID); //to get back in flask

            userScore = document.createElement("input");
            userScore.setAttribute("name", "userScore");
            userScore.value = userDictUsefulInfo[userArr[i]]['score'];
            userScore.type = "hidden";
            surroundingForm.appendChild(userScore); //to get back in flask

            userIdx = document.createElement("input");
            userIdx.setAttribute("name", "userIdx");
            userIdx.value = i;
            userIdx.type = "hidden";
            surroundingForm.appendChild(userIdx); //to get back in flask

            chooseMentorContainer = document.createElement("div");
            chooseMentorContainer.className = "rounded-button button1";
            chooseBtn = document.createElement("button");
            chooseBtn.appendChild(document.createTextNode("Select this mentor"));
            chooseInput = document.createElement("input");
            chooseInput.setAttribute("type", "submit");
            chooseInput.setAttribute("name", "submit_right");
            chooseInput.style.display = 'none';
            chooseBtn.onclick = function() {surroundingForm.submit();}
            chooseBtn.appendChild(chooseInput);
            chooseMentorContainer.appendChild(chooseBtn);
            surroundingForm.appendChild(chooseMentorContainer);
            infoCard.appendChild(surroundingForm);

            let matchTable = document.getElementById("matchTable");
            matchTable.appendChild(mentorCard);
        }
        
    }
    //fadeIn(); //not in a callback but it's the last thing that happens so it's ok.
}






/*
function chooseBtnClickClosure(idx) {
    chooseBtnClick(idx);
}

function chooseBtnClick(idx) {
    //post the yes to flask
    $.ajax({
        type: "POST",
        method:"POST",
        url: Flask.url_for("feed"),
        data: { target_user: userArr[idx]},
        success: function(data) {
            console.log("success"); // show response
        }
    });
    alert("Chose: " + userDictUsefulInfo[userArr[i]]['userFn'] + " " + userDictUsefulInfo[userArr[i]]['userLn']);
}*/