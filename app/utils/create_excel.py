from decimal import DivisionByZero
from xlwt import Workbook
from io import BytesIO
from app import db
from app.input_sets.models import Business, Select, User, \
        ProgressMeeting, Tag, CareerInterest, School, ProgressMeetingCompletionInformation
from datetime import datetime 

EMAIL = 0
NAME = 1
ROLE = 2
# DIVISION = 8
# DIVISION_PREFERENCE = 9
BIO = 3
# CITY = 11
# CURRENT_OCCUPATION = 12
MENTOR_GENDER_PREFERENCE = 4
GENDER_IDENTITY = 5
PERSONALITY_TRAITS = 6
PERSONAL_INTERESTS = 7
CAREER_INTERESTS_EXPERIENCE = 8
EDUCATION = 9
NUM_MATCHES = 10

MENTEE_EMAIL = 0
MENTEE_NAME = 1
MENTOR_EMAIL = 2
MENTOR_NAME = 3
LAST_MEETING_TITLE = 4
LAST_MEETING_NUMBER = 5
# PROGRESS_MEETING_NOTES = 6



def create_excel_sheet(id):
    business = Business.query.filter_by(id=id).first()
    if business is not None:
        filename = print_to_sheet(business)
        return filename
    else:
        print("Business with that id does not exist.")
        return None



"""
Writes to excel sheet
user --> information1, information2, etc.

"""        
def write_col_guide_users(sheet):
    sheet.write(0, EMAIL, "Email") # Write email into 0th position
    sheet.write(0, NAME, "Name") # Write first name + last name
    sheet.write(0, ROLE, "Role") # Write mentor/mentee
    sheet.write(0, BIO, "Bio")
    sheet.write(0, MENTOR_GENDER_PREFERENCE, "Mentor gender preference")
    sheet.write(0, GENDER_IDENTITY, "Gender identity")
    sheet.write(0, PERSONALITY_TRAITS, "Personality traits")
    sheet.write(0, PERSONAL_INTERESTS, "Personal interests")
    sheet.write(0, CAREER_INTERESTS_EXPERIENCE, "Career interests/experience")
    sheet.write(0, EDUCATION, "Education")
    sheet.write(0, NUM_MATCHES, "Willing to have X mentors/mentees")


"""
Writes to excel sheet
mentee --> mentor (multiple cols for same mentee)

"""        
def write_col_guide_pairings(sheet):
    sheet.write(0, MENTEE_EMAIL, "Mentee email") # Write email into 0th position
    sheet.write(0, MENTEE_NAME, "Mentee name") # Write first name + last name
    sheet.write(0, MENTOR_EMAIL, "Mentor email") # Write mentor/mentee email
    sheet.write(0, MENTOR_NAME, "Mentor name") # Write mentor/mentee first name + last name
    sheet.write(0, LAST_MEETING_TITLE, "Last meeting title") # Write most recent meeting title
    sheet.write(0, LAST_MEETING_NUMBER, "Last meeting number") # Write most recent meeting number


def print_to_sheet(business):

    # Create workbook
    wb = Workbook()

    # Create sheet
    userSheet = wb.add_sheet('Users')
    write_col_guide_users(userSheet)

    users = User.query.filter_by(business_id=business.id).all()

    write_to_user_sheet(userSheet, business, users)

    pairingSheet = wb.add_sheet('Pairings')
    write_col_guide_pairings(pairingSheet)

    write_to_pairings_sheet(pairingSheet, business, users)

    filename = "excel_spreadsheets/" + business.name.replace(" ", "_") + \
        "_spreadsheet_(" + datetime.today().strftime('%Y-%m-%d') + ").xls"
    #format datetime into month/day/year
    wb.save(filename) 

    return filename



def write_to_user_sheet(userSheet, business, users):
    cnt = 1
    for u in users:
        userSheet.write(cnt, EMAIL, u.email) # Write email into 0th position
        userSheet.write(cnt, NAME, u.first_name + " " + u.last_name) # Write first name + last name into 1st position
        userSheet.write(cnt, ROLE, "Mentee" if u.is_student else "Mentor")
        userSheet.write(cnt, BIO, u.bio) # Write bio
       
        mentorGenderPreference = u.mentor_gender_preference
        if mentorGenderPreference != None:
            if mentorGenderPreference == "male":
                userSheet.write(cnt, MENTOR_GENDER_PREFERENCE, "Male mentor") # Write user mentor gender preference
            elif mentorGenderPreference == "female":
                userSheet.write(cnt, MENTOR_GENDER_PREFERENCE, "Female mentor")
            else:
                userSheet.write(cnt, MENTOR_GENDER_PREFERENCE, "No preference")
        else:
            userSheet.write(cnt, MENTOR_GENDER_PREFERENCE, "N/A")

        genderIdentity = u.gender_identity
        if genderIdentity != None:
            if genderIdentity == "male":
                userSheet.write(cnt, GENDER_IDENTITY, "Male")
            elif genderIdentity == "female":
                userSheet.write(cnt, GENDER_IDENTITY, "Female") # Write user gender identity
            elif genderIdentity == "nonbinaryNonconforming":
                userSheet.write(cnt, GENDER_IDENTITY, "Non-binary/non-conforming")
            else:
                userSheet.write(cnt, GENDER_IDENTITY, "Prefer not to respond")
        
        personalities = ""
        if u.personality_1:
            personalities += u.personality_1 + "; "
        if u.personality_2:
            personalities += u.personality_2 + "; "
        if u.personality_3:
            personalities += u.personality_3
        userSheet.write(cnt, PERSONALITY_TRAITS, personalities)

        interestList = ""
        for interest in u.rtn_interests():
            interestList += (interest.entered_name + "; ")
        if len(interestList) > 2:
            interestList = interestList[:-2] #cut the semicolon
        userSheet.write(cnt, PERSONAL_INTERESTS, interestList)

        
        careerInterestList = ""
        for cint in u.rtn_career_interests():
            careerInterestList += (cint.entered_name + "; ")
        if len(careerInterestList) > 2:
            careerInterestList = careerInterestList[:-2] #cut the semicolon
        userSheet.write(cnt, CAREER_INTERESTS_EXPERIENCE, careerInterestList)


        educationList = ""
        for school in u.rtn_education():
            educationList += (school.entered_name + "; ")
        if len(educationList) > 2:
            educationList = educationList[:-2] #cut the semicolon
        userSheet.write(cnt, EDUCATION, educationList)

        if u.num_pairings_can_make:
            userSheet.write(cnt, NUM_MATCHES, u.num_pairings_can_make)
        else:
            userSheet.write(cnt, NUM_MATCHES, 1)

        cnt+=1



def write_to_pairings_sheet(pairingsSheet, business, users):
    user_dict = {user.id : user for user in users}
    mentee_ids = [user.id for user in users if user.is_student]

    selects = db.session.query(
        Select
    ).filter(
        Select.mentee_id.in_(mentee_ids)
    ).group_by(
        Select.mentee_id
    ).all()

    cnt = 1
    for s in selects:
        mentee = user_dict[s.mentee_id]
        mentor = user_dict[s.mentor_id]
        pairingsSheet.write(cnt, MENTEE_EMAIL, mentee.email) # Write email into 0th position
        pairingsSheet.write(cnt, MENTEE_NAME, mentee.first_name + " " + mentee.last_name) # Write first name + last name into 1st position

        pairingsSheet.write(cnt, MENTOR_EMAIL, mentor.email)
        pairingsSheet.write(cnt, MENTOR_NAME, mentor.first_name + " " + mentor.last_name)

        #write the mentor/mentee matches and # of meetings completed
        write_meeting_info(pairingsSheet, business.id, s, cnt)

        cnt+=1


def write_meeting_info(pairingsSheet, business_id, select, cnt):
    curr_meeting_id = select.current_meeting_number_mentor
    if select.current_meeting_number_mentee > curr_meeting_id: 
        curr_meeting_id = select.current_meeting_number_mentee
        #highest completed meeting between the mentee and mentor

    curr_meeting_id = curr_meeting_id - 1 #subtract 1 after finding the max to find the last completed meeting

    currProgressMeeting = ProgressMeeting.query.filter(ProgressMeeting.business_ID==business_id) \
            .filter(ProgressMeeting.num_meeting==curr_meeting_id).first()
    if currProgressMeeting != None:
        pairingsSheet.write(cnt, LAST_MEETING_TITLE, currProgressMeeting.title) #meeting title
        pairingsSheet.write(cnt, LAST_MEETING_NUMBER, currProgressMeeting.num_meeting) #meeting number
    else:
        pairingsSheet.write(cnt, LAST_MEETING_TITLE, "No meetings completed") #meeting title
        pairingsSheet.write(cnt, LAST_MEETING_NUMBER, "0") #meeting number



#call starter function
#get_business_name()

"""
if __name__ == '__main__':
    get_business_name()
"""