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
MATCH_EMAIL = 3
MATCH_NAME = 4
LAST_MEETING_TITLE = 5
LAST_MEETING_NUMBER = 6
PROGRESS_MEETING_NOTES = 7
DIVISION = 8
DIVISION_PREFERENCE = 9
BIO = 10
CITY = 11
CURRENT_OCCUPATION = 12
MENTOR_GENDER_PREFERENCE = 13
GENDER_IDENTITY = 14
PERSONALITY_TRAITS = 15
PERSONAL_INTERESTS = 16
CAREER_INTERESTS_EXPERIENCE = 17
EDUCATION = 18



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
def write_col_guide(sheet):
    sheet.write(0, EMAIL, "Email") # Write email into 0th position
    sheet.write(0, NAME, "Name") # Write first name + last name
    sheet.write(0, ROLE, "Role") # Write mentor/mentee
    sheet.write(0, MATCH_EMAIL, "Match email") # Write mentor/mentee email
    sheet.write(0, MATCH_NAME, "Match name") # Write mentor/mentee first name + last name
    sheet.write(0, LAST_MEETING_TITLE, "Last meeting title") # Write most recent meeting title
    sheet.write(0, LAST_MEETING_NUMBER, "Last meeting number") # Write most recent meeting number
    sheet.write(0, DIVISION, "Division") # Write division
    sheet.write(0, DIVISION_PREFERENCE, "Division preference")
    sheet.write(0, PROGRESS_MEETING_NOTES,"Last meeting notes")
    sheet.write(0, BIO, "Bio")
    sheet.write(0, CITY, "City")
    sheet.write(0, CURRENT_OCCUPATION, "Current Occupation")
    sheet.write(0, MENTOR_GENDER_PREFERENCE, "Mentor gender preference")
    sheet.write(0, GENDER_IDENTITY, "Gender identity")
    sheet.write(0, PERSONALITY_TRAITS, "Personality traits")
    sheet.write(0, PERSONAL_INTERESTS, "Personal interests")
    sheet.write(0, CAREER_INTERESTS_EXPERIENCE, "Career interests/experience")
    sheet.write(0, EDUCATION, "Education")

def print_to_sheet(business):

    # Create workbook
    wb = Workbook()

    # Create sheet
    sheet1 = wb.add_sheet('Sheet 1')
    write_col_guide(sheet1)

    users = User.query.filter_by(business_id=business.id)
    cnt = 1
    for u in users:
        sheet1.write(cnt, EMAIL, u.email) # Write email into 0th position
        sheet1.write(cnt, NAME, u.first_name + " " + u.last_name) # Write first name + last name into 1st position

        #write the mentor/mentee match
        if u.is_student: #user is a mentee
            sheet1.write(cnt, ROLE, "Mentee")
            select = Select.query.filter_by(mentee_id=u.id).first()
            if select != None:
                mentor = User.query.filter_by(id=select.mentor_id).first()
                sheet1.write(cnt, MATCH_EMAIL, mentor.email) # Write mentor email into 4th position
                sheet1.write(cnt, MATCH_NAME, mentor.first_name + " " + mentor.last_name) # Write mentor first name + last name into 5th position
                #write the amount of meetings completed
                write_meeting_info(sheet1, business.id, "mentee", select, cnt)
                #subtract 1 from current meeting id to get last meeting (not upcoming one)

            else: 
                sheet1.write(cnt, MATCH_EMAIL, "N/A") # Write mentor email into 4th position (N/A)
                sheet1.write(cnt, MATCH_NAME, "N/A") # Write mentor first name + last name into 5th position (N/A)

                sheet1.write(cnt, LAST_MEETING_TITLE, "N/A") #meeting title
                sheet1.write(cnt, LAST_MEETING_NUMBER, "N/A") #meeting number
        else: #user is a mentor
            sheet1.write(cnt, ROLE, "Mentor")
            select = Select.query.filter_by(mentor_id=u.id).first()
            if select != None:
                mentee = User.query.filter_by(id=select.mentee_id).first()
                sheet1.write(cnt, MATCH_EMAIL, mentee.email) # Write mentee email into 4th position
                sheet1.write(cnt, MATCH_NAME, mentee.first_name + " " + mentor.last_name) # Write mentee first name + last name into 5th position
           
                #write the amount of meetings completed
                write_meeting_info(sheet1, business.id, "mentor", select, cnt)
                #subtract 1 from current meeting id to get last meeting (not upcoming one)
            else:
                sheet1.write(cnt, MATCH_EMAIL, "N/A") # Write mentor email into 4th position (N/A)
                sheet1.write(cnt, MATCH_NAME, "N/A") # Write mentor first name + last name into 5th position (N/A)

                sheet1.write(cnt, LAST_MEETING_TITLE, "N/A") #meeting title
                sheet1.write(cnt, LAST_MEETING_NUMBER, "N/A") #meeting number

        
        #Write meeting responses

        sheet1.write(cnt, DIVISION, u.division) # Write division 7th position

        divisionPreference = u.division_preference
        if divisionPreference != None:
            if divisionPreference == "same":
                sheet1.write(cnt, DIVISION_PREFERENCE, "Same division") # Write user division preference
            elif divisionPreference == "different":
                sheet1.write(cnt, DIVISION_PREFERENCE, "Different division") 
            else:
                sheet1.write(cnt, DIVISION_PREFERENCE, "No preference") 
        else:
            sheet1.write(cnt, DIVISION_PREFERENCE, "N/A")

        sheet1.write(cnt, BIO, u.bio) # Write bio
        sheet1.write(cnt, CITY, u.city_name) # Write city name
        sheet1.write(cnt, CURRENT_OCCUPATION, u.current_occupation) # Write current occupation

        mentorGenderPreference = u.mentor_gender_preference
        if mentorGenderPreference != None:
            if mentorGenderPreference == "male":
                sheet1.write(cnt, MENTOR_GENDER_PREFERENCE, "Male mentor") # Write user mentor gender preference
            elif mentorGenderPreference == "female":
                sheet1.write(cnt, MENTOR_GENDER_PREFERENCE, "Female mentor")
            else:
                sheet1.write(cnt, MENTOR_GENDER_PREFERENCE, "No preference")
        else:
            sheet1.write(cnt, MENTOR_GENDER_PREFERENCE, "N/A")

        genderIdentity = u.gender_identity
        if genderIdentity != None:
            if genderIdentity == "male":
                sheet1.write(cnt, GENDER_IDENTITY, "Male")
            elif genderIdentity == "female":
                sheet1.write(cnt, GENDER_IDENTITY, "Female") # Write user gender identity
            elif genderIdentity == "nonbinaryNonconforming":
                sheet1.write(cnt, GENDER_IDENTITY, "Non-binary/non-conforming")
            else:
                sheet1.write(cnt, GENDER_IDENTITY, "Prefer not to respond")
        

        sheet1.write(cnt, PERSONALITY_TRAITS, u.personality_1 + "; " + u.personality_2 + "; " + u.personality_3)


        interestList = ""
        for interest in u.rtn_interests():
            interest = Tag.query.filter_by(id=interest.interestID).first()
            if interest != None:
                interestList += (interest.title + "; ")
        if len(interestList) > 2:
            interestList = interestList[:-2] #cut the semicolon
        sheet1.write(cnt, PERSONAL_INTERESTS, interestList)

        
        careerInterestList = ""
        for cint in u.rtn_career_interests():
            cint = CareerInterest.query.filter_by(id=cint.careerInterestID).first()
            if cint != None:
                careerInterestList += (cint.title + "; ")
        if len(careerInterestList) > 2:
            careerInterestList = careerInterestList[:-2] #cut the semicolon
        sheet1.write(cnt, CAREER_INTERESTS_EXPERIENCE, careerInterestList)


        educationList = ""
        for school in u.rtn_education():
            edu = School.query.filter_by(id=school.educationID).first()
            if edu != None:
                educationList += (edu.title + "; ")
        if len(educationList) > 2:
            educationList = educationList[:-2] #cut the semicolon
        sheet1.write(cnt, EDUCATION, educationList)

        cnt+=1
    
    filename = "excel_spreadsheets/" + business.name.replace(" ", "_") + \
        "_spreadsheet_(" + datetime.today().strftime('%Y-%m-%d') + ").xls"
    #format datetime into month/day/year
    wb.save(filename) 

    return filename


def write_meeting_info(sheet1, business_id, role, select, cnt):
    curr_meeting_id = select.current_meeting_number_mentor
    if select.current_meeting_number_mentee > curr_meeting_id: 
        curr_meeting_id = select.current_meeting_number_mentee
        #highest completed meeting between the mentee and mentor

    curr_meeting_id = curr_meeting_id - 1 #subtract 1 after finding the max to find the last completed meeting


    currProgressMeeting = ProgressMeeting.query.filter(ProgressMeeting.business_ID==business_id) \
            .filter(ProgressMeeting.num_meeting==curr_meeting_id).first()
    if currProgressMeeting != None:
        sheet1.write(cnt, LAST_MEETING_TITLE, currProgressMeeting.title) #meeting title
        sheet1.write(cnt, LAST_MEETING_NUMBER, currProgressMeeting.num_meeting) #meeting number

        pmci = ProgressMeetingCompletionInformation.query.filter(
            ProgressMeetingCompletionInformation.num_progress_meeting == curr_meeting_id,
            ProgressMeetingCompletionInformation.select_id == select.id
        ).first()

        #write the meeting notes
        if role == "mentee":
            sheet1.write(cnt, PROGRESS_MEETING_NOTES, pmci.mentee_meeting_notes)
        else:
            sheet1.write(cnt, PROGRESS_MEETING_NOTES, pmci.mentor_meeting_notes)
        
    else:
        sheet1.write(cnt, LAST_MEETING_TITLE, "No meetings completed") #meeting title
        sheet1.write(cnt, LAST_MEETING_NUMBER, "0") #meeting number



#call starter function
#get_business_name()

"""
if __name__ == '__main__':
    get_business_name()
"""