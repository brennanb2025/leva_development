
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
from app.input_sets.models import User, Select, Business, Event, ProgressMeetingCompletionInformation
from app import app, db
import app.model.feed as feed
from app.utils.create_excel import create_excel_sheet


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
        if s_u.User not in dictMenteeToMentor:
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

#gets all matches (even if user is already matched, including already matched people.)
def get_all_matches(userId):
    #returns array of objects: match info (userid, matching stuff, score, etc)

    user = User.query.filter_by(id=userId).first()

    if user is None:
        return None

    if user.is_student:
        return feed.get_all_matches(userId)
    return None


#get potential future matches for user
def get_potential_matches(userId):
    #returns array of objects: match info (userid, matching stuff, score, etc)

    user = User.query.filter_by(id=userId).first()
    if user is None:
        return None

    if user.is_student:
        return feed.feedMentee(userId)
    return None

#does not handle multiple mentees : one mentor. Must be one mentor : 1 mentee
def validate_matches(matches): #takes {menteeId : mentorId}
    invalidMatches = {}

    #verify all are mentee:mentor
    for m in matches.keys():
        if not m.is_student:
            invalidMatches[m] = matches[m]
        if matches[m].is_student:
            invalidMatches[m] = matches[m]

    #handle multiple mentees choosing the same mentor

    numMentorMatching = {}
    #get the # each mentor is matched:
    for m in matches.values():
        if m in numMentorMatching:
            numMentorMatching[m] += 1
        else:
            numMentorMatching[m] = 1


    #verify none already in database
    for m in matches.keys():

        #this match doesn't exist in the db
        selectQuery = db.session.query( \
                Select
            ).filter( \
                Select.mentee == m.id and Select.mentor_id == matches[m].id
            ).first()
        if selectQuery != None:
            invalidMatches[m] = matches[m] #invalid

        #check if the pairing can each make another match
        mentee = User.query.filter_by(id=m.id)
        mentor = User.query.filter_by(id=matches[m].id)
        selectsMentee = Select.query.filter_by(mentee_id=m.id).all()
        selectsMentor = Select.query.filter_by(mentor_id=matches[m].userId).all()
        
        if len(selectsMentee) >= mentee.num_pairings_can_make or \
                numMentorMatching[matches[m].id]+len(selectsMentor) >= mentor.num_pairings_can_make:
            #can't go over number of times this mentor has been chosen in the given dict
            # + the # of pairings the mentor was already a part of.
            invalidMatches[m] = matches[m] #invalid

    return invalidMatches


def applyMatches(matches): #takes {menteeId : mentorId} -> bool denoting success
    if len(validate_matches(matches)) != 0:
        return False

    for m in matches.keys: #post new select for each pairing
        success = feed.feedPost(m.id, matches[m].id)
        if not success:
            return False

    return True
    
def deleteMatch(menteeId, mentorId):

    selectQuery = db.session.query( \
                Select
            ).filter( \
                Select.mentee_id == menteeId and Select.mentor_id == mentorId
            ).first()

    if selectQuery is None:
        return False

    print("deleting match:", selectQuery)

    #delete any progress meetings associated with this user
    ProgressMeetingCompletionInformation.query.filter(
            #ProgressMeetingCompletionInformation.num_progress_meeting == selectQuery.current_meeting_number_mentee,
            ProgressMeetingCompletionInformation.select_id == selectQuery.id
        ).delete()    
    
    #delete the select
    Select.query.filter_by(id=selectQuery.id).delete()

    db.session.commit() #only commit when all deletes are done
    return True
    

def createExcelSheet(businessId):
    return create_excel_sheet(businessId)


def logData(num, msg, userId):
    if str(app.config['LOG_DATA']) == "True" and num != None and msg != None and userId != None:
        newEvent = Event(userID=userId, action=num, message=msg)
        db.session.add(newEvent)
        db.session.commit()