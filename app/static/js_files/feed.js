var userArr = [];
var userDictUsefulInfo = [];
var csrftoken = $('meta[name=csrf-token]').attr('content')
var isStudent;


/*var chooseBtn = document.createElement("div");
chooseBtn.setAttribute("class", "chooseBtn");
chooseBtn.setAttribute("id", "chooseBtn");
chooseImg = document.createElement("img");
chooseImg.setAttribute("src", Flask.url_for("static", {"filename": "choose_arrow.png"}));
chooseImg.setAttribute("class", "fillSize");
chooseBtn.appendChild(chooseImg);*/
//TODO:
//chooseBtn onclick
//add chooseBtn to various places on chooseUser


//gallery stuff
var slideIndex = [];
// Next/previous controls
/*function plusSlides(n, containerId, idx) {
    showSlides(slideIndex[idx] += n, containerId, idx);
}*/

//plusSlidesClosure is for the +/- arrows on each picture. 
//It maintains the scope of the variables passed during the buttons' creation by passing them 
//into another function - the one that actually adds/subtracts and then shows the slides
//see: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Closures
function plusSlidesClosure(n, containerId, idx) {
    return function() {
        showSlides(slideIndex[idx] += n, containerId, idx);
    }
}
// Thumbnail image controls
function currentSlide(n, containerId, idx) {
    document.getElementsByClassName("container");
    showSlides(slideIndex[idx] = n, containerId, idx);
}


function setupSlideIndex() {
    var containers = document.getElementsByClassName("container");
    for(i = 0; i < containers.length; i++) {
        slideIndex.push(2); //second and third slide. Note: not sure if this works with > 2 slides.
    }
}

function showAllSlides() {
    var containers = document.getElementsByClassName("container");
    for(i = 0; i < containers.length; i++) {
        showSlides(0, containers[i].id, slideIndex[i]);
    }
}

function showSlides(n, containerId, idx) {
    var i;
    var slides = document.getElementById(containerId).getElementsByClassName("mySlides");
    if(slides.length == 0) {
        return;
    }
    if (n > slides.length) {slideIndex[idx] = 1}
    if (n < 1) {slideIndex[idx] = slides.length}
    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    slides[slideIndex[idx]-1].style.display = "block";
}

//this was for the pink highlight effect
/*
function chooseUser(userDivElementId, idx) {
    var chosenUser = document.getElementById("chosenUser");
    console.log("choosing: " + userDivElementId + " " + idx);
    //unchoose prev user
    if(chosenUser != -1) { //they already chose a user
        chosenElems = document.querySelectorAll(".userDivChosen"); //get by class name - should only be 1
        console.log(chosenElems);
        for(i = 0; i < chosenElems.length; i++) {
            chosenElems[i].classList.add("userDiv"); //unchoose it
            chosenElems[i].classList.remove("userDivChosen");
        }
    }
    chosenUser.value = idx;

    chooseThisUserElem = document.getElementById(userDivElementId);
    chooseThisUserElem.classList.remove('userDiv');
    chooseThisUserElem.classList.add('userDivChosen'); //change the class

    parent = chooseThisUserElem.parentNode;
    

}
*/


function init(isStudentSet) {
    isStudent = isStudentSet;
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    }
})

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
    } else {
        for(i = 0; i < 10; i++) {
            
            if(i >= userArr.length) {
                break;
            }

            surroundingForm = document.createElement("form");
            surroundingForm.setAttribute("id", "form" + i);
            surroundingForm.setAttribute("action", "/feed");
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


            addDiv = document.createElement("div");
            addDiv.setAttribute("class", "userDiv");
            

            addDiv.appendChild(document.createElement("br"));
            addDiv.setAttribute("id", "userDiv" + i);
            //this was for the pink highlight effect
            /*(function(i, addDivId) {
                addDiv.addEventListener('click', (e) => {
                    chooseUser(addDivId, i);
                });
            })(i, addDiv.id);*/

            centerWide = document.createElement("div");
            centerWide.setAttribute("class", "centerWide");

            //line break
            centerWide.appendChild(document.createElement("br"));

            indexUser = document.createElement("div");
            indexUser.setAttribute("class", "indexNumber")
            indexUser.appendChild(document.createTextNode(i+1));
            centerWide.appendChild(indexUser);
            //line break
            centerWide.appendChild(document.createElement("br"));



            userName = document.createElement("div");
            userName.setAttribute("class", "userTitle");
            userName.appendChild(document.createTextNode(userDictUsefulInfo[userArr[i]]['userFn'] + " " + userDictUsefulInfo[userArr[i]]['userLn']));
            centerWide.appendChild(userName);
            centerWide.appendChild(document.createElement("br"));
            
            if(userDictUsefulInfo[userArr[i]]['userIsStudent'] === "False") {
                currentOccupation = document.createElement("div");
                currentOccupation.setAttribute("class", "userTitle");
                if(userDictUsefulInfo[userArr[i]]['userCurrentOccupation'] == null) {
                    currentOccupation.appendChild(document.createTextNode("None"));
                } else {
                    currentOccupation.appendChild(document.createTextNode(userDictUsefulInfo[userArr[i]]['userCurrentOccupation']));
                }
                
                centerWide.appendChild(currentOccupation);
            }

            //line breaks
            centerWide.appendChild(document.createElement("br"));
            centerWide.appendChild(document.createElement("br"));


            //Container for the gallery
            surroundingContainer = document.createElement("div");
            surroundingContainer.setAttribute("class", "feedMedia centerDiv grayBackground");
            container = document.createElement("div");
            container.setAttribute("class", "container");
            container.setAttribute("id", "container" + i);
            mySlides1 = document.createElement("div");
            mySlides1.setAttribute("class", "mySlides");

            profilePicture = document.createElement("img");
            profilePicture.setAttribute("class", "feedMedia");
            profilePicture.setAttribute("alt", "profile_picture");
            if(userDictUsefulInfo[userArr[i]]['userProfilePicture'] === null) {
                profilePicture.setAttribute("src", Flask.url_for("static", {"filename": "blank-profile-picture.png"}));
            } else {
                profilePicture.setAttribute("src", userDictUsefulInfo[userArr[i]]['userProfilePicture']);
            }
            mySlides1.appendChild(profilePicture);

            mySlides2 = document.createElement("div");
            mySlides2.setAttribute("class", "mySlides");
            if(userDictUsefulInfo[userArr[i]]['userProfilePicture'] === null) {
                noVidDiv = document.createElement("div");
                noVidDiv.setAttribute("class", "noVidFeed");
                noVidDiv.appendChild(document.createTextNode("No intro video"));
                noVidDiv.appendChild(document.createElement("br"));
                mySlides2.appendChild(noVidDiv);
            } else {
                introVid = document.createElement("video");
                introVid.setAttribute("class", "feedMedia");
                introVid.controls = true;
                introVidSrc = document.createElement("source");
                introVidSrc.setAttribute("class", "feedMedia");
                introVidSrc.setAttribute("src", userDictUsefulInfo[userArr[i]]['userIntroVideo']);
                introVidSrc.setAttribute("type", "video/mp4");
                introVid.appendChild(document.createTextNode("Your browser does not support the video tag."));
                introVid.appendChild(introVidSrc);
                mySlides2.appendChild(introVid);
            }


            container.appendChild(mySlides2);
            container.appendChild(mySlides1);

            prevBtn = document.createElement("a");
            prevBtn.setAttribute("class", "prev");
            //prevBtn.onclick = function() { plusSlidesClosure(-1, container.id, i); };
            prevBtn.onclick = plusSlidesClosure(-1, container.id, i);
            prevBtn.appendChild(document.createTextNode("❮"));
            container.appendChild(prevBtn);

            nextBtn = document.createElement("a");
            nextBtn.setAttribute("class", "next");
            //nextBtn.onclick = function() { plusSlidesClosure(1, container.id, i); };  
            nextBtn.onclick = plusSlidesClosure(1, container.id, i);
            nextBtn.appendChild(document.createTextNode("❯"));
            container.appendChild(nextBtn);

            surroundingContainer.appendChild(container);
            centerWide.appendChild(surroundingContainer);
            
            addDiv.appendChild(centerWide);

            centerThin = document.createElement("div");
            centerThin.setAttribute("class", "centerThin");

            aboutMeText = document.createElement("div");
            aboutMeText.setAttribute("class", "headerText");
            aboutMeText.appendChild(document.createTextNode("About Me"));
            centerThin.appendChild(aboutMeText);

            //bio
            userBio = document.createElement("textarea");
            userBio.setAttribute("id", "bio");
            userBio.setAttribute("class", "bio");
            userBio.setAttribute("readonly", true);
            userBio.appendChild(document.createTextNode(userDictUsefulInfo[userArr[i]]['userBio']));
            centerThin.appendChild(userBio);
            //line breaks
            centerThin.appendChild(document.createElement("br"));
            centerThin.appendChild(document.createElement("br"));
            centerThin.appendChild(document.createElement("br"));
            //matching interests
            matchingInterests = document.createElement("div");
            matchingInterests.appendChild(document.createTextNode("Matching interests"));
            matchingInterests.setAttribute("class", "headerText");
            centerThin.appendChild(matchingInterests);

            whiteContainer1 = document.createElement("div");
            whiteContainer1.setAttribute("class", "whiteContainer");
            regText1 = document.createElement("div");
            regText1.setAttribute("class", "regText");
            if(userDictUsefulInfo[userArr[i]]['interest matches'].length == 0) {
                regText1.appendChild(document.createTextNode("None"));
                regText1.appendChild(document.createElement("br"));
            } else {
                for(var j = 0; j < userDictUsefulInfo[userArr[i]]['interest matches'].length; j++) {
                    regText1.appendChild(document.createTextNode(userDictUsefulInfo[userArr[i]]['interest matches'][j]));
                    regText1.appendChild(document.createElement("br"));
                }
            }
            whiteContainer1.appendChild(regText1);
            centerThin.appendChild(whiteContainer1);
            //line break
            centerThin.appendChild(document.createElement("br"));
            centerThin.appendChild(document.createElement("br"));
            centerThin.appendChild(document.createElement("br"));
            //matching career interests
            matchingCareerInterests = document.createElement("div");
            matchingCareerInterests.appendChild(document.createTextNode("Matching career interests"));
            matchingCareerInterests.setAttribute("class", "headerText");
            centerThin.appendChild(matchingCareerInterests);

            whiteContainer2 = document.createElement("div");
            whiteContainer2.setAttribute("class", "whiteContainer");
            regText2 = document.createElement("div");
            regText2.setAttribute("class", "regText");
            if(userDictUsefulInfo[userArr[i]]['career matches'].length == 0) {
                regText2.appendChild(document.createTextNode("None"));
                regText2.appendChild(document.createElement("br"));
            } else {
                for(var j = 0; j < userDictUsefulInfo[userArr[i]]['career matches'].length; j++) {
                    regText2.appendChild(document.createTextNode(userDictUsefulInfo[userArr[i]]['career matches'][j]));
                    regText2.appendChild(document.createElement("br"));
                }
            }
            whiteContainer2.appendChild(regText2);
            centerThin.appendChild(whiteContainer2);
            //line break
            centerThin.appendChild(document.createElement("br"));
            centerThin.appendChild(document.createElement("br"));
            centerThin.appendChild(document.createElement("br"));
            //matching schools
            matchingEducation = document.createElement("div");
            matchingEducation.appendChild(document.createTextNode("Matching education"));
            matchingEducation.setAttribute("class", "headerText");
            centerThin.appendChild(matchingEducation);

            whiteContainer3 = document.createElement("div");
            whiteContainer3.setAttribute("class", "whiteContainer");
            regText3 = document.createElement("div");
            regText3.setAttribute("class", "regText");
            if(userDictUsefulInfo[userArr[i]]['school matches'].length == 0) {
                regText3.appendChild(document.createTextNode("None"));
                regText3.appendChild(document.createElement("br"));
            } else {
                for(var j = 0; j < userDictUsefulInfo[userArr[i]]['school matches'].length; j++) {
                    regText3.appendChild(document.createTextNode(userDictUsefulInfo[userArr[i]]['school matches'][j]));
                    regText3.appendChild(document.createElement("br"));
                }
            }
            whiteContainer3.appendChild(regText3);
            centerThin.appendChild(whiteContainer3);

            //line break
            centerThin.appendChild(document.createElement("br"));
            centerThin.appendChild(document.createElement("br"));

            optionTable = document.createElement("table");
            optionTable.setAttribute("class", "optionTable");
            optionTr = document.createElement("tr");
            optionTr.setAttribute("class", "optionTr");

            //SHOW ME MORE button
            optionTdMid = document.createElement("td");
            optionTdMid.setAttribute("class", "optionTdMid");
            showMoreLink = document.createElement("a");
            showMoreLink.setAttribute("class", "optionButtonMid");
            showMoreLink.setAttribute("name", "submit_left");
            //noLink.setAttribute("value", "left"); I don't think I need this
            showMoreLink.setAttribute("href", Flask.url_for("view", {"id": userArr[i]}));
            showMoreLink.appendChild(document.createTextNode("Show me more"));
            optionTdMid.appendChild(showMoreLink);
            optionTr.appendChild(optionTdMid);

            //YES button
            optionTdRight = document.createElement("td");
            optionTdRight.setAttribute("class", "optionTdRight");
            yesLink = document.createElement("input");
            yesLink.setAttribute("type", "submit");
            yesLink.setAttribute("class", "optionButtonSide");
            yesLink.setAttribute("name", "submit_right");
            //yesLink.onclick = chooseBtnClickClosure(i);
            yesLink.value = "Select this mentor";
            optionTdRight.appendChild(yesLink);
            optionTr.appendChild(optionTdRight);

            optionTable.appendChild(optionTr);
            centerThin.appendChild(optionTable);
            addDiv.appendChild(centerThin);

            surroundingForm.appendChild(addDiv);
            
            //add tray to table
            let matchTable = document.getElementById("matchTable");
            matchTable.appendChild(surroundingForm);

            //separate divs
            separator = document.createElement("div");
            separator.setAttribute("class", "separator");
            matchTable.appendChild(separator);
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