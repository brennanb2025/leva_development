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
            desc(ProgressMeeting.num_meeting)
        ).all()




business_name = "The Garage"
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

titles = []
titles.append("Initial progress meeting")
"""
titles.append("Meeting 2")
titles.append("Meeting 3")
titles.append("title3")
titles.append("title4")"""


content_descriptions = []
content_descriptions.append("""
    Topics To Guide Your First Meeting:\n
    ∙ Establish your goals for the mentorship program. Be clear about what you are looking for and how you can help each other. \n
    ∙ Discuss female empowerment in the workplace, what that looks like to you, and how both the mentee and the mentor can actively support women.  \n
    ∙ Learn about career history and personal interests.  \n
    ∙ Coordinate another time to meet that works for both of you.
""")

"""
content_descriptions.append("Meeting 2 description!")
content_descriptions.append("Meeting 3 description")
content_descriptions.append("description3")
content_descriptions.append("description4")"""


contentList = []
contentList.append("""
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
""")

"""contentList.append("Meeting 2 content!")
contentList.append("Meeting 3 content!")
contentList.append("content3")
contentList.append("content4")"""

#Create the meetings:
"""
first_meeting_date = datetime.datetime(2022, 6, 10) #6/13/22
numMeetings = 1
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

"""
print("\n\nProgress meetings in this business (" + business_name + ") - after adding:")
for pm in get_progress_meetings(business_id):
    print(pm.ProgressMeeting)
"""


#setting selects
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
