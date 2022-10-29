const entriesPerRow = 3;
const maxRows = 10;
let rowArrCint = [];
let rowArrEdu = [];
let rowArrTag = [];
let formProfileSubmit;
let formPwdSubmit;

let cropper;

var csrftoken = $('meta[name=csrf-token]').attr('content');

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    }
});

function post_image() {
    originalPicture = document.getElementById("inputFile");
    croppedImg = document.getElementById("croppedImgFile");
    if(originalPicture.value === "") {
        errorNoPictureSelected();
    } else {
        let formData = new FormData(); //create new form to submit (with just the cropped image)
        if(croppedImg.value === "") {
            alert("No new image found. Please click on the cropped image before applying changes.");
        } else {
            formData.append('croppedImgFile', croppedImg.files[0]);
            $.ajax({
                type: 'POST',
                url: Flask.url_for("editProfPic"), 
                data : formData,
                processData: false,  // tell jQuery not to process the data
                contentType: false,  // tell jQuery not to set contentType
                success : function(data) {
                    window.location.reload();
                }
            });
        }
    }
}

function errorNoPictureSelected() {
    alert("No picture selected");
}


function init(contact_method) {
    //image stuff
    inputFile = document.getElementById("inputFile");
    if(inputFile) { //ensure not null
        inputFile.addEventListener('change', function() {
            if (inputFile.files && inputFile.files[0]) {

                if(((inputFile.files[0].size/1024)/1024).toFixed(4) > 5) { // file size < 5 MB
                    alert("File too big (max file size = 5 MB).");
                    document.getElementById('inputFile').value = "";
                    return;
                }
                var reader = new FileReader();
                reader.onload = function (e) {
                    
                    img = document.getElementById("image");
                    if(img) {
                        cropper.destroy(); //destroy the cropper 
                        img.remove(); //delete the previous img if it exists
                    }
                    newImg = document.createElement("img");
                    newImg.setAttribute("id", "image");
                    newImg.setAttribute("class", "image_container pad_bottom");
                    newImg.setAttribute("src", e.target.result);
                    newImg.setAttribute("alt", "your image");
                    newImg.style.display = "none"; //hide image
                    newImg.addEventListener('load', function(event) {
                        newImg.style.display = "block"; //show image
                        
                        cropper = new Cropper(newImg, {
                            aspectRatio: 1/1,
                            minCropBoxWidth: 100,
                            minCropBoxHeight: 100,
                        });
                        
                        set_cropper_listener();

                    });
                    
                    document.getElementById("image_container_div").appendChild(newImg);
                    document.getElementById("image_container_div").style.display = "block"; //show all image
                    //document.getElementById("imgStuff").style.display = "block"; //show all image stuff
                    document.getElementById("scrollAdvice").style.display = "block"; //show advice
                    //remove cropping
                    //document.getElementById("crop-btn").style.display = "block"; //show advice
                    //delete old img thing if it exists, create new image and appendchild to image_container_div.
                };

                reader.readAsDataURL(inputFile.files[0]);

                if(check_image_size(inputFile.files[0], false)) {
                    //put it in the image as croppedImgFile right now
                    let file = new File([inputFile.files[0]], document.getElementById("inputFile").files[0].name,{type:"image/jpeg", lastModified:new Date().getTime()});  
                    // Create a new container
                    let container = new DataTransfer();
                    // Add the image file to the container
                    container.items.add(file);
                    document.getElementById("croppedImgFile").files = container.files;
                }

            }
        }, false);
    } else {
        //won't proc because of defer
        console.log("Null");
    }

    /*
    //video stuff
    videoFile = document.getElementById("videoFile");
    if(videoFile) { //ensure not null
        videoFile.addEventListener('change', function() {
            if (videoFile.files && videoFile.files[0]) {

                if(document.getElementById("newVideoSource")) {
                    document.getElementById("newVideoSource").remove(); //delete the previous video source if it exists
                }

                if(((videoFile.files[0].size/1024)/1024).toFixed(4) > 40) { // file size < 40MB
                    alert("File too big (max file size = 40 MB).");
                    document.getElementById('videoFile').value = "";
                    return;
                }
        
                vidSource = document.createElement("source");
                let videoPlacer = document.getElementById("newVideo")
                videoPlacer.preload = 'metadata';

                vidSource.setAttribute("id", "newVideoSource");
                vidSource.setAttribute("type", "video/mp4");
                vidSource.src = URL.createObjectURL(videoFile.files[0]);
                videoPlacer.appendChild(vidSource);
                videoPlacer.load();

                videoPlacer.onloadedmetadata = function() { //when video is fully loaded
                    if(videoPlacer.duration < 30) { //<30 seconds is ok
                        videoPlacer.style.display = "block"; //show new video
                        document.getElementById("videoDuration").value = videoPlacer.duration; //new duration
                        document.getElementById("vidStuff").style.display = "block"; //show all video back
                    } else {
                        if(document.getElementById("newVideoSource")) {
                            document.getElementById("newVideoSource").remove(); //delete the previous video source if it exists
                        }
                        alert("Video is too long (max duration = 30 seconds).");
                        document.getElementById('videoFile').value = "";
                        videoPlacer.style.display = "none"; //hide once again.
                        document.getElementById("videoDuration").value = "";
                    }
                }

            }
        }, false);
    } else {
        //won't proc because of defer
        console.log("Null");
    }
    */

    //document.getElementById("scrollAdvice").style.display = "none"; //hide advice
    //comment out cropping
    //document.getElementById("cropPreview").style.display = "none"; //hide preview
    //document.getElementById("crop-btn").style.display = "none"; //hide crop btn
    document.getElementById("croppedImgFile").style.display = "none"; //hide input for post form
    //document.getElementById("newVideo").style.display = "none"; //hide new video if user hasn't input anything yet
    //document.getElementById("imgStuff").style.display = "none"; //hide all image back
    //document.getElementById("vidStuff").style.display = "none"; //hide all video back

    if(contact_method === "True") {
        document.getElementById("phoneNum").style.display = "none"; //hide input for phone number div
    }

    document.getElementById("deleteProfileBtn").onclick = function() {
        var divToAppendTo = document.getElementById("inDeleteForm");
        divToAppendTo.appendChild(document.createTextNode("Please enter your first name to confirm.  "));
        var profileName = document.createElement("input");
        profileName.setAttribute("name", "first_name");
        divToAppendTo.appendChild(profileName);
        divToAppendTo.appendChild(document.createTextNode(" ")); //spacing
        
        var newBtn = document.createElement("button");
        newBtn.setAttribute("name", "second_delete_profile_btn");
        newBtn.setAttribute("class", "deleteAccountBtn");
        newBtn.setAttribute("textContent", "Delete");
        newBtn.innerHTML = "Delete"; //since textContent doesn't seem to be working
        divToAppendTo.appendChild(newBtn);
    }

    document.getElementById("editProfileForm").onsubmit = function() {
        document.getElementById("submitBtn").value = document.activeElement.id
    }

}


function check_image_size(file, crop) {
    if(((file.size/1024)/1024).toFixed(4) > 5) { // file size < 5 MB
        if(crop) {
            alert("Crop is too big (max size = 5 MB).");
        } else {
            alert("File too big (max file size = 5 MB).");
        }
        document.getElementById('inputFile').value = "";
        return false;
    }
    return true;
}

function set_cropper_listener() {
    image.addEventListener('ready', function () { //image ready --> add event listener
        console.log("ready");
        if(this.cropper === cropper) { //ensure ready
            image.addEventListener('cropend', function () {
                console.log("crop fired");
                cropper.getCroppedCanvas().toBlob(function(blob) {  
                    let file = new File([blob], document.getElementById("inputFile").files[0].name,{type:"image/jpeg", lastModified:new Date().getTime()});  
                    
                    if(check_image_size(file, true)) {
                        // Create a new container
                        let container = new DataTransfer();
                        // Add the cropped image file to the container
                        container.items.add(file);
                        // Replace the original image file with the new cropped image file
                        document.getElementById("croppedImgFile").files = container.files;
                    }
                    
                    /*var readerNew = new FileReader();
                    readerNew.onload = function (e) {  
                        imgCrop = document.getElementById("croppedImage");
                        if(imgCrop) {
                            imgCrop.remove(); //delete the previous img if it exists
                        }
                        croppedImgElem = document.createElement("img");
                        croppedImgElem.setAttribute("id", "croppedImage");
                        croppedImgElem.setAttribute("class", "image_container centerDiv");
                        croppedImgElem.setAttribute("src", e.target.result);
                        croppedImgElem.setAttribute("alt", "your image");
                        document.getElementById("cropPreview").style.display = "block"; //show advice
                        document.getElementById("cropped_image").appendChild(croppedImgElem);
                    }
                    readerNew.readAsDataURL(file);*/
                }, "image/jpeg", 0.7); //function, type, quality
            });
        };
    });
}


//resume stuff
inputFileResume = document.getElementById("inputFileResume");
if(inputFileResume) { //ensure not null
    inputFileResume.addEventListener('change', function() {
        if (inputFileResume.files && inputFileResume.files[0]) {

            if(((inputFileResume.files[0].size/1024)/1024).toFixed(4) > 5) { // file size < 5 MB
                alert("File too big (max file size = 5 MB).");
                document.getElementById('inputFileResume').value = "";
                return;
            }
            //document.getElementById("resumeFilename").textContent = ("File chosen: " + inputFileResume.files[0].name);
        }
            
    }, false);
} else {
    //won't proc because of defer
    console.log("Null");
}

//window ready
window.addEventListener('load', function() {
    formProfileSubmit = document.getElementById("editProfileForm")
    formPwdSubmit = document.getElementById("submitPwdForm")
})

function validate_then_submit() {
    deleteErrorMessages()
    alert("VALIDATING ALL")
    errors = client_validate_everything()
    if(Object.keys(errors).length == 0) { //validate passes --> submit
        formProfileSubmit.submit()
    } else {
        show_validation_errors(errors)
    }
}

function validate_password_then_submit() {
    deleteErrorMessages()
    errors = client_validate_password()
    if(Object.keys(errors).length == 0) { //validate passes --> submit
        formPwdSubmit.submit()
    } else {
        show_validation_errors(errors)
    }
}

function deleteErrorMessages() {
    $('.error').remove();
}

function show_validation_errors(errors, stage) { //errors is a dictionary of errors that happened during server-side validation
    if(errors === null || errors === undefined || Object.keys(errors).length === 0) {
        //let errors = document.getElementById(stage).getElementsByClassName("error");
        //console.log(errors)
        return
    }
    for (const [key, value] of Object.entries(errors)) {
        //console.log(document.getElementById(key).childNodes)
        let input = document.getElementById(key);
        input.style.borderColor = "red"
        setTimeout(() => {
            document.getElementById(key).style = ""
        }, 3000)
        let error_node = document.createElement("span");
        error_node.className = "error"
        error_node.style.color = "red";
        error_node.innerHTML = value;
        input.parentNode.appendChild(error_node)
    }
    alert("Please fix the registration errors on this page!")
}


function client_validate_password() {
    var errors = {}
    success = true

    if(formPwdSubmit.password.value === '') {
        errors["password"] = 'Please enter a password.'
        success = false
    }
    if(formPwdSubmit.password2.value === '') {
        errors["password2"] = 'Please reenter your password.'
        success = false
    }
    if(success) { //everything correct up to this point
        if(formPwdSubmit.password.value != formPwdSubmit.password2.value) { //passwords don't match
            errors["password2"] = 'Passwords do not match.'
        }
    }

    return errors
}

function client_validate_everything() {
    var errors = {}
    success = true

    if(document.getElementById("first_name").value === '') {
        errors["first_name"] = 'Please enter a first name.'
        success = false
    }
    if(document.getElementById("last_name").value === '') {
        errors["last_name"] = 'Please enter a last name.'
        success = false
    }

    if(!($(document.getElementById("emailBtn")).is(':checked') && $(document.getElementById("emailBtn")).val() == 'Email') && document.getElementById("phoneNumber").value === "") { 
        //user chose to be contacted by phone
        errors["phoneNumber"] = 'Your phone number cannot be empty.'
    }


    //location
    if(document.getElementById("city_name").value === '') {
        errors['city_name'] = 'Please enter a city.'
    }

    //bio
    if(document.getElementById("bio").value === "") {
        errors['bio'] = 'Your bio cannot be empty.'
    }

    // Commented out for beta test
    // if(document.getElementById("personality1").value === "" || document.getElementById("personality2").value === "" ||
    //         document.getElementById("personality3").value === "") {
    //     errors['personality'] = "Please enter three words or phrases that describe you."
    // }


    //division
    if(document.getElementById("division").value === '') {
        errors['division'] = 'Please enter your division within the company.'
    }

    // if(document.getElementById("current_occupation").value === "") {
    //     errors['current_occupation'] = 'Please enter your current occupation.'
    // }

    //validate matching attributes
    if(document.getElementById("num_tags").value === "0") {
        errors['num_tags'] = 'Please enter at least one interest.'
    }

    if(document.getElementById("num_career_interests").value === "0") {
        errors['num_career_interests'] = 'Please enter at least one career interest.'
    }

    if(document.getElementById("num_education_listings").value === "0") {
        errors['num_education_listings'] = 'Please enter at least one school.'
    }
    return errors
}


function setPreexistingAttributes(dataInterest, dataCareerInterest, dataEducation) {
    for(var i = 0; i < dataInterest.length; i++) {
        add_tag_jinja(dataInterest[i]);
    }
    for(var i = 0; i < dataCareerInterest.length; i++) {
        add_career_interest_jinja(dataCareerInterest[i]);
    }
    for(var i = 0; i < dataEducation.length; i++) {
        add_education_jinja(dataEducation[i]);
    }
}

function radio_email() {
    document.getElementById("phoneNum").style.display = "none"; //hide input for phone number
}
function radio_phone() {
    document.getElementById("phoneNum").style.display = "block"; //show phone number
}

function add_tag_jinja(tag) {
    arrTds = document.getElementsByName("tagName");
    var add_here = -1;
    for(var i = 0; i < rowArrTag.length; i++) {
        if(rowArrTag[i] < entriesPerRow) { //able to be put in this row
            add_here = i;
            break;
        }
    }
    if(add_here === -1) { //no spaces found
        var newTr = document.createElement('tr');
        add_here = rowArrTag.length;
        newTr.setAttribute("name", "tagTr"+add_here);
        newTr.setAttribute("id", "tagTr"+add_here);
        document.getElementById("tagTable").appendChild(newTr);
        rowArrTag.push(0);
    }
    //create user input text td
    var textCell = document.createElement("td");            //create user input and button remove tds
    textCell.setAttribute("name", "tagTd");
    textCell.setAttribute("class", "removableCell");
    tagName = document.createElement("input");              //create tag input and add to textCell
    tagName.value = tag;
    tagName.setAttribute("name", "tagName");
    tagName.setAttribute("type", "hidden");
    textCell.appendChild(tagName); //for getting the tag name back in routes
    textCell.appendChild(document.createTextNode(tag));

    //create remove button
    var removeBtnCell = document.createElement("td");
    removeBtnCell.setAttribute("name", "tagTdRemove");
    removeBtnCell.setAttribute("class", "removeableBtn");
    var remove = document.createElement("input");
    remove.setAttribute("type", "button");
    remove.setAttribute("name", "removeTagBtn");
    remove.setAttribute("class", "removeableBtn");
    remove.value = "X";
    remove.addEventListener('click', removeTag, false);
    removeBtnCell.appendChild(remove);

    var divContainer = document.createElement("div");       //create div container
    divContainer.setAttribute("name", "divContainer");
    divContainer.setAttribute("class", "divContainer");
    divContainer.appendChild(textCell);        //add user input and remove button to new tray
    divContainer.appendChild(removeBtnCell);     
    
    var newTr = document.createElement("tr");               //create tray to store user input and remove button 
    newTr.appendChild(divContainer);            //add div to new tray

    var newTable = document.createElement("table");         //create new table
    newTable.appendChild(newTr);                //add new tr to table

    var newTd = document.createElement("td");
    newTd.appendChild(newTable);

    tagTray = document.getElementById("tagTr" + add_here); //get first available tray
    tagTray.appendChild(newTd);          //add table to the tag tray
    
    rowArrTag[add_here] = rowArrTag[add_here]+1; //increment value of this row's index
    document.getElementById("num_tags").value = (parseInt(document.getElementById("num_tags").value)+1).toString();
}
function add_education_jinja(education) {
    arrTds = document.getElementsByName("educationName");
    var add_here = -1;
    for(var i = 0; i < rowArrEdu.length; i++) {
        if(rowArrEdu[i] < entriesPerRow) { //able to be put in this row
            add_here = i;
            break;
        }
    }
    if(add_here == -1) { //no spaces found
        var newTr = document.createElement('tr');
        add_here = rowArrEdu.length;
        newTr.setAttribute("name", "educationTr"+add_here);
        newTr.setAttribute("id", "educationTr"+add_here);
        document.getElementById("educationTable").appendChild(newTr);
        rowArrEdu.push(0);
    }
    //create user input text td
    var textCell = document.createElement("td");            //create user input and button remove tds
    textCell.setAttribute("name", "educationTd");
    textCell.setAttribute("class", "removableCell");
    educationName = document.createElement("input");              //create education input and add to textCell
    educationName.value = education;
    educationName.setAttribute("name", "educationName");
    educationName.setAttribute("type", "hidden");
    textCell.appendChild(educationName); //for getting the education name back in routes
    textCell.appendChild(document.createTextNode(education));

    //create remove button
    var removeBtnCell = document.createElement("td");
    removeBtnCell.setAttribute("name", "educationTdRemove");
    removeBtnCell.setAttribute("class", "removeableBtn");
    var remove = document.createElement("input");
    remove.setAttribute("type", "button");
    remove.setAttribute("name", "removeEducationBtn");
    remove.setAttribute("class", "removeableBtn");
    remove.value = "X";
    remove.addEventListener('click', removeEducation, false);
    removeBtnCell.appendChild(remove);

    var divContainer = document.createElement("div");       //create div container
    divContainer.setAttribute("name", "divContainer");
    divContainer.setAttribute("class", "divContainer");
    divContainer.appendChild(textCell);        //add user input and remove button to new tray
    divContainer.appendChild(removeBtnCell);     
    
    var newTr = document.createElement("tr");               //create tray to store user input and remove button 
    newTr.appendChild(divContainer);            //add div to new tray

    var newTable = document.createElement("table");         //create new table
    newTable.appendChild(newTr);                //add new tr to table

    var newTd = document.createElement("td");
    newTd.appendChild(newTable);

    educationTray = document.getElementById("educationTr" + add_here); //get first available tray
    educationTray.appendChild(newTd);          //add table to the education tray
    
    rowArrEdu[add_here] = rowArrEdu[add_here]+1; //increment value of this row's index
    document.getElementById("num_education_listings").value = (parseInt(document.getElementById("num_education_listings").value)+1).toString();
}
function add_career_interest_jinja(careerInterest) {
    arrTds = document.getElementsByName("careerInterestName");
    var add_here = -1;
    for(var i = 0; i < rowArrCint.length; i++) {
        if(rowArrCint[i] < entriesPerRow) { //able to be put in this row
            add_here = i;
            break;
        }
    }
    if(add_here == -1) { //no spaces found
        var newTr = document.createElement('tr');
        add_here = rowArrCint.length;
        newTr.setAttribute("name", "careerInterestTr"+add_here);
        newTr.setAttribute("id", "careerInterestTr"+add_here);
        document.getElementById("careerInterestTable").appendChild(newTr);
        rowArrCint.push(0);
    }   

    //create user input text td
    var textCell = document.createElement("td");            //create user input and button remove tds
    textCell.setAttribute("name", "careerInterestTd");
    textCell.setAttribute("class", "removableCell");
    careerInterestName = document.createElement("input");              //create careerInterest input and add to textCell
    careerInterestName.value = careerInterest;
    careerInterestName.setAttribute("name", "careerInterestName");
    careerInterestName.setAttribute("type", "hidden");
    textCell.appendChild(careerInterestName); //for getting the careerInterest name back in routes
    textCell.appendChild(document.createTextNode(careerInterest));

    //create remove button
    var removeBtnCell = document.createElement("td");
    removeBtnCell.setAttribute("name", "careerInterestTdRemove");
    removeBtnCell.setAttribute("class", "removeableBtn");
    var remove = document.createElement("input");
    remove.setAttribute("type", "button");
    remove.setAttribute("name", "removeCareerInterestBtn");
    remove.setAttribute("class", "removeableBtn");
    remove.value = "X";
    remove.addEventListener('click', removeCareerInterest, false);
    removeBtnCell.appendChild(remove);

    var divContainer = document.createElement("div");       //create div container
    divContainer.setAttribute("name", "divContainer");
    divContainer.setAttribute("class", "divContainer");
    divContainer.appendChild(textCell);        //add user input and remove button to new tray
    divContainer.appendChild(removeBtnCell);     
    
    var newTr = document.createElement("tr");               //create tray to store user input and remove button 
    newTr.appendChild(divContainer);            //add div to new tray

    var newTable = document.createElement("table");         //create new table
    newTable.appendChild(newTr);                //add new tr to table

    var newTd = document.createElement("td");
    newTd.appendChild(newTable);

    careerInterestTray = document.getElementById("careerInterestTr" + add_here); //get first available tray
    careerInterestTray.appendChild(newTd);          //add table to the careerInterest tray

    rowArrCint[add_here] = rowArrCint[add_here]+1; //increment value of this row's index
    document.getElementById("careerInterestField").value = ""; //empty input careerInterest field
    document.getElementById("num_career_interests").value = (parseInt(document.getElementById("num_career_interests").value)+1).toString();
}

document.getElementById('bio').onkeyup = function () {
    document.getElementById('char_count').innerHTML = "Characters left: " + (500 - this.value.length);
};


function add_tag() {
    set_attributes_changed()
    arrTds = document.getElementsByName("tagName");
    var tag = document.getElementById("tagField").value;
    if(!checkOnEnter(tag, arrTds)) {
        document.getElementById("tagField").value = ""; //empty input tag field
        return;
    }
    var add_here = -1;
    for(var i = 0; i < rowArrTag.length; i++) {
        if(rowArrTag[i] < entriesPerRow) { //able to be put in this row
            add_here = i;
            break;
        }
    }
    if(add_here === -1) { //no spaces found
        if(rowArrTag.length == maxRows) { //no available spaces and max # rows
            alert("Max number of attributes reached");
            return;
        }
        var newTr = document.createElement('tr');
        add_here = rowArrTag.length;
        newTr.setAttribute("name", "tagTr"+add_here);
        newTr.setAttribute("id", "tagTr"+add_here);
        document.getElementById("tagTable").appendChild(newTr);
        rowArrTag.push(0);
    }

    //create user input text td
    var textCell = document.createElement("td");            //create user input and button remove tds
    textCell.setAttribute("name", "tagTd");
    textCell.setAttribute("class", "removableCell");
    tagName = document.createElement("input");              //create tag input and add to textCell
    tagName.value = tag;
    tagName.setAttribute("name", "tagName");
    tagName.setAttribute("type", "hidden");
    textCell.appendChild(tagName); //for getting the tag name back in routes
    textCell.appendChild(document.createTextNode(tag));

    //create remove button
    var removeBtnCell = document.createElement("td");
    removeBtnCell.setAttribute("name", "tagTdRemove");
    removeBtnCell.setAttribute("class", "removeableBtn");
    var remove = document.createElement("input");
    remove.setAttribute("type", "button");
    remove.setAttribute("name", "removeTagBtn");
    remove.setAttribute("class", "removeableBtn");
    remove.value = "X";
    remove.addEventListener('click', removeTag, false);
    removeBtnCell.appendChild(remove);

    var divContainer = document.createElement("div");       //create div container
    divContainer.setAttribute("name", "divContainer");
    divContainer.setAttribute("class", "divContainer");
    divContainer.appendChild(textCell);        //add user input and remove button to new tray
    divContainer.appendChild(removeBtnCell);     
    
    var newTr = document.createElement("tr");               //create tray to store user input and remove button 
    newTr.appendChild(divContainer);            //add div to new tray

    var newTable = document.createElement("table");         //create new table
    newTable.appendChild(newTr);                //add new tr to table

    var newTd = document.createElement("td");
    newTd.appendChild(newTable);

    tagTray = document.getElementById("tagTr" + add_here); //get first available tray
    tagTray.appendChild(newTd);          //add table to the tag tray
    
    rowArrTag[add_here] = rowArrTag[add_here]+1; //increment value of this row's index
    document.getElementById("tagField").value = ""; //empty input tag field
    document.getElementById("num_tags").value = (parseInt(document.getElementById("num_tags").value)+1).toString();
}

function removeTag() {
    set_attributes_changed()
    cellRemove = this.parentNode.parentNode.parentNode.parentNode.parentNode;
    tags = cellRemove.parentNode; //the education tray = this.parent x 5
    tags.removeChild(cellRemove);
    document.getElementById("num_tags").value = (parseInt(document.getElementById("num_tags").value)-1).toString()
    rowArrTag[tags.rowIndex] = rowArrTag[tags.rowIndex]-1; //decrement the row index
}

function add_education() {
    set_attributes_changed()
    arrTds = document.getElementsByName("educationName");
    var education = document.getElementById("educationField").value;
    if(!checkOnEnter(education, arrTds)) {
        document.getElementById("educationField").value = ""; //empty input tag field
        return;
    }
    var add_here = -1;
    for(var i = 0; i < rowArrEdu.length; i++) {
        if(rowArrEdu[i] < entriesPerRow) { //able to be put in this row
            add_here = i;
            break;
        }
    }
    if(add_here == -1) { //no spaces found
        if(rowArrEdu.length == maxRows) { //no available spaces and max # rows
            alert("Max number of attributes reached");
            return;
        }
        var newTr = document.createElement('tr');
        add_here = rowArrEdu.length;
        newTr.setAttribute("name", "educationTr"+add_here);
        newTr.setAttribute("id", "educationTr"+add_here);
        document.getElementById("educationTable").appendChild(newTr);
        rowArrEdu.push(0);
    }

    //create user input text td
    var textCell = document.createElement("td");            //create user input and button remove tds
    textCell.setAttribute("name", "educationTd");
    textCell.setAttribute("class", "removableCell");
    educationName = document.createElement("input");              //create education input and add to textCell
    educationName.value = education;
    educationName.setAttribute("name", "educationName");
    educationName.setAttribute("type", "hidden");
    textCell.appendChild(educationName); //for getting the education name back in routes
    textCell.appendChild(document.createTextNode(education));

    //create remove button
    var removeBtnCell = document.createElement("td");
    removeBtnCell.setAttribute("name", "educationTdRemove");
    removeBtnCell.setAttribute("class", "removeableBtn");
    var remove = document.createElement("input");
    remove.setAttribute("type", "button");
    remove.setAttribute("name", "removeEducationBtn");
    remove.setAttribute("class", "removeableBtn");
    remove.value = "X";
    remove.addEventListener('click', removeEducation, false);
    removeBtnCell.appendChild(remove);

    var divContainer = document.createElement("div");       //create div container
    divContainer.setAttribute("name", "divContainer");
    divContainer.setAttribute("class", "divContainer");
    divContainer.appendChild(textCell);        //add user input and remove button to new tray
    divContainer.appendChild(removeBtnCell);     
    
    var newTr = document.createElement("tr");               //create tray to store user input and remove button 
    newTr.appendChild(divContainer);            //add div to new tray

    var newTable = document.createElement("table");         //create new table
    newTable.appendChild(newTr);                //add new tr to table

    var newTd = document.createElement("td");
    newTd.appendChild(newTable);

    educationTray = document.getElementById("educationTr" + add_here); //get first available tray
    educationTray.appendChild(newTd);          //add table to the education tray
    
    rowArrEdu[add_here] = rowArrEdu[add_here]+1; //increment value of this row's index
    document.getElementById("educationField").value = ""; //empty input education field
    document.getElementById("num_education_listings").value = (parseInt(document.getElementById("num_education_listings").value)+1).toString();
}

function removeEducation() {
    set_attributes_changed()
    cellRemove = this.parentNode.parentNode.parentNode.parentNode.parentNode;
    educationTr = cellRemove.parentNode; //the education tray = this.parent.parent
    educationTr.removeChild(cellRemove);
    document.getElementById("num_education_listings").value = (parseInt(document.getElementById("num_education_listings").value)-1).toString()
    rowArrEdu[educationTr.rowIndex] = rowArrEdu[educationTr.rowIndex]-1; //decrement the row index
}

function add_career_interest() {
    set_attributes_changed()
    arrTds = document.getElementsByName("careerInterestName");
    var careerInterest = document.getElementById("careerInterestField").value;
    if(!checkOnEnter(careerInterest, arrTds)) {
        document.getElementById("careerInterestField").value = ""; //empty input tag field
        return;
    }
    var add_here = -1;
    for(var i = 0; i < rowArrCint.length; i++) {
        if(rowArrCint[i] < entriesPerRow) { //able to be put in this row
            add_here = i;
            break;
        }
    }
    if(add_here == -1) { //no spaces found
        if(rowArrCint.length == maxRows) { //no available spaces and max # rows
            alert("Max number of attributes reached");
            return;
        }
        var newTr = document.createElement('tr');
        add_here = rowArrCint.length;
        newTr.setAttribute("name", "careerInterestTr"+add_here);
        newTr.setAttribute("id", "careerInterestTr"+add_here);
        document.getElementById("careerInterestTable").appendChild(newTr);
        rowArrCint.push(0);
    }   

    //create user input text td
    var textCell = document.createElement("td");            //create user input and button remove tds
    textCell.setAttribute("name", "careerInterestTd");
    textCell.setAttribute("class", "removableCell");
    careerInterestName = document.createElement("input");              //create careerInterest input and add to textCell
    careerInterestName.value = careerInterest;
    careerInterestName.setAttribute("name", "careerInterestName");
    careerInterestName.setAttribute("type", "hidden");
    textCell.appendChild(careerInterestName); //for getting the careerInterest name back in routes
    textCell.appendChild(document.createTextNode(careerInterest));

    //create remove button
    var removeBtnCell = document.createElement("td");
    removeBtnCell.setAttribute("name", "careerInterestTdRemove");
    removeBtnCell.setAttribute("class", "removeableBtn");
    var remove = document.createElement("input");
    remove.setAttribute("type", "button");
    remove.setAttribute("name", "removeCareerInterestBtn");
    remove.setAttribute("class", "removeableBtn");
    remove.value = "X";
    remove.addEventListener('click', removeCareerInterest, false);
    removeBtnCell.appendChild(remove);

    var divContainer = document.createElement("div");       //create div container
    divContainer.setAttribute("name", "divContainer");
    divContainer.setAttribute("class", "divContainer");
    divContainer.appendChild(textCell);        //add user input and remove button to new tray
    divContainer.appendChild(removeBtnCell);     
    
    var newTr = document.createElement("tr");               //create tray to store user input and remove button 
    newTr.appendChild(divContainer);            //add div to new tray

    var newTable = document.createElement("table");         //create new table
    newTable.appendChild(newTr);                //add new tr to table

    var newTd = document.createElement("td");
    newTd.appendChild(newTable);

    careerInterestTray = document.getElementById("careerInterestTr" + add_here); //get first available tray
    careerInterestTray.appendChild(newTd);          //add table to the careerInterest tray

    rowArrCint[add_here] = rowArrCint[add_here]+1; //increment value of this row's index
    document.getElementById("careerInterestField").value = ""; //empty input careerInterest field
    document.getElementById("num_career_interests").value = (parseInt(document.getElementById("num_career_interests").value)+1).toString();
}

function removeCareerInterest() {
    set_attributes_changed()
    cellRemove = this.parentNode.parentNode.parentNode.parentNode.parentNode;
    careerInterestTr = cellRemove.parentNode;
    careerInterestTr.removeChild(cellRemove);
    document.getElementById("num_career_interests").value = (parseInt(document.getElementById("num_career_interests").value)-1).toString()
    rowArrCint[careerInterestTr.rowIndex] = rowArrCint[careerInterestTr.rowIndex]-1; //decrement the row index
}

function checkOnEnter(word, arr) {
    if(word === "") {
        alert("Error: empty input.");
        return false;
    }
    for(var i = 0; i < arr.length; i++) {
        if(arr[i].value === word) {
            alert("Error: duplicate entry: " + word);
            return false;
        }
    }
    return true;
}

function set_attributes_changed() {
    document.getElementById("changedAttributes").value = "True"
}