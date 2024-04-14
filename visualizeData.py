from requests import delete
from app import db
from app.input_sets.models import Event, Select, Business, User, ProgressMeetingCompletionInformation, AdminUser, UserFeedWeights

import app.model.admin as admin
import app.model.editProfile as editProfileFuncs
import app.model.feed as feedFuncs

#from app.routes import delete_intro_video, delete_profile_picture, delete_resume, delete_user_attributes, logData



# b = Business(
#     name="brennanTest",
#     number_employees_maximum=100,
#     number_employees_currently_registered=0)
# db.session.add(b)
# db.session.commit()

# for b in Business.query.all():
#     print(b.id, b.name)


# print(User.query.filter_by(email="a@a.com").first())
# print(User.query.filter_by(email="c@c.com").first())

print("a@a.com feed with weights:")
m13M = feedFuncs.get_all_matches_feedWeights(13)
print([(m13.mentor, m13.score) for m13 in m13M.matches])

print("c@c.com feed with weights:")
m15M = feedFuncs.get_all_matches_feedWeights(15)
print([(m15.mentor, m15.score) for m15 in m15M.matches])


# dictWeights13 = {}
# dictWeights13['personality'] = 1 # rates personality None
# dictWeights13['mentor_gender_preference'] = 0 # rates mentor gender preference None
# dictWeights13['interests'] = 2 # rates interests important
# dictWeights13['career_interests'] = 2 # rates career interests important
# dictWeights13['education'] = 0 # rates education not important
# editProfileFuncs.setFeedWeight(13, dictWeights13)


# dictWeights14 = {}
# dictWeights14['personality'] = 1 # rates personality None (alike, 1, 100%)
# dictWeights14['mentor_gender_preference'] = 0 # mentor gender preference None (is mentor) (alike, 0,0 low-low, 50%)
# dictWeights14['interests'] = 2 # rates interests important (alike, 2-2, high-high: 100%)
# dictWeights14['career_interests'] = 1 # rates career interests none (diff, 2-1, high-none: 100%)
# dictWeights14['education'] = 2 # rates education important (diff, 0-2, high-low: 75%)
# editProfileFuncs.setFeedWeight(14, dictWeights14)

"""
u = AdminUser(
    email="brennanbenson2025@u.northwestern.edu",
    first_name="Brennan",
    last_name="Benson",
    business_id=3
)

db.session.add(u) #add to database
u.set_password("brennanbenson2025@u.northwestern.edu") #must set pwd w/ hashing method
db.session.commit()
"""

#print("All admin users:", AdminUser.query.all())



"""
for b in Business.query.all():
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
    print(u.email)
    print(u.first_name)

"""

"""
Event.query.filter_by(action=16).delete()
db.session.commit()

print(Event.query.filter_by(action=18).all())
print(str(len(Event.query.all())))
"""
