var userArr = [];
var userDictUsefulInfo = [];
var csrftoken = $('meta[name=csrf-token]').attr('content')
var isStudent;

//gallery stuff
var slideIndex = 1;
// Next/previous controls
function plusSlides(n) {
    showSlides(slideIndex += n);
}
// Thumbnail image controls
function currentSlide(n) {
    showSlides(slideIndex = n);
}
function showSlides(n) {
    var i;
    var slides = document.getElementsByClassName("mySlides");
    if(slides.length == 0) {
        return;
    }
    if (n > slides.length) {slideIndex = 1}
    if (n < 1) {slideIndex = slides.length}
    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    slides[slideIndex-1].style.display = "block";
}



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
            noFound.appendChild(document.createTextNode("No student matches found."));
        }
        document.getElementById("noMatchDiv").appendChild(noFound);
    } else {
        
        addDiv = document.createElement("div");

        addDiv.appendChild(document.createElement("br"));

        centerWide = document.createElement("div");
        centerWide.setAttribute("class", "centerWide");

        userName = document.createElement("div");
        userName.setAttribute("class", "userTitle");
        userName.appendChild(document.createTextNode(userDictUsefulInfo[userArr[0]]['userFn'] + " " + userDictUsefulInfo[userArr[0]]['userLn']));
        centerWide.appendChild(userName);
        centerWide.appendChild(document.createElement("br"));
        
        if(userDictUsefulInfo[userArr[0]]['userIsStudent'] === "False") {
            currentOccupation = document.createElement("div");
            currentOccupation.setAttribute("class", "userTitle");
            if(userDictUsefulInfo[userArr[0]]['userCurrentOccupation'] == null) {
                currentOccupation.appendChild(document.createTextNode("None"));
            } else {
                currentOccupation.appendChild(document.createTextNode(userDictUsefulInfo[userArr[0]]['userCurrentOccupation']));
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
        mySlides1 = document.createElement("div");
        mySlides1.setAttribute("class", "mySlides");

        profilePicture = document.createElement("img");
        profilePicture.setAttribute("class", "feedMedia");
        profilePicture.setAttribute("alt", "profile_picture");
        if(userDictUsefulInfo[userArr[0]]['userProfilePicture'] === null) {
            console.log("setting not have pic");
            profilePicture.setAttribute("src", Flask.url_for("static", {"filename": "blank-profile-picture.png"}));
        } else {
            profilePicture.setAttribute("src", userDictUsefulInfo[userArr[0]]['userProfilePicture']);
        }
        mySlides1.appendChild(profilePicture);
        container.appendChild(mySlides1);

        mySlides2 = document.createElement("div");
        mySlides2.setAttribute("class", "mySlides");
        if(userDictUsefulInfo[userArr[0]]['userProfilePicture'] === null) {
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
            introVidSrc.setAttribute("src", userDictUsefulInfo[userArr[0]]['userIntroVideo']);
            introVidSrc.setAttribute("type", "video/mp4");
            introVid.appendChild(document.createTextNode("Your browser does not support the video tag."));
            introVid.appendChild(introVidSrc);
            mySlides2.appendChild(introVid);
        }
        container.appendChild(mySlides2);

        prevBtn = document.createElement("a");
        prevBtn.setAttribute("class", "prev");
        prevBtn.onclick = function() { plusSlides(-1); };
        prevBtn.appendChild(document.createTextNode("❮"));
        container.appendChild(prevBtn);

        nextBtn = document.createElement("a");
        nextBtn.setAttribute("class", "next");
        nextBtn.onclick = function() { plusSlides(1); };
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
        userBio.appendChild(document.createTextNode(userDictUsefulInfo[userArr[0]]['userBio']));
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
        if(userDictUsefulInfo[userArr[0]]['interest matches'].length == 0) {
            regText1.appendChild(document.createTextNode("None"));
            regText1.appendChild(document.createElement("br"));
        } else {
            for(var j = 0; j < userDictUsefulInfo[userArr[0]]['interest matches'].length; j++) {
                regText1.appendChild(document.createTextNode(userDictUsefulInfo[userArr[0]]['interest matches'][j]));
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
        if(userDictUsefulInfo[userArr[0]]['career matches'].length == 0) {
            regText2.appendChild(document.createTextNode("None"));
            regText2.appendChild(document.createElement("br"));
        } else {
            for(var j = 0; j < userDictUsefulInfo[userArr[0]]['career matches'].length; j++) {
                regText2.appendChild(document.createTextNode(userDictUsefulInfo[userArr[0]]['career matches'][j]));
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
        if(userDictUsefulInfo[userArr[0]]['school matches'].length == 0) {
            regText3.appendChild(document.createTextNode("None"));
            regText3.appendChild(document.createElement("br"));
        } else {
            for(var j = 0; j < userDictUsefulInfo[userArr[0]]['school matches'].length; j++) {
                regText3.appendChild(document.createTextNode(userDictUsefulInfo[userArr[0]]['school matches'][j]));
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

        //NO button
        optionTdLeft = document.createElement("td");
        optionTdLeft.setAttribute("class", "optionTdLeft");
        noLink = document.createElement("a");
        noLink.setAttribute("class", "optionButtonSide");
        noLink.setAttribute("name", "submit_left");
        //noLink.setAttribute("value", "left"); I don't think I need this
        noLink.onclick = function() {
            matchBtnClick("no");
        }
        noLink.appendChild(document.createTextNode("NO"));
        optionTdLeft.appendChild(noLink);
        optionTr.appendChild(optionTdLeft);

        //SHOW ME MORE button
        optionTdMid = document.createElement("td");
        optionTdMid.setAttribute("class", "optionTdMid");
        showMoreLink = document.createElement("a");
        showMoreLink.setAttribute("class", "optionButtonMid");
        showMoreLink.setAttribute("name", "submit_left");
        //noLink.setAttribute("value", "left"); I don't think I need this
        showMoreLink.setAttribute("href", Flask.url_for("view", {"id": userArr[0]}));
        showMoreLink.appendChild(document.createTextNode("SHOW ME MORE"));
        optionTdMid.appendChild(showMoreLink);
        optionTr.appendChild(optionTdMid);

        //YES button
        optionTdRight = document.createElement("td");
        optionTdRight.setAttribute("class", "optionTdRight");
        yesLink = document.createElement("a");
        yesLink.setAttribute("class", "optionButtonSide");
        yesLink.setAttribute("name", "submit_right");
        //noLink.setAttribute("value", "left"); I don't think I need this
        yesLink.onclick = function() {
            matchBtnClick("yes");
        }
        yesLink.appendChild(document.createTextNode("YES"));
        optionTdRight.appendChild(yesLink);
        optionTr.appendChild(optionTdRight);

        optionTable.appendChild(optionTr);
        centerThin.appendChild(optionTable);
        addDiv.appendChild(centerThin);
        
        //add tray to table
        let matchTable = document.getElementById("matchTable");
        matchTable.appendChild(addDiv);
        
    }
    //fadeIn(); //not in a callback but it's the last thing that happens so it's ok.
}

function matchBtnClick(yesNo) {
    //post the yes or no to flask
    $.ajax({
        type: "POST",
        method:"POST",
        url: Flask.url_for("feed"),
        data: { target_user: userArr[0], yesorno: yesNo},
        success: function(data) {
            console.log("success"); // show response
        }
    });

    userArr.shift(); //remove 1st idx
    if(userArr.length == 0) {
        get_new_users(function() {
            clear_document();
            async function waitThenShowSlides() { //show the slides
                return result = await ready_document();
            }; 
            waitThenShowSlides().then(function() {
                showSlides(slideIndex);
            });
        });
    } else { //^must do this synchronously. So that's why the if/else.
        clear_document();
        async function waitThenShowSlides() { //show the slides
            return result = await ready_document();
        }; 
        waitThenShowSlides().then(function() {
            showSlides(slideIndex);
        });
    }
    //scroll to top
    window.scrollTo(0, 0);
    slideIndex = 1; //reset gallery position
}

function clear_document() {
    let matchTable = document.getElementById("matchTable");
    /*fadeOut(function() {
        //callback v*/
    while (matchTable.firstChild) { //while has a child
        matchTable.removeChild(matchTable.lastChild); //remove the last child (last because removing last is faster than removing first.)
    }
    //});
}

/*
function fadeOut(callback) {
    console.log("fadeOut starting");
    let matchTable = document.getElementById("matchTable");
    var op = 1;  // initial opacity
    var timer = setInterval(function () {
        if (op <= 0.05){
            clearInterval(timer);
            matchTable.style.display = 'none';
            callback();
        }
        matchTable.style.opacity = op;
        matchTable.style.filter = 'alpha(opacity=' + op * 100 + ")";
        op -= op * 0.1;
    }, 20);
    console.log("fadeOut done");
}
function fadeIn() {
    console.log("fadeIn starting");
    let matchTable = document.getElementById("matchTable");
    var op = 0.05;  // initial opacity
    matchTable.style.display = 'block';
    var timer = setInterval(function () {
        if (op >= 1){
            clearInterval(timer);
        }
        matchTable.style.opacity = op;
        matchTable.style.filter = 'alpha(opacity=' + op * 100 + ")";
        op += op * 0.1;
    }, 20);
    console.log("fadeIn done");
    matchTable.style.opacity = '1';
}
*/