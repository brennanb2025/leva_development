from requests import delete
from app import db
from app.input_sets.models import Event, Select, Business, User, ProgressMeetingCompletionInformation, AdminUser

#from app.routes import delete_intro_video, delete_profile_picture, delete_resume, delete_user_attributes, logData

print(User.query.all())
"""
u = AdminUser(
    email="adminTest1@test.com",
    first_name="adminTest1First",
    last_name="adminTest1Last",
    business_id=1
)

db.session.add(u) #add to database
u.set_password("adminTest1") #must set pwd w/ hashing method
db.session.commit()

print("All admin users:",AdminUser.query.all())
"""


"""for b in Business.query.all():
    print(b)
"""

#print(User.query.filter_by(last_name="lisa").all())

#for u in User.query.all():
#    print(u)

"""
for s in Select.query.all():
    print(s)

for p in ProgressMeetingCompletionInformation.query.all():
    print(p)
    """  



"""
user = User.query.filter_by(first_name = "Kara").first()
#user = User.query.filter_by(first_name = "Linda").first()


delete_profile_picture(user)
delete_intro_video(user)
delete_user_attributes(user.id)
delete_resume(user)

selectEntry = None
if user.is_student: #is mentee
    selectEntry = Select.query.filter_by(mentee_id=user.id).all()

    for s in selectEntry:
        ProgressMeetingCompletionInformation.query.filter(
            ProgressMeetingCompletionInformation.select_id == s.id
        ).delete()

    Select.query.filter_by(mentee_id=user.id).delete()
else:
    selectEntry = Select.query.filter_by(mentor_id=user.id).all()

    for s in selectEntry:
        ProgressMeetingCompletionInformation.query.filter(
            ProgressMeetingCompletionInformation.select_id == s.id
        ).delete()

    Select.query.filter_by(mentor_id=user.id).delete()

Business.query.filter_by(id=user.business_id).first().dec_number_employees_currently_registered() 
#decrease business number registered by 1 because this user has been deleted


User.query.filter_by(id=user.id).delete()
db.session.commit()
"""

#print(User.query.filter_by(first_name = "Kara").all())

"""
Event.query.filter_by(action=16).delete()
db.session.commit()

print(Event.query.filter_by(action=18).all())
print(str(len(Event.query.all())))
"""


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

"""
Event.query.filter_by(action=16).delete()
db.session.commit()

print(Event.query.filter_by(action=18).all())
print(str(len(Event.query.all())))
"""
