"""
Functions to add:
progress
getMeetingInfo(m)
getCompletedMeetingInfo(m, isMentee, selectId, currentMeetingNum)
currentMeetingSetDone
"""

from app import app, db

from app.input_sets.models import User, Tag, InterestTag, EducationTag, School, CareerInterest, \
        CareerInterestTag, Select, Business, Event, ProgressMeeting, \
        ProgressMeetingCompletionInformation, UserFeedback



class ProgressInfo:
    def __init__(self, selectEntry=None, matchedUser=None, currentMeetingNumber=None,
                progressDone=None, currMeetingInfo=None, prevMeetingInfo=None,
                futureMeetingInfo=None):
        self.selectEntry = selectEntry
        self.matchedUser = matchedUser
        self.currentMeetingNumber = currentMeetingNumber
        self.progressDone = progressDone
        self.currMeetingInfo = currMeetingInfo
        self.prevMeetingInfo = prevMeetingInfo
        self.futureMeetingInfo = futureMeetingInfo

#TODO MAKE OBJECT
def get_progress_info(user):
    isMentee = user.is_student #user.is_mentee

    progressInfos = []

    select_mentor_mentee = None #the mentor or mentee that the user logged in has selected, or None
    if isMentee: 
        selectEntries = Select.query.filter_by(mentee_id=user.id).all()
        for entry in selectEntries:
            select_mentor_mentee = User.query.filter_by(id=entry.mentor_id).first()
            currentMeetingNumber = entry.current_meeting_number_mentee
            progressInfos.append(
                ProgressInfo(
                    selectEntry=entry,
                    matchedUser=select_mentor_mentee,
                    currentMeetingNumber=currentMeetingNumber
                )
            )
    else:
        selectEntries = Select.query.filter_by(mentor_id=user.id).all()
        for entry in selectEntries:
            select_mentor_mentee = User.query.filter_by(id=entry.mentee_id).first()
            currentMeetingNumber = entry.current_meeting_number_mentor
            progressInfos.append(
                ProgressInfo(
                    selectEntry=entry,
                    matchedUser=select_mentor_mentee,
                    currentMeetingNumber=currentMeetingNumber
                )
            )

    for i in range(len(progressInfos)):
        #selectEntry is the database entry for this user's select. It will be None if this user hasn't been selected/hasn't yet selected.
        
        info = progressInfos[i]

        progressDone = False

        futureMeetingInfo = [] #future meeting list of info dicts
        prevMeetingInfo = [] #previous meeting list of info dicts
        currMeetingInfo = {} #current meeting info dict
        if info.selectEntry != None and info.currentMeetingNumber != None:
            currMeeting = ProgressMeeting.query.filter(ProgressMeeting.business_ID==user.business_id, \
                    ProgressMeeting.num_meeting==info.currentMeetingNumber).first()
            if currMeeting != None:
                progressInfos[i].currMeetingInfo = getMeetingInfo(currMeeting)
            else:
                progressDone = True

            previousMeetings = ProgressMeeting.query.filter(ProgressMeeting.business_ID==user.business_id, \
                    ProgressMeeting.num_meeting < info.currentMeetingNumber).all()
            futureMeetings = ProgressMeeting.query.filter(ProgressMeeting.business_ID==user.business_id, \
                    ProgressMeeting.num_meeting > info.currentMeetingNumber).all()
            
            for m in previousMeetings: #build the dicts of the info about each meeting
                prevMeetingInfo.append(getCompletedMeetingInfo(m, isMentee, info.selectEntry.id, m.num_meeting))
            for m in futureMeetings:
                futureMeetingInfo.append(getMeetingInfo(m))

            progressInfos[i].prevMeetingInfo = prevMeetingInfo

            progressInfos[i].futureMeetingInfo = futureMeetingInfo

            progressInfos[i].progressDone = progressDone

    return progressInfos





#Returns a dict of all the necessary meeting information to show. 
#This will change the text in the content description and the content into an array of the different paragraphs
#(It splits around \n.)
def getMeetingInfo(m): 
    mInfo = {}
    mInfo["num"] = m.num_meeting
    mInfo["date"] = m.completion_date.strftime("%B %d, %Y")
    mInfo["title"] = m.title
    mInfo["desc"] = m.content_description.split('\n')
    mInfo["content"] = m.content.split('\n')
    return mInfo

#Returns a dict of all the necessary meeting information to show, but for the completed meetings. 
#Specifically, gets the meeting notes for the specified user.
def getCompletedMeetingInfo(m, isMentee, selectId, currentMeetingNum): 
    mInfo = {}
    mInfo["num"] = m.num_meeting
    mInfo["date"] = m.completion_date.strftime("%B %d, %Y")
    mInfo["title"] = m.title
    mInfo["desc"] = m.content_description.split('\n')
    mInfo["content"] = m.content.split('\n')
    
    if isMentee:
        mInfo["meetingNotes"] = ProgressMeetingCompletionInformation.query.filter(
            ProgressMeetingCompletionInformation.num_progress_meeting == currentMeetingNum,
            ProgressMeetingCompletionInformation.select_id == selectId
        ).first().mentee_meeting_notes
    else:
        mInfo["meetingNotes"] = ProgressMeetingCompletionInformation.query.filter(
            ProgressMeetingCompletionInformation.num_progress_meeting == currentMeetingNum,
            ProgressMeetingCompletionInformation.select_id == selectId
        ).first().mentor_meeting_notes
        
    return mInfo


def submitFeedback(userid, content):
    user = User.query.filter_by(id=userid).first()
    if not User:
        return False

    business = user.business_id

    # get current meeting number
    isMentee = user.is_student
    if isMentee: 
        selectEntry = Select.query.filter_by(mentee_id=user.id).first() #the entry of the mentor-mentee selection, or None
        lastMeetingNumber = selectEntry.current_meeting_number_mentee
    else:
        selectEntry = Select.query.filter_by(mentor_id=user.id).first() #the entry of the mentor-mentee selection, or None
        lastMeetingNumber = selectEntry.current_meeting_number_mentor

    userFeedback = UserFeedback(user_id=userid, content=content, business_id=business, meeting_number=lastMeetingNumber)
    db.session.add(userFeedback)
    db.session.commit()


def shouldSolicitFeedback(user):
    # get last UserFeedback
    lastFeedback = UserFeedback.query.filter(
        UserFeedback.user_id == user.id
    ).order_by(
        UserFeedback.meeting_number.desc() # opposite order .first() = last
    ).first()

    # get business feedback solicitation frequency
    frequency = Business.query.filter_by(id=user.business_id).first().feedback_solicitation_frequency

    # get last submitted progress meeting number
    isMentee = user.is_student
    if isMentee: 
        selectEntry = Select.query.filter_by(mentee_id=user.id).first() #the entry of the mentor-mentee selection, or None
        lastMeetingNumber = selectEntry.current_meeting_number_mentee
    else:
        selectEntry = Select.query.filter_by(mentor_id=user.id).first() #the entry of the mentor-mentee selection, or None
        lastMeetingNumber = selectEntry.current_meeting_number_mentor

    # should solicit feedback if: 
    # last submitted progress meeting number - last feedback meeting number >= frequency
    # eg last time user submitted feedback was after meeting 1, they just finished their 4th meeting, 
    # frequency = every 3 meetings. It prompted them after meeting 1, they submitted,
    # that was 3 meetings ago, prompt them again.

    if not lastFeedback: # user has never submitted feedback
        # in this case, we should solicit feedback unless the frequency is 0.
        if not frequency or frequency == 0:
            return False
        return True

    return (lastMeetingNumber - lastFeedback.meeting_number) >= frequency


def set_current_meeting_info_done(user, matchUser, meetingNotes):

    isMentee = user.is_student

    if isMentee: 
        selectEntry = Select.query.filter_by(mentee_id=user.id, mentor_id=matchUser.id).first() #the entry of the mentor-mentee selection, or None
        if selectEntry != None:
            completionInfoMentee = ProgressMeetingCompletionInformation.query.filter(
                ProgressMeetingCompletionInformation.num_progress_meeting == selectEntry.current_meeting_number_mentee,
                ProgressMeetingCompletionInformation.select_id == selectEntry.id
            ).first()
            if completionInfoMentee == None: 
                #if there is no existing meeting notes for this meeting
                completionInfo = ProgressMeetingCompletionInformation(
                    num_progress_meeting = selectEntry.current_meeting_number_mentee,
                    select_id = selectEntry.id,
                    mentee_meeting_notes = meetingNotes
                )
                db.session.add(completionInfo)
                #no meeting notes for this one, creating them for the mentee
            else:
                #update meeting notes
                #meeting notes already exist, setting mentee notes here
                completionInfoMentee.set_meeting_notes(meetingNotes, "mentee")
                completionInfoMentee.set_completion_timestamp("mentee") #update timestamp

            selectEntry.inc_current_meeting_ID("mentee") #increment the meeting number
            db.session.commit()

    else:
        selectEntry = Select.query.filter_by(mentor_id=user.id, mentee_id=matchUser.id).first()
        if selectEntry != None:
            completionInfoMentor = ProgressMeetingCompletionInformation.query.filter(
                ProgressMeetingCompletionInformation.num_progress_meeting == selectEntry.current_meeting_number_mentor,
                ProgressMeetingCompletionInformation.select_id == selectEntry.id
            ).first()
            if completionInfoMentor == None: 
                #if there is no existing meeting notes for this meeting
                completionInfo = ProgressMeetingCompletionInformation(
                    num_progress_meeting = selectEntry.current_meeting_number_mentor,
                    select_id = selectEntry.id,
                    mentor_meeting_notes = meetingNotes
                )
                db.session.add(completionInfo)
                #no meeting notes for this one, creating them for the mentor
            else:
                #if there are existing meeting notes, update meeting notes
                #meeting notes already exist, setting mentor notes here
                completionInfoMentor.set_meeting_notes(meetingNotes, "mentor")
                completionInfoMentor.set_completion_timestamp("mentor") #update timestamp

            selectEntry.inc_current_meeting_ID("mentor") #increment the meeting number
            db.session.commit()