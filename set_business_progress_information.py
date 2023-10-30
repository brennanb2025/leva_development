from app import db
from app.input_sets.models import ProgressMeeting, Business, Select, User, ProgressMeetingCompletionInformation
import datetime
from sqlalchemy import desc

"""for b in Business.query.all():
    print(b)"""


def get_progress_meetings(business_id): #returns the progress meetings from a given business id
    return db.session.query( \
            ProgressMeeting,
            Business
        ).outerjoin(ProgressMeeting, Business.id == ProgressMeeting.business_ID) \
        .filter(
            ProgressMeeting.business_ID == business_id
        ).order_by(
            ProgressMeeting.num_meeting
        ).all()


#print("Selects:")
#print(Select.query.all())


business_name = "SWE"
#business_name = "test_progress_meetings_business"
business_id = Business.query.filter_by(name=business_name).first().id

progressMeetings = get_progress_meetings(business_id)


print("\nProgress meetings in this business (" + business_name + "):")
for pm in progressMeetings:
    print(pm.ProgressMeeting)




#resetting stuff to ensure that changes are stable
#userToResetNumMeetingID = User.query.filter_by(email="u1@u1.com").first().id
#Select.query.filter_by(mentee_id=userToResetNumMeetingID).first().current_meeting_ID = 1
#ProgressMeeting.query.filter_by(business_ID=business_id).delete()



#This actually changes the progress meetings

businessID = Business.query.filter_by(name=business_name).first().id

#titles = []
#titles.append...
titleNovember = "Getting to Know Your Mentor/Mentee" #November
titleDecember = "Final Exams Prep and Advice" #December
titleJanuary = "Choosing a Major and Academic Opportunities at NU" 
titleFebruary = "Finding Your Path at NU (Clubs, Social Groups, Sports, Study Abroad, etc)"
titleMarch = "Careers, Internships, Research, and Fellowships"
titleApril = "General Advice from Mentors - \"I wish I had...\""
titleMay = "Summer Plans and Plans for Next Year"
titleJune = "Finals and Goodbyes!"


#content_descriptions = []
#content_descriptions.append(...)


#contentList = []
#contentList.append("""

contentNovember = """After you have interacted with your mentor/mentee at least once, please complete this mandatory 10-question survey about your initial experience. \n
https://forms.gle/BADUhCdxwLCJXHqeA
"""

contentDecember = """After you have interacted with your mentor/mentee at least once, please complete this mandatory 10-question survey about your initial experience. \n
https://forms.gle/BADUhCdxwLCJXHqeA
"""


"""
Sample Agenda \n
\n
Example Questions for Mentors\n
∙ How do you see our culture supporting women and where are the opportunities?\n
∙ What are your professional goals and how can I help you get there?\n
∙ What drives you?\n
∙ What makes you who you are?\n
∙ What are your strengths and weaknesses?\n
∙ What aspects of your career are you hoping to improve on?\n
∙ How can I best support you?\n
 \n
Example Questions for Mentees\n
∙ What does female empowerment in the workplace look like to you?\n
∙ What advice do you have to better support myself as a woman and/or how I can better support other women? \n
∙ Tell me about your path to your current position.  \n
∙ What makes you who you are?\n
∙ What aspects of your career have given you fulfillment?\n
∙ How have past mentorship relationships impacted you?\n
∙ What advice do you have for me at my stage of career?\n
"""

"""
contentList.append("Meeting 2 content!")
contentList.append("Meeting 3 content!")
contentList.append("content3")
contentList.append("content4")"""

#Create the meetings:

"""
first_meeting_date = datetime.datetime(2022, 10, 26) #10/26/22
numMeetings = 4
timeBetweenMeeting = 10 #days
for i in range(numMeetings):
    # add timeBetweenMeetings
    # set meeting, num meeting as i
    newMeeting = ProgressMeeting(business_ID=businessID,
            completion_date=(first_meeting_date + datetime.timedelta(days=i*timeBetweenMeeting)),
            num_meeting = (i+1), 
            title=titles[i],
            content_description=content_descriptions[i],
            content=contentList[i])
    db.session.add(newMeeting)
"""

novemberDate = datetime.datetime(2022,11,30)
decemberDate = datetime.datetime(2022,12,31)
januaryDate = datetime.datetime(2023,1,31)
februaryDate = datetime.datetime(2023,2,28)
marchDate = datetime.datetime(2023,3,31)
aprilDate = datetime.datetime(2023,4,30)
mayDate = datetime.datetime(2023,5,31)
juneDate = datetime.datetime(2023,6,30)

meetingNovember = ProgressMeeting(business_ID=businessID,
        completion_date=novemberDate,
        num_meeting = 1,
        title=titleNovember,
        content_description="",
        content=contentNovember)
db.session.add(meetingNovember)

meetingDecember = ProgressMeeting(business_ID=businessID,
        completion_date=decemberDate,
        num_meeting = 2, 
        title=titleDecember,
        content_description="",
        content=contentDecember)
db.session.add(meetingDecember)

meetingJanuary = ProgressMeeting(business_ID=businessID,
        completion_date=januaryDate,
        num_meeting = 3, 
        title=titleJanuary,
        content_description="",
        content="")
db.session.add(meetingJanuary)

meetingFebruary = ProgressMeeting(business_ID=businessID,
        completion_date=februaryDate,
        num_meeting = 4, 
        title=titleFebruary,
        content_description="",
        content="")
db.session.add(meetingFebruary)

meetingMarch = ProgressMeeting(business_ID=businessID,
        completion_date=marchDate,
        num_meeting = 5, 
        title=titleMarch,
        content_description="",
        content="")
db.session.add(meetingMarch)

meetingApril = ProgressMeeting(business_ID=businessID,
        completion_date=aprilDate,
        num_meeting = 6, 
        title=titleApril,
        content_description="",
        content="")
db.session.add(meetingApril)

meetingMay = ProgressMeeting(business_ID=businessID,
        completion_date=mayDate,
        num_meeting = 7, 
        title=titleMay,
        content_description="",
        content="")
db.session.add(meetingMay)

meetingJune = ProgressMeeting(business_ID=businessID,
        completion_date=juneDate,
        num_meeting = 8, 
        title=titleJune,
        content_description="",
        content="")
db.session.add(meetingJune)



print("\n\nProgress meetings in this business (" + business_name + ") - after adding:")
for pm in get_progress_meetings(business_id):
    print(pm.ProgressMeeting)



#setting selects - this is unneeded and was from the past.
"""
for u in User.query.all():
    select = Select.query.filter_by(mentee_id=u.id).first()
    if select != None:
        select.set_current_meeting_ID("mentee", 1)
    select = Select.query.filter_by(mentor_id=u.id).first()
    if select != None:
        select.set_current_meeting_ID("mentor", 1)

for s in Select.query.all():
    print(s.current_meeting_number_mentor)
    print(s.current_meeting_number_mentee)
"""

#ProgressMeetingCompletionInformation.query.filter_by(id=5).delete()
#Select.query.filter_by(id=7).first().set_current_meeting_ID("mentee",2)
#Select.query.filter_by(id=7).first().set_current_meeting_ID("mentor",2)

#print(ProgressMeetingCompletionInformation.query.all())

#delete meeting notes
#ProgressMeetingCompletionInformation.query.delete()








#Only uncomment this when the changes are final.
#db.session.commit()
