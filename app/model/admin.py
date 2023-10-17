
"""
Methods to move:
admin_login_post
admin_data
admin_lookup_user
admin_lookup_users_in_business
admin_selects_info
admin_user_matches
admin_lookup_business
admin_all_businesses
admin_get_events
logData(num, msg)

"""
from app.input_sets.models import User, Select, Business, Event
from app import app, db

def admin_validate_login(username, password):
    return str(app.config['ADMIN_PASSWORD']) == password and str(app.config['ADMIN_USERNAME']) == username

def admin_lookup_user(userId, firstName, lastName, email):
    if userId != None:  
        return User.query.filter_by(id=userId).all()
    if firstName != None and lastName != None:
        return User.query.filter(
                first_name = firstName,
                last_name = lastName).all()
    if email != None:
        return User.query.filter_by(email=email).all()

def admin_lookup_users_in_business(businessId):
    return User.query.filter_by(
                business_id=businessId
            ).all()


def selects_info(businessId):
    users = User.query.filter_by(
                business_id=businessId
            ).all()

    unmatchedUsers = []
    listSelects = {} #select id : select
    for u in users:
        select = None
        if u.is_student:
            selects = Select.query.filter_by(mentee_id=u.id).all()
        else:
            selects = Select.query.filter_by(mentor_id=u.id).all()
        if len(selects) == 0:
            unmatchedUsers.append(u) #id, first name, last name, email
        
        #could have multiple selects
        for s in selects:
            listSelects[s.id] = s #add the select
        
    arrInfo = []
    for s in listSelects.keys():
        select = listSelects[s]
        arrInfo.append( #select, mentee, mentor
                (select, User.query.filter_by(id=select.mentee_id).first(), User.query.filter_by(id=select.mentor_id).first()))
        

    return unmatchedUsers, arrInfo


def user_matches(businessId):
    match_and_users = db.session.query( \
            User,
            Select
    ).filter( \
        User.business_id == businessId and User.is_student
    ).outerjoin(User, User.id == Select.mentee_id).all()

    dictMenteeToMentor = {}
    for s_u in match_and_users:
        if not dictMenteeToMentor.__contains__(s_u.User):
            dictMenteeToMentor[s_u.User] = []
        dictMenteeToMentor[s_u.User].append(User.query.filter_by(id=s_u.Select.mentor_id).first())

    return dictMenteeToMentor


def lookup_business(businessId, businessString):
    business = None
    if businessId:
        business = Business.query.filter_by(id=int(businessId)).first()
    if businessString:
        business = Business.query.filter_by(name=businessId).first()

    return business


def all_businesses():
    return Business.query.all()


def get_events(action, startTime, endTime):
    #note: for and here must use special ampersand character - also requires parentheses because of operator precedence
    return Event.query.filter_by(action=action).filter(
        (Event.timestamp >= startTime) & (Event.timestamp <= endTime)).limit(100).all()




def logData(num, msg, userId):
    if str(app.config['LOG_DATA']) == "True" and num != None and msg != None and userId != None:
        newEvent = Event(userID=userId, action=num, message=msg)
        db.session.add(newEvent)
        db.session.commit()