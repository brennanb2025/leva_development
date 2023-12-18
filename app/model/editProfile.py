
from app.input_sets.models import User, Tag, InterestTag, EducationTag, School, CareerInterest, \
        CareerInterestTag, Select, Business, Event, ProgressMeeting, ProgressMeetingCompletionInformation

from app import app, db

import app.model.AWS as AWS
import app.model.userUtilities as utilities

import os, json

class readyUserProfileResponse:
    def __init__(self):
        self.interestList = None
        self.careerInterestList = None
        self.educationList = None
        self.user = None
        self.divisionPreference = None
        self.mentorGenderPreference = None
        self.genderIdentity = None

def readyUserProfile(userId):
    resp = readyUserProfileResponse()

    user = User.query.filter_by(id=userId).first() #get the correct profile by inputting user id
    interestList = []
    for interest in user.rtn_interests():
        #interestList.append(Tag.query.filter_by(tagID=interest.interestID).first().title)
        interest = Tag.query.filter_by(id=interest.interestID).first()
        if interest != None:
            interestList.append(interest.title)
    resp.interestList = interestList

    careerInterestList = []
    for cint in user.rtn_career_interests():
        #careerInterestList.append(CareerInterest.query.filter_by(careerInterestID=cint.careerInterestID).first().title)
        cint = CareerInterest.query.filter_by(id=cint.careerInterestID).first()
        if cint != None:
            careerInterestList.append(cint.title)
    resp.careerInterestList = careerInterestList

    educationList = []
    for school in user.rtn_education():
        #educationList.append(School.query.filter_by(schoolID=school.educationID).first().title)
        edu = School.query.filter_by(id=school.educationID).first()
        if edu != None:
            educationList.append(edu.title)
    resp.educationList = careerInterestList

    mentorGenderPreference = user.mentor_gender_preference
    if mentorGenderPreference != None:
        if mentorGenderPreference == "male":
            mentorGenderPreference = "Male mentor"
        elif mentorGenderPreference == "female":
            mentorGenderPreference = "Female mentor"
        else:
            mentorGenderPreference = "No preference"
    
    resp.mentorGenderPreference = mentorGenderPreference
    
    """
    divisionPreference = user.division_preference
    if divisionPreference != None:
        if divisionPreference == "same":
            divisionPreference = "Same division"
        elif divisionPreference == "different":
            divisionPreference = "Different division"
        else:
            divisionPreference = "No preference"

    resp.divisionPreference = divisionPreference
    """

    genderIdentity = user.gender_identity
    if genderIdentity != None:
        if genderIdentity == "male":
            genderIdentity = "Male"
        elif genderIdentity == "female":
            genderIdentity = "Female"
        elif genderIdentity == "nonbinaryNonconforming":
            genderIdentity = "Non-binary/non-conforming"
        else:
            genderIdentity = "Prefer not to respond"

    resp.genderIdentity = genderIdentity

    return resp



class editResumeResponse:
    def __init__(self):
        self.success = False
        self.resumeNotInput = False
        self.unreadable = False
        self.tooBig = False
        self.noFilename = False
        self.fileTypeUnreadable = False
        self.fileTypeNotAllowed = False
        self.fileTypeError = ""

    
def editProfileResume(user, resume):
    
    success = True
    resp = editResumeResponse()

    resumeSize = -1
    if resume:
        resume.seek(0, os.SEEK_END)
        resumeSize = resume.tell()
        resume.seek(0)
    else:
        success = False
        editResumeResponse.resumeNotInput = True
    
    if resumeSize == -1:
        editResumeResponse.unreadable = True
        success = False

    elif (resumeSize/1024)/1024 > 5:
        editResumeResponse.tooBig = True
        success = False
    elif resume.filename == '':
        editResumeResponse.noFilename = True
        success = False
    else:
        file_ext = os.path.splitext(resume.filename)[1]
        if file_ext == None:
            success = False
            editResumeResponse.fileTypeUnreadable = True
        elif file_ext not in json.loads(app.config['UPLOAD_EXTENSIONS_RESUME']):
            editResumeResponse.fileTypeNotAllowed = True
            editResumeResponse.fileTypeError = 'Accepted file type: .pdf. You uploaded a', file_ext + "."
            success = False

    if success: 
        resume.seek(0) #I read the file before to check the length so I must put the cursor at the beginning in order to upload it.
        AWS.delete_resume(user)
        output, filename = AWS.upload_resume_file_to_s3(resume, user)
        user.set_resume(output, filename) #set the user profile picture link
        db.session.commit()

    resp.success = success

    return resp


def deleteProfile(user):
    AWS.delete_profile_picture(user)
    AWS.delete_intro_video(user)
    delete_user_attributes(user.id)
    AWS.delete_resume(user)

    selectEntry = None
    if user.is_student: #is mentee
        selectEntry = Select.query.filter_by(mentee_id=user.id).first()

        if selectEntry is not None:
            ProgressMeetingCompletionInformation.query.filter(
                #ProgressMeetingCompletionInformation.num_progress_meeting == selectEntry.current_meeting_number_mentee,
                ProgressMeetingCompletionInformation.select_id == selectEntry.id
            ).delete()

            Select.query.filter_by(mentee_id=user.id).delete()
    else:
        selectEntry = Select.query.filter_by(mentor_id=user.id).first()

        if selectEntry is not None:
            ProgressMeetingCompletionInformation.query.filter(
                #ProgressMeetingCompletionInformation.num_progress_meeting == selectEntry.current_meeting_number_mentor,
                ProgressMeetingCompletionInformation.select_id == selectEntry.id
            ).delete()

            Select.query.filter_by(mentor_id=user.id).delete()

    Business.query.filter_by(id=user.business_id).first().dec_number_employees_currently_registered() 
    #decrease business number registered by 1 because this user has been deleted
    

    User.query.filter_by(id=user.id).delete()
    db.session.commit()



def delete_user_attributes(userID):
    #when deleting, decrement each of the tags' usage number
    for i in InterestTag.query.filter_by(user_id=userID).all():
        i.delete_inc()
    db.session.commit()
    for i in EducationTag.query.filter_by(user_id=userID).all():
        i.delete_inc()
    db.session.commit()
    for i in CareerInterestTag.query.filter_by(user_id=userID).all():
        i.delete_inc()
    db.session.commit()

    #now just delete the user's tags
    InterestTag.query.filter_by(user_id=userID).delete()
    EducationTag.query.filter_by(user_id=userID).delete()
    CareerInterestTag.query.filter_by(user_id=userID).delete()

    db.session.commit()


def checkFirstName(first_name):
    return first_name != ''

def checkLastName(last_name):
    return last_name != ''

def checkCityName(city_name):
    return city_name == ''

def checkCurrentOccupationName(current_occupation):
    return current_occupation != ''

def checkMentorGenderPreference(radio_gender_preference):
    return not (radio_gender_preference == None or radio_gender_preference == '') #preference empty

def checkGenderIdentity(radio_gender_identity):
    return not (radio_gender_identity == None or radio_gender_identity == '') #empty

def checkBio(bio):
    return bio != '' #bio empty


class checkAttributesResponse:
    def __init__(self):
        self.success = False
        self.interestError = False
        self.educationError = False
        self.careerInterestError = False
        self.careerInterestErrorMessage = ""

def checkAttributes(num_tags, num_education_listings, num_career_interests, isMentee):
    resp = checkAttributesResponse()
    success = True

    if int(num_tags) == 0:
        resp.interestError = True
        success = False

    if int(num_education_listings) == 0:
        resp.educationError = True
        success = False

    if int(num_career_interests) == 0:
        if isMentee:
            resp.careerInterestErrorMessage = 'Please enter at least one career interest.'
        else:
            resp.careerInterestErrorMessage = 'Please enter at least one career experience.'
        resp.careerInterestError = True
        success = False
    resp.success = success
    return resp


def changeAttributes(interestArr, eduArr, cintArr, user):
    #I want to register the new attributes - delete the old ones.
    delete_user_attributes(user.id)

    #get interests
    #I don't actually need num_tags since I can iterate thru getlist, 
    # but I can see it being useful/efficient for future features.
    #ok I'm just going to iterate through the list to protect against index out of bounds exceptions

    #for i in range(int(form1.get('num_tags'))):
    for i in range(len(interestArr)):
        name = interestArr[i].strip()
        if name != "":
            interestTag = InterestTag(
                user_id=user.id,
                entered_name=name
            )
            db.session.add(interestTag)
            db.session.commit() #I have to do this before I set the resource so the id will be set.
            interestTag.set_interestID(name, db.session)

    #for i in range(int(form1.get('num_education_listings'))):
    for i in range(len(eduArr)):
        name = eduArr[i].strip()
        if name != "":
            educationTag = EducationTag(
                user_id=user.id,
                entered_name=name
            )
            db.session.add(educationTag)
            db.session.commit() #I have to do this before I set the resource so the id will be set.
            educationTag.set_educationID(name, db.session)

    #for i in range(int(form1.get('num_career_interests'))):
    for i in range(len(cintArr)):
        name = cintArr[i].strip()
        if name != "":
            cintTag = CareerInterestTag(
                user_id=user.id,
                entered_name=name
            )
            db.session.add(cintTag)
            db.session.commit() #I have to do this before I set the resource so the id will be set.
            cintTag.set_careerInterestID(name, db.session)

    db.session.commit()

def checkPersonality(personality1, personality2, personality3):
    if personality1 != None and personality2 != None and personality3 != None:
        if personality1.strip() == "" or personality2.strip() == "" or personality3.strip() == "":
            return False
    else:
        return False
    return True

def checkDivision(division):
    return division.strip() != ""

def checkDivisionPreference(divisionPreference):
    return not (divisionPreference == None and divisionPreference != "")
        #mentee and mentor division preference empty or mentor and mentee division preference empty

def checkContactPreference(radio_contact, phoneNumber):
    if radio_contact == 'Phone number' and phoneNumber == "": #user chose to be contacted by phone
        return False
    if radio_contact != 'Email' and radio_contact != 'Phone number': #somehow removed the check
        return False
    return True



class editProfilePasswordResponse:
    def __init__(self):
        self.success = False
        self.passwordError = False
        self.password2Error = False
        self.password2ErrorMessage = ""


def editProfilePassword(password, password2, id):
    resp = editProfilePasswordResponse()
    success = True

    if password == '':
        success = False
        resp.passwordError = True
    if password2 == '':
        success = False
        resp.password2Error = True
        resp.password2ErrorMessage = 'Please reenter your password.'
    if success: #did enter everything
        if password != password2: #passwords don't match
            success = False
            resp.password2Error = True
            resp.password2ErrorMessage = 'Passwords do not match.'

    if success:
        User.query.filter_by(id=id).first().set_password(password) #set hashed pwd
        db.session.commit()
    
    resp.success = success
    return resp


class editProfilePictureResponse:
    def __init__(self):
        self.success = False
        self.errorMsg = ""
        self.fileNotFound = False
        self.imageUnreadable = False
        self.imageSizeUnreadable = False
        self.badFileType = False
        self.badFileTypeMessage = ""

def editProfilePicture(img,id):
    success = True
    errorMsg = ""
    resp = editProfilePictureResponse()

    if img == None:
        resp.fileNotFound = True
        resp.success=False
        resp.errorMsg = "[Please select a file]"
        return resp

    #remove cropping
    """if int((img.getbuffer().nbytes/1024)/1024) > 5:
        flash(u'Image is too big (max 5 MB).', 'imageError')
        success = False"""


    #imgSize = -1
    #img.seek(0, os.SEEK_END)
    #imgSize = img.tell()
    #img.seek(0)
    
    """if imgSize == -1:
        errorMsg = errorMsg + "[Couldn't read image]"
        flash(u"Couldn't read image.", 'imageError')
        success = False
    elif (imgSize/1024)/1024 > 5:
        errorMsg = errorMsg + "[Image is too big (max 5 MB)]"
        flash(u'Image is too big (max 5 MB).', 'imageError')
        success = False
    el"""
    if img.filename == '':
        resp.imageUnreadable = True
        errorMsg = errorMsg + "[Could not read image filename]"
        success = False
    else:
        imgType = utilities.validate_image(img.stream)
        if imgType == None:
            resp.imageSizeUnreadable = True
            errorMsg = errorMsg + "[Could not assess image size]"
        elif imgType not in json.loads(app.config['UPLOAD_EXTENSIONS']):
            resp.badFileType = True
            resp.badFileTypeMessage = 'Accepted file types: .png, .jpg. You uploaded a ' + imgType + "."
            errorMsg = errorMsg + "[Wrong image type]"
            success = False
    
    if success: 
        user = User.query.filter_by(id=id).first()
        AWS.delete_profile_picture(user)
        output, filename = AWS.upload_media_file_to_s3(img, user)
        user.set_profile_picture(output, filename) #set the user profile picture link
        db.session.commit()
    
    resp.success = success
    resp.errorMsg = errorMsg
    return resp