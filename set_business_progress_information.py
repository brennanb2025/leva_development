from app import db
from app.input_sets.models import ProgressMeeting, Business
import datetime

"""for b in Business.query.all():
    print(b)"""

for m in ProgressMeeting.query.all():
    print(m)


#businessID = Business.query.filter_by(name="<businessName>").first().id
print(Business.query.filter_by(name="businessProgressTest").first())
businessID = Business.query.filter_by(name="businessProgressTest").first().id

titles = []
titles.append("title1")
titles.append("title2")
titles.append("title3")
titles.append("title4")

content_descriptions = []
content_descriptions.append("description1")
content_descriptions.append("description2")
content_descriptions.append("description3")
content_descriptions.append("description4")

contentList = []
contentList.append("content1")
contentList.append("content2")
contentList.append("content3")
contentList.append("content4")

#alternatively,
first_meeting_date = datetime.datetime(2022, 4, 25) #2/25/22
numMeetings = 4
timeBetweenMeeting = 20 #days
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

db.session.commit()
