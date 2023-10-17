from requests import delete
from app import db
from app.input_sets.models import Event, Select, Business, User, ProgressMeetingCompletionInformation

from app.routes import delete_intro_video, delete_profile_picture, delete_resume, delete_user_attributes, logData

"""
for b in Business.query.all():
    print(b)

for u in User.query.all():
<<<<<<<<< Temporary merge branch 1
    print(u.email)
    print(u.first_name)
=========
    print(u)
>>>>>>>>> Temporary merge branch 2

"""
Event.query.filter_by(action=16).delete()
db.session.commit()

print(Event.query.filter_by(action=18).all())
print(str(len(Event.query.all())))
"""