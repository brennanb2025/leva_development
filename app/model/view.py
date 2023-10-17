from app import app
from app.input_sets.models import User, Tag, InterestTag, EducationTag, School, CareerInterest, \
        CareerInterestTag, Select, Business, Event, ProgressMeeting, ProgressMeetingCompletionInformation

import app.model.AWS as AWS

class readyUserProfileResponse:
    def __init__(self):
        self.interestList = None
        self.careerInterestList = None
        self.educationList = None
        self.user = None
        self.resumeUrl = None
        self.divisionPreference = None
        self.mentorGenderPreference = None
        self.genderIdentity = None

def create_user_page(id): 
    resp = readyUserProfileResponse()
    user = User.query.filter_by(id=id).first()
    resp.user = user
    if user == None:
        return resp

    interestList = []
    for interest in user.rtn_interests():
        interestList.append(interest.entered_name)
    resp.interestList = interestList
    
    careerInterestList = []
    for cint in user.rtn_career_interests():
        careerInterestList.append(cint.entered_name)
    resp.careerInterestList = careerInterestList

    educationList = []
    for educ in user.rtn_education():
        educationList.append(educ.entered_name)
    resp.educationList = educationList

    resp.resumeUrl = AWS.create_resume_link(user)

    mentorGenderPreference = user.mentor_gender_preference
    if mentorGenderPreference != None:
        if mentorGenderPreference == "male":
            mentorGenderPreference = "Male mentor"
        elif mentorGenderPreference == "female":
            mentorGenderPreference = "Female mentor"
        else:
            mentorGenderPreference = "No preference"
    resp.mentorGenderPreference = mentorGenderPreference

    divisionPreference = user.division_preference
    if divisionPreference != None:
        if divisionPreference == "same":
            divisionPreference = "Same division"
        elif divisionPreference == "different":
            divisionPreference = "Different division"
        else:
            divisionPreference = "No preference"
    resp.divisionPreference = divisionPreference

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