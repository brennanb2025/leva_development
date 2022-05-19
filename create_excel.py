import xlwt
from xlwt import Workbook
from app import db
from app.input_sets.models import Business, Select, User, ProgressMeeting, Tag, CareerInterest, School
from datetime import datetime 


def get_business_name():
    name = input("Business name: ")
    name = str(name)
    if Business.query.filter_by(name=name).first() == None:
        print("Failure - business with that name does not exist.")
    else:
        print_to_sheet(name)



"""
Writes to excel sheet
user --> information1, information2, etc.

"""        
def write_col_guide(sheet):
    sheet.write(0, 0, "Email") # Write email into 0th position
    sheet.write(0, 1, "Name") # Write first name + last name
    sheet.write(0, 2, "Role") # Write mentor/mentee
    sheet.write(0, 3, "Match email") # Write mentor/mentee email
    sheet.write(0, 4, "Match name") # Write mentor/mentee first name + last name
    sheet.write(0, 5, "Last meeting title") # Write most recent meeting title
    sheet.write(0, 6, "Last meeting number") # Write most recent meeting number
    sheet.write(0, 7, "Division") # Write division
    sheet.write(0, 8, "Division preference")
    sheet.write(0, 9, "Bio")
    sheet.write(0, 10, "City")
    sheet.write(0, 11, "Current Occupation")
    sheet.write(0, 12, "Mentor gender preference")
    sheet.write(0, 13, "Gender identity")
    sheet.write(0, 14, "Personality traits")
    sheet.write(0, 15, "Personal interests")
    sheet.write(0, 16, "Career interests/experience")
    sheet.write(0, 17, "Education")

def print_to_sheet(name):
    # Create workbook
    wb = Workbook()
    
    # Create sheet
    sheet1 = wb.add_sheet('Sheet 1')
    write_col_guide(sheet1)

    business = Business.query.filter_by(name=name).first()

    users = User.query.filter_by(business_id=business.id)
    cnt = 1
    for u in users:
        sheet1.write(cnt, 0, u.email) # Write email into 0th position
        sheet1.write(cnt, 1, u.first_name + " " + u.last_name) # Write first name + last name into 1st position

        #write the mentor/mentee match
        if u.is_student: #user is a mentee
            sheet1.write(cnt, 2, "Mentee")
            select = Select.query.filter_by(mentee_id=u.id).first()
            if select != None:
                mentor = User.query.filter_by(id=select.mentor_id).first()
                sheet1.write(cnt, 3, mentor.email) # Write mentor email into 4th position
                sheet1.write(cnt, 4, mentor.first_name + " " + mentor.last_name) # Write mentor first name + last name into 5th position

                #write the amount of meetings completed
                write_meeting_info(sheet1, business.id, select.current_meeting_ID-1, cnt)
                #subtract 1 from current meeting id to get last meeting (not upcoming one)

            else: 
                sheet1.write(cnt, 3, "N/A") # Write mentor email into 4th position (N/A)
                sheet1.write(cnt, 4, "N/A") # Write mentor first name + last name into 5th position (N/A)

                sheet1.write(cnt, 5, "N/A") #meeting title
                sheet1.write(cnt, 6, "N/A") #meeting number
        else: #user is a mentor
            sheet1.write(cnt, 2, "Mentor")
            select = Select.query.filter_by(mentor_id=u.id).first()
            if select != None:
                mentee = User.query.filter_by(id=select.mentee_id).first()
                sheet1.write(cnt, 3, mentee.email) # Write mentee email into 4th position
                sheet1.write(cnt, 4, mentee.first_name + " " + mentor.last_name) # Write mentee first name + last name into 5th position
           
                #write the amount of meetings completed
                write_meeting_info(sheet1, business.id, select.current_meeting_ID-1, cnt)
                #subtract 1 from current meeting id to get last meeting (not upcoming one)
            else:
                sheet1.write(cnt, 3, "N/A") # Write mentor email into 4th position (N/A)
                sheet1.write(cnt, 4, "N/A") # Write mentor first name + last name into 5th position (N/A)

                sheet1.write(cnt, 5, "N/A") #meeting title
                sheet1.write(cnt, 6, "N/A") #meeting number

        
        #Write meeting responses

        sheet1.write(cnt, 7, u.division) # Write division 7th position

        divisionPreference = u.division_preference
        if divisionPreference != None:
            if divisionPreference == "same":
                sheet1.write(cnt, 8, "Same division") # Write user division preference
            elif divisionPreference == "different":
                sheet1.write(cnt, 8, "Different division") 
            else:
                sheet1.write(cnt, 8, "No preference") 
        else:
            sheet1.write(cnt, 8, "N/A")

        sheet1.write(cnt, 9, u.bio) # Write bio
        sheet1.write(cnt, 10, u.city_name) # Write city name
        sheet1.write(cnt, 11, u.current_occupation) # Write current occupation

        mentorGenderPreference = u.mentor_gender_preference
        if mentorGenderPreference != None:
            if mentorGenderPreference == "male":
                sheet1.write(cnt, 12, "Male mentor") # Write user mentor gender preference
            elif mentorGenderPreference == "female":
                sheet1.write(cnt, 12, "Female mentor")
            else:
                sheet1.write(cnt, 12, "No preference")
        else:
            sheet1.write(cnt, 12, "N/A")

        genderIdentity = u.gender_identity
        if genderIdentity != None:
            if genderIdentity == "male":
                sheet1.write(cnt, 13, "Male")
            elif genderIdentity == "female":
                sheet1.write(cnt, 13, "Female") # Write user gender identity
            elif genderIdentity == "nonbinaryNonconforming":
                sheet1.write(cnt, 13, "Non-binary/non-conforming")
            else:
                sheet1.write(cnt, 13, "Prefer not to respond")
        

        sheet1.write(cnt, 14, u.personality_1 + "; " + u.personality_2 + "; " + u.personality_3)


        interestList = ""
        for interest in u.rtn_interests():
            interest = Tag.query.filter_by(id=interest.interestID).first()
            if interest != None:
                interestList += (interest.title + "; ")
        if len(interestList) > 2:
            interestList = interestList[:-2] #cut the semicolon
        sheet1.write(cnt, 15, interestList)

        
        careerInterestList = ""
        for cint in u.rtn_career_interests():
            cint = CareerInterest.query.filter_by(id=cint.careerInterestID).first()
            if cint != None:
                careerInterestList += (cint.title + "; ")
        if len(careerInterestList) > 2:
            careerInterestList = careerInterestList[:-2] #cut the semicolon
        sheet1.write(cnt, 16, careerInterestList)


        educationList = ""
        for school in u.rtn_education():
            edu = School.query.filter_by(id=school.educationID).first()
            if edu != None:
                educationList += (edu.title + "; ")
        if len(educationList) > 2:
            educationList = educationList[:-2] #cut the semicolon
        sheet1.write(cnt, 17, educationList)

        cnt+=1
    
    wb.save("excel_spreadsheets/" + name.replace(" ", "_") + \
        "_spreadsheet_(" + datetime.today().strftime('%Y-%m-%d') + ").xls") #format datetime into month/day/year
    print("Success!")


def write_meeting_info(sheet1, business_id, curr_meeting_id, cnt):
    currProgressMeeting = ProgressMeeting.query.filter(ProgressMeeting.business_ID==business_id) \
            .filter(ProgressMeeting.num_meeting==curr_meeting_id).first()
    if currProgressMeeting != None:
        sheet1.write(cnt, 5, currProgressMeeting.title) #meeting title
        sheet1.write(cnt, 6, currProgressMeeting.num_meeting) #meeting number
    else:
        sheet1.write(cnt, 5, "No meetings completed") #meeting title
        sheet1.write(cnt, 6, "0") #meeting number


#call starter function
get_business_name()

"""
if __name__ == '__main__':
    get_business_name()
"""