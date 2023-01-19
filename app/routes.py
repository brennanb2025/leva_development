#This file is the python flask backend
from flask import request, render_template, flash, redirect, url_for, session, make_response, send_from_directory
from app import app, db, s3_client#, oauth
#import lm as well?^
from app.input_sets.forms import LoginForm, EditPasswordForm, RegistrationForm
from uuid import uuid4
from app.input_sets.models import User, Tag, InterestTag, EducationTag, School, CareerInterest, \
        CareerInterestTag, Select, Business, Event, ProgressMeeting, ProgressMeetingCompletionInformation
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
import datetime
import random as rd
import re
import os
from flask_wtf.csrf import CSRFError
import datetime
import boto3
import imghdr
#from flask_login import (
    #current_user,
    #login_required,
    #login_user,
    #logout_user,
    #LoginManager
#)
#from oauthlib.oauth2 import WebApplicationClient
import requests
from datetime import timedelta
from flask import jsonify
#from requests_oauthlib import OAuth2Session
import json

#TODO: ADD  and form.validate():   to protect forms


#search other users heuristic constants
heuristicVals = {} #how much to weight matching attributes
heuristicVals["education"] = 10     #2 matching schools - weight at +10
heuristicVals["career"] = 20        #career interest
heuristicVals["interest"] = 15      #personal interest
heuristicVals["personality"] = 5
heuristicVals["division_pref"] = 15
heuristicVals["gender_pref"] = 15

#session timeout
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours=10) #10 hours until need to resign in

#different urls that application implements
#@'s are decorators, modifies function that follows it. Creates association between URL and function.



#index page GET.
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET']) 
def index():
    return render_template('index1.html', userID=session.get('userID'))
    #return render_template('index.html', userID=session.get('userID')) (old)

@app.route('/portal')
def portal():
    return render_template('portal.html', userID=session.get('userID'))


@app.route("/admin-cac68d5c-70dd-426a-ae05-195b2565b966", methods = ['GET'])
def admin_login():
    return render_template("admin_login.html")

@app.route("/admin-cac68d5c-70dd-426a-ae05-195b2565b966", methods = ['POST'])
def admin_login_post():
    # check to see if the login credentials are correct, then
    #if username and password match...
    if str(app.config['ADMIN_PASSWORD']) == request.form.get("username") and str(app.config['ADMIN_USERNAME']) == request.form.get("password"):
        return redirect(url_for("admin_data"))
    return redirect(url_for("/index"))


@app.route("/admin-data", methods = ['GET'])
def admin_data():
    if url_for('admin_login_post') in request.referrer: #did it come from admin login page?
        data = {
            "num_users": 94,
            "server_uptime": "3 years",
            "event": str(Event.query.count())
        }
        return render_template("admin.html", data=jsonify(data))
    else:
        return redirect(url_for("index"))


@app.route('/mentor')
def mentor():
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))

    user = User.query.filter_by(id=session.get('userID')).first()

    if Select.query.filter_by(mentee_id=user.id).first() != None or Select.query.filter_by(mentor_id=user.id).first() != None:
        #user already selected a mentor
        return render_template('mentor.html', isStudent=user.is_student, userID=session.get('userID'), find_match=False)
    
    return render_template('mentor.html', isStudent=user.is_student, userID=session.get('userID'), find_match=True)

@app.route('/progress', methods=['GET'])
def progress():
    
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))

    user = User.query.filter_by(id=session.get('userID')).first()
    
    isMentee = user.is_student #user.is_mentee
    currentMeetingNumber = -1 #current meeting number

    select_mentor_mentee = None #the mentor or mentee that the user logged in has selected, or None
    if isMentee: 
        selectEntry = Select.query.filter_by(mentee_id=user.id).first() #the entry of the mentor-mentee selection, or None
        if selectEntry != None:
            select_mentor_mentee = User.query.filter_by(id=selectEntry.mentor_id).first()
            currentMeetingNumber = selectEntry.current_meeting_number_mentee
    else:
        selectEntry = Select.query.filter_by(mentor_id=user.id).first()
        if selectEntry != None:
            select_mentor_mentee = User.query.filter_by(id=selectEntry.mentee_id).first()
            currentMeetingNumber = selectEntry.current_meeting_number_mentor

    #selectEntry is the database entry for this user's select. It will be None if this user hasn't been selected/hasn't yet selected.

    progressDone = False

    futureMeetingInfo = [] #future meeting list of info dicts
    prevMeetingInfo = [] #previous meeting list of info dicts
    currMeetingInfo = {} #current meeting info dict
    if selectEntry != None and currentMeetingNumber != -1:
        currMeeting = ProgressMeeting.query.filter(ProgressMeeting.business_ID==user.business_id, \
                ProgressMeeting.num_meeting==currentMeetingNumber).first()
        if currMeeting != None:
            currMeetingInfo = getMeetingInfo(currMeeting)
        else:
            progressDone = True

        previousMeetings = ProgressMeeting.query.filter(ProgressMeeting.business_ID==user.business_id, \
                ProgressMeeting.num_meeting < currentMeetingNumber).all()
        futureMeetings = ProgressMeeting.query.filter(ProgressMeeting.business_ID==user.business_id, \
                ProgressMeeting.num_meeting > currentMeetingNumber).all()
        
        for m in previousMeetings: #build the dicts of the info about each meeting
            prevMeetingInfo.append(getCompletedMeetingInfo(m, isMentee, selectEntry.id, m.num_meeting))
        for m in futureMeetings:
            futureMeetingInfo.append(getMeetingInfo(m))

    logData(15,"")

    
    return render_template('progress.html', selectEntry=selectEntry, isMentee=isMentee, \
            selectMentorMentee=select_mentor_mentee, userID=user.id, progressDone=progressDone, \
            currMeetingInfo=currMeetingInfo, prevMeetingInfo=prevMeetingInfo, futureMeetingInfo=futureMeetingInfo)


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

@app.route('/progress', methods=['POST'])
def currentMeetingSetDone():
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))
    
    user = User.query.filter_by(id=session.get('userID')).first()
    isMentee = user.is_student #user.is_mentee

    form = request.form

    if isMentee: 
        selectEntry = Select.query.filter_by(mentee_id=user.id).first() #the entry of the mentor-mentee selection, or None
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
                    mentee_meeting_notes = form.get("meetingNotes")
                )
                db.session.add(completionInfo)
                #no meeting notes for this one, creating them for the mentee
            else:
                #update meeting notes
                #meeting notes already exist, setting mentee notes here
                completionInfoMentee.set_meeting_notes(form.get("meetingNotes"), "mentee")
                completionInfoMentee.set_completion_timestamp("mentee") #update timestamp

            selectEntry.inc_current_meeting_ID("mentee") #increment the meeting number
            db.session.commit()

    else:
        selectEntry = Select.query.filter_by(mentor_id=user.id).first()
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
                    mentor_meeting_notes = form.get("meetingNotes")
                )
                db.session.add(completionInfo)
                #no meeting notes for this one, creating them for the mentor
            else:
                #if there are existing meeting notes, update meeting notes
                #meeting notes already exist, setting mentor notes here
                completionInfoMentor.set_meeting_notes(form.get("meetingNotes"), "mentor")
                completionInfoMentor.set_completion_timestamp("mentor") #update timestamp

            selectEntry.inc_current_meeting_ID("mentor") #increment the meeting number
            db.session.commit()

    return progress() #send to progress page



#sign-in page GET.
@app.route('/sign-in', methods=['GET'])
def sign_in():

    if userLoggedIn(): #valid session token -- user already logged in
        return redirect(url_for('view', id=session['userID']))

    form = LoginForm()
    title="Sign in"

    return render_template('sign_in.html', form=form, title=title)

#sign-in page POST. Checks each input from the form. 
# If the user correctly inputs their information, makes a new cookie and adds the user to the session. Then sends them to the view GET.
@app.route('/sign-in', methods=['POST'])
def sign_inPost():

    form1 = request.form 
    
    success = True
    if form1.get('email') == "": #no email entered
        success = False
        flash(u'Please enter an email', 'emailError')
    if form1.get('password') == "": #no password entered
        flash(u'Please enter a password', 'passwordError')
        success = False
    if success: #they entered an email and password - now check them
        if User.query.filter_by(email=form1.get('email')).first() == None: #email entered but not found
            success = False
            flash(u'User does not exist. If you are a new user, click the "Make an Account" button below.', 'emailError')
        elif not User.query.filter_by(email=form1.get('email')).first().check_password(form1.get('password')): #email and password do not match
            flash(u'Incorrect password', 'passwordError')
            success = False
    if success: 
        user = User.query.filter_by(email=form1.get('email')).first()
        id = user.id
        resp = make_response(redirect(url_for('view', id=id))) #get view should send to main page
        resp.set_cookie('userID', str(id))

        session["userID"] = id
        #newToken = SessionTokens(sessionID=sessionToken) #make a new token
        #db.session.add(newToken) #add to database
        logData(4,"") #log in post success
        return resp
    else:
        logData(3,"") #log in post failure
        return redirect(url_for('sign_in')) #failure


#ensures that the image is valid.
def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

#register GET. Creates a registration form and passes popular tags as suggestions.
@app.route('/register', methods=['GET'])
def register():

    #publicVisitorIP = request.remote_addr #no host proxy

    # Attempts to register an email/password pair.
    form = RegistrationForm()

    if userLoggedIn():
        return redirect(url_for('view', id=session.get('userID')))

    interestTags, careerInterests, schools = get_popular_tags()

    resp = make_response(render_template('register1.html', interestTags=interestTags, careerInterests=careerInterests, schools=schools, 
            interestList=list(), educationList=list(), careerInterestList=list(), form=form))
    #return render_template('register_first_access.html', interestTags=interestTags, careerInterests=careerInterests, schools=schools, form=form)

    resp.set_cookie('initialTimestampGET', str(datetime.datetime.utcnow())) #record the current time as a string

    logData(0,"") #log data: register get

    return resp #return the template with the cookie

#returns (tags, careerInterests, schools) - the 500 most used tags from each category.
def get_popular_tags(): 
    tags = Tag.query.order_by(Tag.num_use.desc()).limit(500).all() #sort by num_use and limit to 200
    carInts = CareerInterest.query.order_by(CareerInterest.num_use.desc()).limit(500).all()
    schools = School.query.order_by(School.num_use.desc()).limit(500).all()
    return (tags, carInts, schools)


#post register page 1
@app.route('/register/validate/1', methods=['POST'])
def registerValidate1():
    #email checking

    errors = {}
    success = True

    email = request.json['email'] 
    
    if email == '':
        success = False
        errors["email"] = 'Please enter an email.'
    else:
        """regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$' #if it isn't a valid email address
        if(not(re.search(regex,email))):
            success = False
            errors["email"] = 'Invalid email address'"""
        #commented out to allow weird email addresses

        if User.query.filter_by(email=email).first() != None: #email taken
            success = False
            errors["email"] = 'Email taken. Please enter a different email.'

    return json.dumps({
            'success':success,
            'errors':json.dumps(errors)
        })


#post register page 2
@app.route('/register/validate/2', methods=['POST'])
def registerValidate2():
    #email checking

    errors = {}
    success = True

    business = request.json['business'] 
    
    if business == '':
        success = False
        errors["business"] = 'Please enter a business.'
    else:
        businessRegisteredUnder = Business.query.filter_by(name=business).first()
        if businessRegisteredUnder == None: #business doesn't exist in database
            success = False
            errors["business"] = 'The entered business is not registered.'
        else:
            if businessRegisteredUnder.number_employees_maximum == businessRegisteredUnder.number_employees_currently_registered:
                #every spot is taken in this business. 
                success = False
                errors["business"] = 'The entered business has no spots left for more users.'

    return json.dumps({
            'success':success,
            'errors':json.dumps(errors)
        })



#register POST. Checks form input. If it is correctly input, creates a new user. Then sends them to the sign-in page.
#Current file size limited to 5 MB.
@app.route('/register', methods=['POST'])
def registerPost():

    form1 = request.form   
    
    success = True

    if form1.get("radio_mentor_mentee") == "mentee":
        isMentee = True
    else: #== "mentor"
        isMentee = False

    (success, errors) = checkBasicInfo(form1)

    if int(form1.get('num_tags')) == 0:
        success = False
        flash(u'Please enter at least one interest.', 'interestError')
        errors.append("num_tags")

    if int(form1.get('num_education_listings')) == 0:
        success = False
        flash(u'Please enter at least one school.', 'educationError')
        errors.append("num_education_listings")

    if int(form1.get('num_career_interests')) == 0:
        success = False
        flash(u'Please enter at least one career interest.', 'careerInterestError')
        errors.append("num_career_interests")

    if form1.get('radio_contact') == 'Phone number' and form1.get('phoneNumber') == "": #user chose to be contacted by phone
        flash(u'Your phone number cannot be empty.', 'phoneError')
        success = False

    if isMentee == None:
        success = False

    if str(app.config['MATCHING_FLAG_MENTOR_GENDER_PREFERENCE']) == "True": #if gender preference should be taken into account, check it.
        if isMentee and form1.get("radio_gender_preference") == None: #mentee and mentor preference empty
            flash(u"Please enter a preference for your mentor's gender.", 'mentor_preference_error')
            success = False
        if not isMentee and form1.get("radio_gender_identity") == None: #mentor and gender identity not entered
            flash(u"Please enter your gender identity.", 'gender_identity_error')
            success = False
    
    if str(app.config['MATCHING_FLAG_DIVISION_PREFERENCE']) == "True": #if division preference should be taken into account, check it.
        if form1.get("divisionPreference") == None: #mentee and mentor division preference empty or mentor and mentee division preference empty
            flash(u"Please enter a preference for your division.", 'division_preference_error')
            success = False

    if str(app.config['MATCHING_FLAG_PERSONALITY']) == "True": #if personality should be taken into account, check it.
        if form1.get('personality1') != None and form1.get('personality2') != None and form1.get('personality3') != None:
            if form1.get('personality1').strip() == "" or form1.get('personality2').strip() == "" or form1.get('personality3').strip() == "":
                flash(u"Please enter three words or phrases that describe you.", 'personality_error')
                success = False
        else:
            flash(u"Please enter three words or phrases that describe you.", 'personality_error')
            success = False


    if form1.get('current_occupation') == '':
        success = False
        flash(u'Please enter your current occupation.', 'currentOccupationError')
        errors.append("current_occupation")


    if form1.get('business') == '' or form1.get('business') == None:
        success = False
        flash(u'Please enter the company you are a part of.', 'businessError')
    else:
        businessRegisteredUnder = Business.query.filter_by(name=form1.get('business')).first()
        if businessRegisteredUnder == None: #business doesn't exist in database
            success = False
            flash(u'That business is not registered.', 'businessError') 
        else:
            if businessRegisteredUnder.number_employees_maximum == businessRegisteredUnder.number_employees_currently_registered:
                #every spot is taken in this business. 
                success = False
                flash(u'That business has no spots left for more users.', 'businessError')

    #resume pdf
    if "resume" in request.files and request.files["resume"]:
        resume = request.files["resume"]
        #remove cropping
        #if img and int((img.getbuffer().nbytes/1024)/1024) > 5:

        resumeSize = -1
        if resume:
            resume.seek(0, os.SEEK_END)
            resumeSize = resume.tell()
            resume.seek(0)
        
        if resumeSize == -1:
            flash(u"Couldn't read resume.", 'resumeError')
            success = False
        elif (resumeSize/1024)/1024 > 5:
            flash(u'Resume is too big (max 5 MB).', 'resumeError')
            success = False
        elif resume.filename == '':
            flash(u'Could not read resume', 'resumeError')
            success = False
        else:
            file_ext = os.path.splitext(resume.filename)[1]
            if file_ext == None:
                success = False
                flash(u"Could not assess file type properties", 'resumeError')
            elif file_ext not in json.loads(app.config['UPLOAD_EXTENSIONS_RESUME']):
                flash(u'Accepted file type: .pdf. You uploaded a', file_ext + ".", 'resumeError')
                success = False
    #else: didn't input a resume. That's ok, they're optional.

    #if "file" in request.files and request.files["file"]:
    img = None
    errorMsg = ""

    if "croppedImgFile" in request.files and request.files.get("croppedImgFile").filename != '':
        img = request.files.get("croppedImgFile")
    
        #remove cropping
        """if int((img.getbuffer().nbytes/1024)/1024) > 5:
            flash(u'Image is too big (max 5 MB).', 'imageError')
            success = False"""


        #imgSize = -1
        #img.seek(0, os.SEEK_END)
        #imgSize = img.tell()
        #img.seek(0)
        
        """if imgSize == -1:
            errorMsg = errorMsg + "[Couldn't read image]"
            flash(u"Couldn't read image.", 'imageError')
            success = False
        elif (imgSize/1024)/1024 > 5:
            errorMsg = errorMsg + "[Image is too big (max 5 MB)]"
            flash(u'Image is too big (max 5 MB).', 'imageError')
            success = False
        el"""
        """if img.filename == '':
            errorMsg = errorMsg + "[Could not read image filename]"
            flash(u'Could not read image filename', 'imageError')
            success = False
        else:"""
        imgType = validate_image(img.stream)
        if imgType == None:
            errorMsg = errorMsg + "[Could not assess image size]"
            flash(u'Could not assess image size.', 'imageError')
        elif imgType not in json.loads(app.config['UPLOAD_EXTENSIONS']):
            errorMsg = errorMsg + "[Wrong image type]"
            flash(u'Accepted file types: .png, .jpg. You uploaded a ' + imgType + ".", 'imageError')
            success = False
    #image is optional
    """else:
        success = False
        flash(u'Please select a file.', 'pictureError')"""

    """vid = None
    if "videoFile" in request.files:
        vid = request.files["videoFile"]"""
    
    #video file optional
    """else:
        success=False
        flash(u'Please select a file.', 'videoError')"""


    """if vid:
        duration = request.form.get("videoDuration")
        if not duration:
            flash(u"Something went wrong, couldn't assess video duration. Try reuploading the video.", 'videoError')
            success = False
        elif duration == "":
            flash(u"Something went wrong, couldn't assess video duration. Try reuploading the video.", 'videoError')
            success = False
        elif float(duration) >= 30:
            flash(u'Video is too long (max duration: 30 seconds).', 'videoError')
            success = False
        
        if int((len(vid.read())/1024)/1024) > 40: #check size of file. Don't allow file sizes above 40MB.
            flash(u'Video is too big (max 40 MB).', 'videoError')
            success = False"""


    if success: #success, registering new user

        mentor_gender_preferenceForm = form1.get("radio_gender_preference")
        if not isMentee or str(app.config['MATCHING_FLAG_MENTOR_GENDER_PREFERENCE']) == "False":
            mentor_gender_preferenceForm = None #if mentor OR gender should not be taken into account, this should not be entered.

        gender_identityForm = form1.get("radio_gender_identity")
        if isMentee or str(app.config['MATCHING_FLAG_MENTOR_GENDER_PREFERENCE']) == "False":
            gender_identityForm = None #if mentee, this should not be entered.

        #changed division form to be 1:Freshman, 2:Sophomore, etc.
        division_set = form1.get('division').strip()
        if division_set == "1":
            division_set = "Freshman"
        elif division_set == "2":
            division_set = "Sophomore"
        elif division_set == "3":
            division_set = "Junior"
        else:
            division_set = "Senior"

        division_preference_set = form1.get("divisionPreference")
        if str(app.config['MATCHING_FLAG_DIVISION_PREFERENCE']) == "False":
            #if division preference should not be taken into account, set it to None
            division_preference_set = None

        personality_1_set = personality_2_set = personality_3_set = None
        if str(app.config['MATCHING_FLAG_Personality']) == "True":
            personality_1_set = form1.get("personality1").strip()
            personality_2_set = form1.get("personality2").strip()
            personality_3_set = form1.get("personality3").strip()

        businessRegisteredUnder = Business.query.filter_by(name=form1.get('business')).first()
        businessRegisteredUnder.inc_number_employees_currently_registered() #increment number of users registered for this user

        user = User(email=form1.get('email'), first_name=form1.get('first_name'), last_name=form1.get('last_name'), 
                    is_student=isMentee, bio=form1.get('bio'), email_contact=True, phone_number=None,
                    city_name=form1.get('city_name'), current_occupation=form1.get('current_occupation'),
                    business_id=businessRegisteredUnder.id, 
                    mentor_gender_preference=mentor_gender_preferenceForm,
                    gender_identity=gender_identityForm,
                    division_preference=division_preference_set, division=division_set,
                    personality_1=personality_1_set, personality_2=personality_2_set,
                    personality_3=personality_3_set)
        
        db.session.add(user) #add to database
        user.set_password(form1.get('password')) #must set pwd w/ hashing method
        db.session.commit()

        if form1.get('radio_contact') == 'Phone number': #set phone number
            user.set_phone(form1.get('phoneNumber'))

        #get interests
        #I don't actually need num_tags since I can not iterate thru getlist, 
        # but I can see it being useful/efficient for future features.
        interestArr = form1.getlist("tagName")
        for i in range(int(form1.get('num_tags'))):
            name = interestArr[i].strip()
            if name != "":
                interestTag = InterestTag(
                    user_id=user.id,
                    entered_name=name
                )
                db.session.add(interestTag)
                db.session.commit() #I have to do this before I set the resource so the id will be set.
                interestTag.set_interestID(name, db.session)

        #get education
        eduArr = form1.getlist("educationName")
        for i in range(int(form1.get('num_education_listings'))):
            name = eduArr[i].strip()
            if name != "":
                educationTag = EducationTag(
                    user_id=user.id,
                    entered_name=name
                )
                db.session.add(educationTag)
                db.session.commit() #I have to do this before I set the resource so the id will be set.
                educationTag.set_educationID(name, db.session)

        #get career interests
        cintArr = form1.getlist("careerInterestName")
        for i in range(int(form1.get('num_career_interests'))):
            name = cintArr[i].strip()
            if name != "":
                cintTag = CareerInterestTag(
                    user_id=user.id,
                    entered_name=name
                )
                db.session.add(cintTag)
                db.session.commit() #I have to do this before I set the resource so the id will be set.
                cintTag.set_careerInterestID(name, db.session)
        
        #remove cropping
        if "croppedImgFile" in request.files:
            img = request.files.get("croppedImgFile")
            if img:
                output, filename = upload_media_file_to_s3(img, user)
                user.set_profile_picture(output, filename) #set the user profile picture link
                db.session.commit()

        """if "videoFile" in request.files:
            vid = request.files["videoFile"]
            if vid:
                vid.seek(0) #I read the file before to check the length so I must put the cursor at the beginning in order to upload it.
                output, filename = upload_media_file_to_s3(vid, user)
                user.set_intro_video(output, filename) #set the user profile picture link
                db.session.commit()"""

        if "resume" in request.files:
            resume = request.files["resume"]
            if resume:
                resume.seek(0) #I read the file before to check the length so I must put the cursor at the beginning in order to upload it.
                output, filename = upload_resume_file_to_s3(resume, user)
                user.set_resume(output, filename) #set the user resume
                db.session.commit()

        db.session.commit()

        timeDiff = str(datetime.datetime.utcnow() - datetime.datetime.strptime(request.cookies.get('initialTimestampGET'), "%Y-%m-%d %H:%M:%S.%f"))
        dataDict = {}
        dataDict["registerTimeDiff"] = timeDiff
        logData(2, json.dumps(dataDict))

        resp = make_response(redirect(url_for('sign_in'))) #success: get request to sign_in page

        resp.set_cookie('initialTimestampGET', '', expires=0) #delete cookie

        return resp
    else:
        flash(u'We encountered an error registering you. Please fix any errors in the following pages.', 'generalError')
        return registerPreviouslyFilledOut(form1, errors, request)


#gets all the values from the form that was previously filled out, so that they can be sent back and autofilled into a new form.
def registerPreviouslyFilledOut(form, errors, request):

    email = form.get("email")
    first_name = form.get("first_name")
    last_name = form.get("last_name")
    bio = form.get("bio")
    email_or_phone = "email"
    phone_num = ""
    city_name = form.get("city_name")
    first_last_error = False
    current_occupation = form.get("current_occupation")
    division = form.get("division")

    if "email" in errors: #if error - make it blank.
        email = ""
    elif "first name" in errors:
        first_name = ""
    elif "city_name" in errors:
        city_name = ""
    elif "division" in errors:
        division = ""
    elif "current_occupation" in errors:
        current_occupation = ""
    elif "last name" in errors:
        last_name = ""
        if "first name" in errors:
            first_last_error = True


    register_type = form.get("radio_mentor_mentee") #student or mentor
    #^v will be none if somehow they messed with it
    if form.get('radio_contact') == 'Phone number':
        email_or_phone = "phone"
        phone_num = form.get('phoneNumber')
    
    mentorGenderIdentity = form.get("radio_gender_identity")
    menteeGenderPreference = form.get("radio_gender_preference")
    textPersonality1 = form.get("personality1")
    textPersonality2 = form.get("personality2")
    textPersonality3 = form.get("personality3")
    divisionPreference = form.get("divisionPreference")



    #get all the input attributes
    interestInputs = []
    if not "num_tags" in errors:
        interestInputs = form.getlist("tagName")

    eduInputs = []
    if not "num_education_listings" in errors:
        eduInputs = form.getlist("educationName")

    carIntInputs = []
    if not "num_education_listings" in errors:
        carIntInputs = form.getlist("careerInterestName")

    #v load the register page
    formNew = RegistrationForm()

    if userLoggedIn():
        return redirect(url_for('view', id=session.get('userID')))

    """
    Getting back data so I don't have to call to the database again -- too much data (1500 entries) to send back
    interestTags = form.getlist("interestDatalistOption")
    careerInterests = form.getlist("careerInterestDatalistOption")
    schools = form.getlist("schoolDatalistOption")
    if len(interestTags) == 0 or len(careerInterests) == 0 or len(schools) == 0:
        interestTags, careerInterests, schools = get_popular_tags()
    """
    interestTags, careerInterests, schools = get_popular_tags()

    resp = make_response(render_template('register1.html', email=email, first_name=first_name, last_name=last_name, first_last_error=first_last_error,
                bio=bio, email_or_phone=email_or_phone, city_name=city_name, current_occupation=current_occupation,
                division=division, phone_num=phone_num, register_type=register_type,
                interestList=interestInputs, educationList=eduInputs, careerInterestList=carIntInputs,
                interestTags=interestTags, careerInterests=careerInterests, schools=schools, form=formNew,
                mentorGenderIdentity=mentorGenderIdentity, menteeGenderPreference=menteeGenderPreference, textPersonality1=textPersonality1,
                textPersonality2=textPersonality2, textPersonality3=textPersonality3, divisionPreference=divisionPreference))
    
    resp.set_cookie('initialTimestampGET', request.cookies.get('initialTimestampGET')) #return with the initial time

    timeDiff = str(datetime.datetime.utcnow() - datetime.datetime.strptime(request.cookies.get('initialTimestampGET'), "%Y-%m-%d %H:%M:%S.%f"))
    dataDict = {}
    dataDict["registerTimeDiff"] = timeDiff
    dataDict["errors"] = errors
    logData(1, json.dumps(dataDict)) #log data: register post error
    

    return resp
    

#checks the basic registration information.
def checkBasicInfo(form1):
    errors = []
    success = True
    if User.query.filter_by(email=form1.get('email')).first() != None: #email taken
        success = False
        flash(u'Email taken. Please enter a different email.', 'emailError')
        errors.append("email")
    if form1.get('email') == '':
        success = False
        flash(u'Please enter an email.', 'emailError')
        errors.append("email")
    """else:
        regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$' #if it isn't a valid email address
        if(not(re.search(regex,form1.get('email')))):
            flash('Invalid email address', 'emailError')
            success = False
            errors.append("email")"""
    if form1.get('first_name') == '':
        success = False
        flash(u'Please enter a first name.', 'first_nameError')
        errors.append("first name")
    if form1.get('last_name') == '':
        success = False
        flash(u'Please enter a last name.', 'last_nameError')
        errors.append("last name")
    if form1.get('password') == '':
        success = False
        flash(u'Please enter a password.', 'passwordError')
        #errors.append("password") not used for anything - passwords are wiped anyway
    if form1.get('password2') == '':
        success = False
        flash(u'Please reenter your password.', 'password2Error')
        #errors.append("password") not used for anything - passwords are wiped anyway
    if success: #did enter everything
        if form1.get('password') != form1.get('password2'): #passwords don't match
            success = False
            flash(u'Passwords do not match.', 'password2Error')
            #errors.append("password") not used for anything - passwords are wiped anyway

    if form1.get('division') == '':
        success = False
        flash(u'Please enter your division within the company.', 'division_error')
        errors.append("division")
    
    if form1.get('city_name') == '':
        success = False
        flash(u'Please enter a city.', 'cityNameError')
        errors.append("city_name")
    
    if form1.get('num_pairings') == '':
        success = False
        flash(u'Please enter the amount of mentors/mentees you are willing to have.')
        errors.append("num_pairings")
    else:
        if form1.get('num_pairings') == '0':
            success = False
            flash(u'The number of mentors/mentees you are willing to have cannot be 0.')
            errors.append("num_pairings")
        else:
            try:
                int(form1.get('num_pairings')) #try to parse the int field
            except:
                success = False
                flash(u'The number of mentors/mentees you are willing to have must be an integer.')
                errors.append("num_pairings")

    if form1.get('bio') == '':
        success = False
        flash(u'Your bio cannot be empty.', 'bioError')
        errors.append("bio")
    return (success, errors)



# edit-profile GET. Readies edit profile forms and user information.
@app.route('/edit-profile', methods = ['GET'])
def editProfile():

    if not userLoggedIn():
        return redirect(url_for('sign_in'))

    user = User.query.filter_by(id=session.get('userID')).first() #get the correct profile by inputting user id

    formPwd = EditPasswordForm()

    interestList = []
    for interest in user.rtn_interests():
        #interestList.append(Tag.query.filter_by(tagID=interest.interestID).first().title)
        interest = Tag.query.filter_by(id=interest.interestID).first()
        if interest != None:
            interestList.append(interest.title)
    careerInterestList = []
    for cint in user.rtn_career_interests():
        #careerInterestList.append(CareerInterest.query.filter_by(careerInterestID=cint.careerInterestID).first().title)
        cint = CareerInterest.query.filter_by(id=cint.careerInterestID).first()
        if cint != None:
            careerInterestList.append(cint.title)
    educationList = []
    for school in user.rtn_education():
        #educationList.append(School.query.filter_by(schoolID=school.educationID).first().title)
        edu = School.query.filter_by(id=school.educationID).first()
        if edu != None:
            educationList.append(edu.title)
    bio = user.bio

    prof_pic_link = user.profile_picture
    intro_video_link = user.intro_video
    contact_method = user.email_contact
    phone_num = user.phone_number
    personality_1 = user.personality_1
    personality_2 = user.personality_2
    personality_3 = user.personality_3

    mentorGenderPreference = user.mentor_gender_preference
    if mentorGenderPreference != None:
        if mentorGenderPreference == "male":
            mentorGenderPreference = "Male mentor"
        elif mentorGenderPreference == "female":
            mentorGenderPreference = "Female mentor"
        else:
            mentorGenderPreference = "No preference"

    divisionPreference = user.division_preference
    if divisionPreference != None:
        if divisionPreference == "same":
            divisionPreference = "Same division"
        elif divisionPreference == "different":
            divisionPreference = "Different division"
        else:
            divisionPreference = "No preference"

    genderIdentity = user.gender_identity
    if genderIdentity != None:
        if genderIdentity == "male":
            genderIdentity = "Male"
        elif genderIdentity == "female":
            genderIdentity = "Female"
        elif genderIdentity == "nonbinaryNonconforming":
            genderIdentity = "Non-binary/non-conforming"
        else:
            genderIdentity = "Prefer not to respond"

    interestTags, careerInterests, schools = get_popular_tags()

    resumeUrl = create_resume_link(user)

    logData(5,"") #log data edit profile get

    title="Edit profile Page"
    #return render_template('edit_profile.html', intro_video=intro_video_link, 
    #return render_template('editProfileNew.html', intro_video=intro_video_link, 
    return render_template('edit_profile_revised.html', intro_video=intro_video_link, 
            contact_method=contact_method, phone_num=phone_num, profile_picture=prof_pic_link, 
            interestTags=interestTags, careerInterests=careerInterests, schools=schools, 
            title=title, bio=bio, interestList=interestList, careerInterestList=careerInterestList, educationList=educationList, 
            personality_1=personality_1, personality_2=personality_2, personality_3=personality_3, division=user.division,
            resumeUrl=resumeUrl, divisionPreference=divisionPreference,
            mentorGenderPreference=mentorGenderPreference, genderIdentity=genderIdentity,
            formPwd=formPwd, 
            user=user, userID=session.get('userID'))

"""@app.route('/edit-profile-test', methods=['GET'])
def editProfileTest():
    if not userLoggedIn():
        return redirect(url_for('sign_in'))

    user = User.query.filter_by(id=session.get('userID')).first() #get the correct profile by inputting user id

    formPwd = EditPasswordForm()

    interestList = []
    for interest in user.rtn_interests():
        #interestList.append(Tag.query.filter_by(tagID=interest.interestID).first().title)
        interest = Tag.query.filter_by(id=interest.interestID).first()
        if interest != None:
            interestList.append(interest.title)
    careerInterestList = []
    for cint in user.rtn_career_interests():
        #careerInterestList.append(CareerInterest.query.filter_by(careerInterestID=cint.careerInterestID).first().title)
        cint = CareerInterest.query.filter_by(id=cint.careerInterestID).first()
        if cint != None:
            careerInterestList.append(cint.title)
    educationList = []
    for school in user.rtn_education():
        #educationList.append(School.query.filter_by(schoolID=school.educationID).first().title)
        edu = School.query.filter_by(id=school.educationID).first()
        if edu != None:
            educationList.append(edu.title)
    bio = user.bio

    prof_pic_link = user.profile_picture
    intro_video_link = user.intro_video
    contact_method = user.email_contact
    phone_num = user.phone_number
    personality_1 = user.personality_1
    personality_2 = user.personality_2
    personality_3 = user.personality_3

    mentorGenderPreference = user.mentor_gender_preference
    if mentorGenderPreference != None:
        if mentorGenderPreference == "male":
            mentorGenderPreference = "Male mentor"
        elif mentorGenderPreference == "female":
            mentorGenderPreference = "Female mentor"
        else:
            mentorGenderPreference = "No preference"

    divisionPreference = user.division_preference
    if divisionPreference != None:
        if divisionPreference == "same":
            divisionPreference = "Same division"
        elif divisionPreference == "different":
            divisionPreference = "Different division"
        else:
            divisionPreference = "No preference"

    genderIdentity = user.gender_identity
    if genderIdentity != None:
        if genderIdentity == "male":
            genderIdentity = "Male"
        elif genderIdentity == "female":
            genderIdentity = "Female"
        elif genderIdentity == "nonbinaryNonconforming":
            genderIdentity = "Non-binary/non-conforming"
        else:
            genderIdentity = "Prefer not to respond"

    interestTags, careerInterests, schools = get_popular_tags()

    resumeUrl = create_resume_link(user)

    logData(5,"") #log data edit profile get

    title="Edit profile Page"
    #return render_template('edit_profile.html', intro_video=intro_video_link, 
    return render_template('edit_profile_revised.html', intro_video=intro_video_link, 
            contact_method=contact_method, phone_num=phone_num, profile_picture=prof_pic_link, 
            interestTags=interestTags, careerInterests=careerInterests, schools=schools, 
            title=title, bio=bio, interestList=interestList, careerInterestList=careerInterestList, educationList=educationList, 
            personality_1=personality_1, personality_2=personality_2, personality_3=personality_3, division=user.division,
            resumeUrl=resumeUrl, divisionPreference=divisionPreference,
            mentorGenderPreference=mentorGenderPreference, genderIdentity=genderIdentity,
            formPwd=formPwd, 
            user=user, userID=session.get('userID'))"""

@app.route('/edit-profile', methods = ['POST'])
def editProfilePost():

    if not userLoggedIn():
        return redirect(url_for('sign_in'))

    form = request.form

    if form.get("submitBtn") == "editResume": #different types of submissions
        editProfResume()
    elif form.get("submitBtn") == "deleteResume":
        deleteResume()

    success = True
    u = User.query.filter_by(id=session['userID']).first()

    changedFnSuccess = False #init as false in case they didn't change it
    if form.get("first_name") != u.first_name: #changed first name --> check it
        changedFnSuccess=checkFirstName(form)
        if not changedFnSuccess: #changed first name unsuccessful.
            success = False

    changedLnSuccess = False #init as false in case they didn't change it
    if form.get("last_name") != u.last_name: #changed last name --> check it
        changedLnSuccess=checkLastName(form)
        if not changedLnSuccess: #change unsuccessful.
            success = False

    changedCitySuccess = False #init as false in case they didn't change it
    if form.get("city_name") != u.city_name: #changed city name --> check it
        changedCitySuccess=checkCityName(form)
        if not changedCitySuccess: #change unsuccessful.
            success = False
    
    changedOccupationSuccess = False #init as false in case they didn't change it
    if form.get("current_occupation") != u.current_occupation: #changed current occupation --> check it
        changedOccupationSuccess=checkCityName(form)
        if not changedOccupationSuccess: #change unsuccessful.
            success = False

    changedBioSuccess = False #init as false in case they didn't change it
    if form.get("bio") != u.bio: #changed bio --> check it
        changedBioSuccess=checkBio(form)
        if not changedBioSuccess: #change unsuccessful.
            success = False
    
    changedMentorGenderSuccess = False
    if u.is_student and form.get("radio_gender_preference") != None:
        #ensuring that this form actually exists
        if form.get("radio_gender_preference") != u.mentor_gender_preference: #changed preference --> check it
            changedMentorGenderSuccess=checkMentorGenderPreference(form)
            if not changedMentorGenderSuccess: #change unsuccessful.
                success = False

    changedGenderIdentitySuccess = False
    if not u.is_student and form.get("radio_gender_identity") != None:
        if form.get("radio_gender_identity") != u.gender_identity: #changed gender identity --> check it
            changedGenderIdentitySuccess=checkGenderIdentity(form)
            if not changedGenderIdentitySuccess: #change unsuccessful.
                success = False
            
    changedInputsSuccess = False
    if form.get("changedAttributes") == "True": #changed attributes --> check them
        changedInputsSuccess=checkAttributes(form, u.is_student)
        if not changedInputsSuccess: #change unsuccessful.
            success = False
    
    changedPersonalitySuccess = False
    if form.get("personality1") != u.personality_1 or form.get("personality2") != u.personality_2 or form.get("personality3") != u.personality_3: #changed --> check it
        changedPersonalitySuccess=checkPersonality(form)
        if not changedPersonalitySuccess: #change unsuccessful.
            success = False
    
    changedDivisionSuccess = False
    if form.get("division") != u.division: #changed --> check it
        changedDivisionSuccess=checkDivision(form)
        if not changedDivisionSuccess: #change unsuccessful.
            success = False
    
    changedDivisionPreferenceSuccess = False
    if form.get("divisionPreference") != u.division_preference: #changed --> check it
        changedDivisionPreferenceSuccess=checkDivisionPreference(form, u.is_student)
        if not changedDivisionPreferenceSuccess: #change unsuccessful.
            success = False

    changedContactMethodSuccess = False
    if form.get("radio_contact") == "Phone number" and u.email_contact \
                or form.get("radio_contact") == "Email" and not u.email_contact: #changed --> check it
        changedContactMethodSuccess=checkContactPreference(form)
        if not changedContactMethodSuccess: #change unsuccessful.
            success = False

    if success:
        #set here
        if changedFnSuccess:
            u.set_first_name(form.get("first_name"))
        if changedLnSuccess:
            u.set_last_name(form.get("last_name"))
        if changedCitySuccess:
            u.set_city_name(form.get("city_name"))
        if changedOccupationSuccess:
            u.set_current_occupation(form.get("current_occupation"))
        if changedBioSuccess:
            u.set_bio(form.get("bio"))
        if changedMentorGenderSuccess:
            u.set_mentor_gender_preference(form.get("radio_gender_preference"))
        if changedGenderIdentitySuccess:
            u.set_gender_identity(form.get("radio_gender_identity"))
        if changedInputsSuccess:
            changeAttributes(form,u)
        if changedPersonalitySuccess:
            u.set_personality(form.get('personality1').strip(), form.get('personality2').strip(), form.get('personality3').strip())
        if changedDivisionSuccess:
            u.set_division(form.get("division").strip())
        if changedDivisionPreferenceSuccess:
            u.set_division_preference(form.get("divisionPreference"))
        if changedContactMethodSuccess:
            if form.get('radio_contact') == 'Email': #checked the email box
                u.remove_phone()
            if form.get('radio_contact') == 'Phone number':
                u.set_phone(form.get('phoneNumber'))
        
        db.session.commit()

        dataChangedDict = {}
        dataChangedDict["fn"] = changedFnSuccess
        dataChangedDict["ln"] = changedLnSuccess
        dataChangedDict["city"] = changedCitySuccess
        dataChangedDict["occupation"] = changedOccupationSuccess
        dataChangedDict["bio"] = changedBioSuccess
        dataChangedDict["mentorGender"] = changedMentorGenderSuccess
        dataChangedDict["genderIdentity"] = changedGenderIdentitySuccess
        dataChangedDict["attributes"] = changedInputsSuccess
        dataChangedDict["personality"] = changedPersonalitySuccess
        dataChangedDict["division"] = changedDivisionSuccess
        dataChangedDict["divisionPref"] = changedDivisionPreferenceSuccess
        dataChangedDict["contact"] = changedContactMethodSuccess
        
        logData(7,json.dumps(dataChangedDict)) #log data edit profile success

        return redirect(url_for('view', id=session.get('userID')))
    else: 
        dataChangedDict = {}
        dataChangedDict["fn"] = changedFnSuccess
        dataChangedDict["ln"] = changedLnSuccess
        dataChangedDict["city"] = changedCitySuccess
        dataChangedDict["occupation"] = changedOccupationSuccess
        dataChangedDict["bio"] = changedBioSuccess
        dataChangedDict["mentorGender"] = changedMentorGenderSuccess
        dataChangedDict["genderIdentity"] = changedGenderIdentitySuccess
        dataChangedDict["attributes"] = changedInputsSuccess
        dataChangedDict["personality"] = changedPersonalitySuccess
        dataChangedDict["division"] = changedDivisionSuccess
        dataChangedDict["divisionPref"] = changedDivisionPreferenceSuccess
        dataChangedDict["contact"] = changedContactMethodSuccess
        logData(6,json.dumps(dataChangedDict)) #log data edit profile error
        return redirect(url_for('editProfile'))

def checkFirstName(form):
    if form.get("first_name") == '':
        flash(u'Please enter a new first name.', 'firstNameError')
        return False
    else:
        return True

def checkLastName(form):
    if form.get("last_name") == '':
        flash(u'Please enter a new last name.', 'lastNameError')
        return False
    else:
        return True

def checkCityName(form):
    if form.get("city_name") == '':
        flash(u'Please enter a new city name.', 'cityNameError')
        return False
    else:
        return True

def checkCurrentOccupationName(form):
    if form.get("current_occupation") == '':
        flash(u'Please enter a new current occupation.', 'currentOccupationError')
        return False
    else:
        return True

def checkMentorGenderPreference(form):
    if form.get("radio_gender_preference") == None or form.get("radio_gender_preference") == '': #preference empty
        flash(u"Please enter a preference for your mentor's gender.", 'mentor_preference_error')
        return False
    else:
        return True

def checkGenderIdentity(form):
    if form.get("radio_gender_identity") == None or form.get("radio_gender_identity") == '': #empty
        flash(u"Please enter your gender identity.", 'gender_identity_error')
        return False
    else:
        return True

def checkBio(form):
    if form.get("bio") == '': #bio empty
        flash(u'Your bio cannot be empty.', 'bioError')
        return False
    else:
        return True

def checkAttributes(form, isMentee):
    if int(form.get('num_tags')) == 0:
        flash(u'Please enter at least one interest.', 'interestError')
        return False

    if int(form.get('num_education_listings')) == 0:
        flash(u'Please enter at least one school.', 'educationError')
        return False

    if int(form.get('num_career_interests')) == 0:
        if isMentee:
            flash(u'Please enter at least one career interest.', 'careerInterestError')
        else:
            flash(u'Please enter at least one career experience.', 'careerInterestError')
        return False
    return True
def changeAttributes(form, user):
    #I want to register the new attributes - delete the old ones.
    delete_user_attributes(user.id)

    #get interests
    #I don't actually need num_tags since I can iterate thru getlist, 
    # but I can see it being useful/efficient for future features.
    #ok I'm just going to iterate through the list to protect against index out of bounds exceptions
    interestArr = form.getlist("tagName")
    #for i in range(int(form1.get('num_tags'))):
    for i in range(len(interestArr)):
        name = interestArr[i].strip()
        if name != "":
            interestTag = InterestTag(
                user_id=user.id,
                entered_name=name
            )
            db.session.add(interestTag)
            db.session.commit() #I have to do this before I set the resource so the id will be set.
            interestTag.set_interestID(name, db.session)

    #get education
    eduArr = form.getlist("educationName")
    #for i in range(int(form1.get('num_education_listings'))):
    for i in range(len(eduArr)):
        name = eduArr[i].strip()
        if name != "":
            educationTag = EducationTag(
                user_id=user.id,
                entered_name=name
            )
            db.session.add(educationTag)
            db.session.commit() #I have to do this before I set the resource so the id will be set.
            educationTag.set_educationID(name, db.session)

    #get career interests
    cintArr = form.getlist("careerInterestName")
    #for i in range(int(form1.get('num_career_interests'))):
    for i in range(len(cintArr)):
        name = cintArr[i].strip()
        if name != "":
            cintTag = CareerInterestTag(
                user_id=user.id,
                entered_name=name
            )
            db.session.add(cintTag)
            db.session.commit() #I have to do this before I set the resource so the id will be set.
            cintTag.set_careerInterestID(name, db.session)

    db.session.commit()

def checkPersonality(form):
    if form.get('personality1') != None and form.get('personality2') != None and form.get('personality3') != None:
        if form.get('personality1').strip() == "" or form.get('personality2').strip() == "" or form.get('personality3').strip() == "":
            flash(u'You must input 3 personality traits/phrases.', 'personalityError')
            return False
    else:
        flash(u'You must input 3 personality traits/phrases.', 'personalityError')
        return False

    return True

def checkDivision(form):
    if form.get('division').strip() == "":
        flash(u'You must input what division you are in.', 'divisionError')
        return False
    return True

def checkDivisionPreference(form, isMentee):
    if form.get("divisionPreference") == None and form.get("divisionPreference") != "": 
        #mentee and mentor division preference empty or mentor and mentee division preference empty
        if isMentee:
            flash(u"Please enter a preference for your mentor's division.", 'divisionPreferenceError')
        else:
            flash(u"Please enter a preference for your mentee's division.", 'divisionPreferenceError')
        return False
    return True

def checkContactPreference(form):
    if form.get('radio_contact') == 'Phone number' and form.get('phoneNumber') == "": #user chose to be contacted by phone
        flash(u'Your phone number cannot be empty.', 'phoneError')
        return False

    if form.get('radio_contact') != 'Email' and form.get('radio_contact') != 'Phone number': #somehow removed the check
        return False
    
    return True



#edit-profile-password POST.
#changes the user's password if it is input correctly. Then sends the user back to view.
@app.route('/edit-profile-password', methods = ['POST'])
def editProfilePassword():

    if not userLoggedIn():
        return redirect(url_for('sign_in'))
    
    form = request.form

    success = True

    if form.get('password') == '':
        success = False
        flash(u'Please enter a password.', 'passwordError')
    if form.get('password2') == '':
        success = False
        flash(u'Please reenter your password.', 'password2Error')
    if success: #did enter everything
        if form.get('password') != form.get('password2'): #passwords don't match
            success = False
            flash(u'Passwords do not match.', 'password2Error')

    if success:
        User.query.filter_by(id=session['userID']).first().set_password(form.get('password')) #set hashed pwd
        db.session.commit()
        return redirect(url_for('view', id=session.get('userID')))
    else: 
        return redirect(url_for('editProfile'))

@app.route('/edit-profile-picture', methods=['POST'])
def editProfPic():
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))

    img = None
    success = True
    errorMsg = ""
    
    if "croppedImgFile" in request.files:
        img = request.files.get("croppedImgFile")
    else:
        success=False
        errorMsg += "[Please select a file]"
        flash(u'Please select a file.', 'pictureError')
    
    if img:
        #remove cropping
        """if int((img.getbuffer().nbytes/1024)/1024) > 5:
            flash(u'Image is too big (max 5 MB).', 'imageError')
            success = False"""


        #imgSize = -1
        #img.seek(0, os.SEEK_END)
        #imgSize = img.tell()
        #img.seek(0)
        
        """if imgSize == -1:
            errorMsg = errorMsg + "[Couldn't read image]"
            flash(u"Couldn't read image.", 'imageError')
            success = False
        elif (imgSize/1024)/1024 > 5:
            errorMsg = errorMsg + "[Image is too big (max 5 MB)]"
            flash(u'Image is too big (max 5 MB).', 'imageError')
            success = False
        el"""
        if img.filename == '':
            errorMsg = errorMsg + "[Could not read image filename]"
            flash(u'Could not read image', 'imageError')
            success = False
        else:
            imgType = validate_image(img.stream)
            if imgType == None:
                errorMsg = errorMsg + "[Could not assess image size]"
                flash(u'Could not assess image size.', 'imageError')
            elif imgType not in json.loads(app.config['UPLOAD_EXTENSIONS']):
                errorMsg = errorMsg + "[Wrong image type]"
                flash(u'Accepted file types: .png, .jpg. You uploaded a ' + imgType + ".", 'imageError')
                success = False
    else:
        errorMsg = errorMsg + "[Image could not be found]"
        flash(u'Image could not be found.', 'imageError')
        success = False
    
    if success: 
        if img:
            user = User.query.filter_by(id=session.get('userID')).first()
            delete_profile_picture(user)
            output, filename = upload_media_file_to_s3(img, user)
            user.set_profile_picture(output, filename) #set the user profile picture link
            db.session.commit()
        else:
            flash(u'Please select a file.', 'pictureError')
    else:
        logData(18,errorMsg)

    return redirect(url_for('editProfile'))


@app.route('/delete-profile-picture', methods=['POST'])
def deleteProfPic():
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))
    
    user = User.query.filter_by(id=session.get('userID')).first()
    delete_profile_picture(user)

    return redirect(url_for('editProfile'))

"""
@app.route('/delete-intro-video', methods=['POST'])
def deleteIntroVid():
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))
    
    user = User.query.filter_by(id=session.get('userID')).first()
    delete_intro_video(user)

    return redirect(url_for('editProfile'))
"""

#@app.route('/delete-resume', methods=['POST'])
def deleteResume():
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))
    
    user = User.query.filter_by(id=session.get('userID')).first()

    delete_resume(user)

    return redirect(url_for('editProfile'))

"""
@app.route('/edit-video', methods=['POST'])
def editVideo():
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))

    vid = None
    success = True
    if "videoFile" in request.files:
        vid = request.files["videoFile"]
    else:
        success=False
        flash(u'Please select a file.', 'videoError')
    if vid:
        duration = request.form.get("videoDuration")
        if not duration:
            flash(u"Something went wrong, couldn't assess video duration. Try reuploading the video.", 'videoError')
            success = False
        elif duration == "":
            flash(u"Something went wrong, couldn't assess video duration. Try reuploading the video.", 'videoError')
            success = False
        elif float(duration) >= 30:
            flash(u'Video is too long (max duration: 30 seconds).', 'videoError')
            success = False
        
        if int((len(vid.read())/1024)/1024) > 40: #check size of file. Don't allow file sizes above 40MB.
            flash(u'Video is too big (max 40 MB).', 'videoError')
            success = False
    else:
        flash(u'Please select a file.', 'videoError')
        success = False
    
    if success:
        user = User.query.filter_by(id=session.get('userID')).first()
        delete_intro_video(user)
        vid.seek(0) #I read the file before to check the length so I must put the cursor at the beginning in order to upload it.
        output, filename = upload_media_file_to_s3(vid, user)
        user.set_intro_video(output, filename) #set the user profile picture link
        db.session.commit()

    return redirect(url_for('editProfile'))
"""

#@app.route('/edit-profile-resume', methods=['POST'])
def editProfResume():
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))

    success = True

    user = User.query.filter_by(id=session.get('userID')).first()

    #resume pdf
    if "resume" in request.files and request.files["resume"]:
        resume = request.files["resume"]
        #remove cropping
        #if img and int((img.getbuffer().nbytes/1024)/1024) > 5:

        resumeSize = -1
        if resume:
            resume.seek(0, os.SEEK_END)
            resumeSize = resume.tell()
            resume.seek(0)
        else:
            success = False
            flash(u"No resume input.", 'resumeError')
        
        if resumeSize == -1:
            flash(u"Couldn't read resume.", 'resumeError')
            success = False
        elif (resumeSize/1024)/1024 > 5:
            flash(u'Resume is too big (max 5 MB).', 'resumeError')
            success = False
        elif resume.filename == '':
            flash(u'Could not read resume', 'resumeError')
            success = False
        else:
            file_ext = os.path.splitext(resume.filename)[1]
            if file_ext == None:
                success = False
                flash(u"Could not assess file type properties", 'resumeError')
            elif file_ext not in json.loads(app.config['UPLOAD_EXTENSIONS_RESUME']):
                flash(u'Accepted file type: .pdf. You uploaded a', file_ext + ".", 'resumeError')
                success = False
    else:
        flash(u"No resume input.", 'resumeError')
        success = False
    
    if success: 
        if resume:
            resume.seek(0) #I read the file before to check the length so I must put the cursor at the beginning in order to upload it.
            delete_resume(user)
            output, filename = upload_resume_file_to_s3(resume, user)
            user.set_resume(output, filename) #set the user profile picture link
            db.session.commit()
        else:
            success=False
            flash(u'Please select a file.', 'resumeError')

    return redirect(url_for('editProfile'))

@app.route('/view', methods=['GET']) #takes one arg = user.id. This is the user that the person logged in is viewing. Doesn't have to be the same user.
def view():
    #sessionID1 = request.cookies.get("user") #get the session token from the previous page cookies

    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))

    if request.args.get("id") == None: #they went to view get without a user id in the request args
        return redirect(url_for('index'))

    user = User.query.filter_by(id=request.args.get("id")).first() #get the correct profile by inputting user id
    if user == None:
        return not_found("404")

    interestList = []
    for interest in user.rtn_interests():
        interestList.append(interest.entered_name)
    careerInterestList = []
    for cint in user.rtn_career_interests():
        careerInterestList.append(cint.entered_name)
    educationList = []
    for educ in user.rtn_education():
        educationList.append(educ.entered_name)
    isStudent = user.is_student
    bio = user.bio

    prof_pic_link = user.profile_picture
    intro_vid_link = user.intro_video
    

    resumeUrl = create_resume_link(user)

    this_user_is_logged_in = (user.id == session.get('userID'))

    mentorGenderPreference = user.mentor_gender_preference
    if mentorGenderPreference != None:
        if mentorGenderPreference == "male":
            mentorGenderPreference = "Male mentor"
        elif mentorGenderPreference == "female":
            mentorGenderPreference = "Female mentor"
        else:
            mentorGenderPreference = "No preference"

    divisionPreference = user.division_preference
    if divisionPreference != None:
        if divisionPreference == "same":
            divisionPreference = "Same division"
        elif divisionPreference == "different":
            divisionPreference = "Different division"
        else:
            divisionPreference = "No preference"

    genderIdentity = user.gender_identity
    if genderIdentity != None:
        if genderIdentity == "male":
            genderIdentity = "Male"
        elif genderIdentity == "female":
            genderIdentity = "Female"
        elif genderIdentity == "nonbinaryNonconforming":
            genderIdentity = "Non-binary/non-conforming"
        else:
            genderIdentity = "Prefer not to respond"

    #^if the user looking at this person's profile page is the one who is currently logged in, 
    # let them logout from or delete their account.
    title="Profile Page"

    if this_user_is_logged_in:
        logData(9,"")
    else:
        logData(10,"")

    return render_template('profile.html', title=title, profile_picture=prof_pic_link, intro_video=intro_vid_link,
                bio=bio, logged_in=this_user_is_logged_in, resumeUrl=resumeUrl,
                interestList=interestList, careerInterestList=careerInterestList, educationList=educationList, 
                genderIdentity=genderIdentity, divisionPreference=divisionPreference,
                isStudent=isStudent, mentorGenderPreference=mentorGenderPreference, user=user, userID=session.get('userID'))
    #user logged in: show profile page.



"""
The preferred way is to simply create a pre-signed URL for the image, and return a redirect to that URL. 
This keeps the files private in S3, but generates a temporary, time limited, URL that can be used to download the file directly from S3. 
That will greatly reduce the amount of work happening on your server, as well as the amount of data transfer being consumed by your server.
https://stackoverflow.com/questions/52342974/serve-static-files-in-flask-from-private-aws-s3-bucket
"""
def create_resume_link(user):
    if user.resume == None or user.resume_key == None:
        resumeUrl = None
    else:
        resumeUrl = s3_client.generate_presigned_url(
            'get_object', 
            Params = {'Bucket': str(app.config['BUCKET_NAME_RESUME']), 'Key': user.resume_key}, 
            ExpiresIn = 100
        )
    return resumeUrl


"""def createCookie(resp, id):
    #sessionTokenKey = str(uuid4())
    resp.set_cookie(key="user", value=id, max_age=None)
    return resp"""


@app.route('/logout', methods=['GET'])
def logout():
    #sessionID1 = request.cookies.get('user') #get the session token
    #means they hit logout btn
    if session.get('userID'): #valid session token -- user already logged in
        session.pop('userID', None)
        #db.session.commit() #remove this user's session token from the dict

    logData(11,"")

    return redirect(url_for('index'))

@app.route('/deleteProfile', methods=['POST']) #need to check security
def deleteProfile():
    
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))

    form = request.form

    user = User.query.filter_by(id=session.get('userID')).first()

    if form.get('first_name') == None:
        flash(u'Please enter a first name.', 'deletionError')
        return redirect(url_for('editProfile'))
    
    if user.first_name == form.get('first_name'): #check input name = first name
        userID = session.get('userID')
        session.pop('userID', None)

        delete_profile_picture(user)
        delete_intro_video(user)
        delete_user_attributes(user.id)
        delete_resume(user)

        selectEntry = None
        if user.is_student: #is mentee
            selectEntry = Select.query.filter_by(mentee_id=user.id).first()

            ProgressMeetingCompletionInformation.query.filter(
                ProgressMeetingCompletionInformation.num_progress_meeting == selectEntry.current_meeting_number_mentee,
                ProgressMeetingCompletionInformation.select_id == selectEntry.id
            ).delete()

            Select.query.filter_by(mentee_id=user.id).delete()
        else:
            selectEntry = Select.query.filter_by(mentor_id=user.id).first()

            ProgressMeetingCompletionInformation.query.filter(
                ProgressMeetingCompletionInformation.num_progress_meeting == selectEntry.current_meeting_number_mentor,
                ProgressMeetingCompletionInformation.select_id == selectEntry.id
            ).delete()

            Select.query.filter_by(mentor_id=user.id).delete()

        Business.query.filter_by(id=user.business_id).first().dec_number_employees_currently_registered() 
        #decrease business number registered by 1 because this user has been deleted
        

        User.query.filter_by(id=userID).delete()
        db.session.commit()

        logData(12,"")

        return render_template('delete-profile-success.html')
    else:
        flash(u'Incorrect first name.', 'deletionError')
        return redirect(url_for('editProfile'))

#TODO: maybe change aws s3 bucket to NO ACLs and limit access to this account.
def upload_media_file_to_s3(file_upload, user):
    filename = ""
    filename+=str(user.id)
    filename+="/"
    filename+=str(uuid4()) #safe file name: uuid4.
    s3_client.put_object(
        Bucket = str(app.config['BUCKET_NAME']),
        Key = filename,
        Body=file_upload,
        #ACL=str(app.config['ACL']),
        ContentType = file_upload.content_type
    )
    #output = 'https://s3-{}.amazonaws.com/{}/{}'.format(app.config['S3_REGION'], app.config['BUCKET_NAME'], filename)
    output = 'https://{}.s3.amazonaws.com/{}'.format(app.config['BUCKET_NAME'], filename)
    print(filename, output, file_upload.content_type)
    db.session.commit() #just in case

    dictFile = {}
    dictFile["type"] = "profilePicture"
    dictFile["fileInfo"] = [filename, file_upload.content_type]
    logData(8,json.dumps(dictFile))

    return (output, filename)

def upload_resume_file_to_s3(file_upload, user):
    filename = ""
    filename+=str(user.id)
    filename+="/"
    filename+=str(uuid4()) #safe file name: uuid4.
    s3_client.put_object(
        Bucket = str(app.config['BUCKET_NAME_RESUME']),
        Key = filename,
        Body=file_upload,
        ContentType = file_upload.content_type
    )
    output = 'https://s3-{}.amazonaws.com/{}/{}'.format(app.config['S3_REGION'], app.config['BUCKET_NAME_RESUME'], filename)
    print(filename, output, file_upload.content_type)
    db.session.commit() #just in case

    dictFile = {}
    dictFile["type"] = "resume"
    dictFile["fileInfo"] = [filename, file_upload.content_type]
    logData(8,json.dumps(dictFile))

    return (output, filename)
    

def delete_user_attributes(userID):
    #when deleting, decrement each of the tags' usage number
    for i in InterestTag.query.filter_by(user_id=userID).all():
        i.delete_inc()
    db.session.commit()
    for i in EducationTag.query.filter_by(user_id=userID).all():
        i.delete_inc()
    db.session.commit()
    for i in CareerInterestTag.query.filter_by(user_id=userID).all():
        i.delete_inc()
    db.session.commit()

    #now just delete the user's tags
    InterestTag.query.filter_by(user_id=userID).delete()
    EducationTag.query.filter_by(user_id=userID).delete()
    CareerInterestTag.query.filter_by(user_id=userID).delete()

    db.session.commit()

def delete_profile_picture(user):
    if user.profile_picture is not None:
        s3_client.delete_object(Bucket=str(app.config["BUCKET_NAME"]), Key=user.profile_picture_key)
    user.set_profile_picture(None, None)
    db.session.commit()

def delete_intro_video(user):
    if user.intro_video is not None:
        s3_client.delete_object(Bucket=str(app.config["BUCKET_NAME"]), Key=user.intro_video_key)
    user.set_intro_video(None, None)
    db.session.commit()

def delete_resume(user):
    if user.resume is not None:
        s3_client.delete_object(Bucket=str(app.config["BUCKET_NAME_RESUME"]), Key=user.resume_key)
    user.set_resume(None, None)
    db.session.commit()

#changed to /mentor
"""
@app.route('/feed', methods=['GET'])
def feed():
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))
    
    user = User.query.filter_by(id=session.get('userID')).first()

    if Select.query.filter_by(mentee_id=user.id).first() != None: 
        #user already selected a mentor
        return render_template('feed.html', isStudent=user.is_student, userID=session.get('userID'), find_match=False)
    
    return render_template('feed.html', isStudent=user.is_student, userID=session.get('userID'), find_match=True)
"""

# method called in the feed js script
@app.route('/getFeed', methods=['GET'])
def getFeed():
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))
    
    user = User.query.filter_by(id=session.get('userID')).first()

    return feedMentee(user)
    


def feedMentee(user):
    """
    Comment about efficiency:
    Right now how this works is it:
    1. Gets all the users with a matching school
    2. Gets all the users with a matching interest
    3. Gets all the users with a matching career interest
    4. Sorts based on how many times the user shows up in steps 1,2,3 (with heuristic weights)
    5. Returns all of the users from that sorted list.
    There's not really a point in returning only the top 10 users instead of all of them. 
    It appears that I can't avoid getting the users from all 3 of the columns, since I can't rule out any users before I see how 
        many matches they have in EACH column. Like what if one user does not go to the same school but has 100 of the same interests?
        I have to look at the interest column in order to determine that.
    """

    userDict = {} #user : number match.
    matches = {} #for data logging
    matches["division_pref"] = 0
    matches["personality"] = 0
    matches["education"] = 0
    matches["career"] = 0
    matches["interest"] = 0

    #get all mentors in the same business as the user. is_student should remove the user themself from the query.
    potentialUsers = User.query.filter_by(business_id=user.business_id).filter_by(is_student=False).all()

    users = []
    for u in potentialUsers:
        if not mentorSelected(u.id): #only select users that have not already been chosen.
            users.append(u)

    for u in users: #initialize user dictionary
        userDict[u] = 0
        #initialize as 0

    #check gender preference/identity
    if str(app.config['MATCHING_FLAG_MENTOR_GENDER_PREFERENCE']) == "True": #only check if flag for gender/identity is "True"
        for u in users: #initialize user dictionary
            if (user.mentor_gender_preference == "male" and u.gender_identity == "male") or (user.mentor_gender_preference == "female" and u.gender_identity == "female"):
                #matching gender preference / gender
                userDict[u] = heuristicVals["gender_pref"]
            #ignore case mentor gender preference == "noPreference".


    #division preferences
    if str(app.config['MATCHING_FLAG_DIVISION_PREFERENCE']) == "True": #only check if flag for division preference is "True"
        for u in users:
            if (u.division_preference == "same" and user.division == u.division) or u.division_preference == "noPreference":
                #other user division preference
                userDict[u] += heuristicVals["division_pref"]
                matches["division_pref"] += 1
            if (user.division_preference == "same" and user.division == u.division) or user.division_preference == "noPreference":
                #this user division preference
                userDict[u] += heuristicVals["division_pref"]
                matches["division_pref"] += 1

    #personality
    if str(app.config['MATCHING_FLAG_PERSONALITY']) == "True":
        for u in users:
            #match in any personality trait - separate to add to the value per each match.
            if u.personality_1 in user.personality_1 or user.personality_1 in u.personality_1:
                userDict[u] += heuristicVals["personality"]
                matches["personality"] += 1
            if u.personality_1 in user.personality_2 or user.personality_2 in u.personality_1:
                userDict[u] += heuristicVals["personality"]
                matches["personality"] += 1
            if u.personality_1 in user.personality_3 or user.personality_3 in u.personality_1:
                userDict[u] += heuristicVals["personality"]
                matches["personality"] += 1
            if u.personality_2 in user.personality_2 or user.personality_2 in u.personality_2:
                userDict[u] += heuristicVals["personality"]
                matches["personality"] += 1
            if u.personality_2 in user.personality_3 or user.personality_3 in u.personality_2:
                userDict[u] += heuristicVals["personality"]
                matches["personality"] += 1
            if u.personality_3 in user.personality_3 or user.personality_3 in u.personality_3:
                userDict[u] += heuristicVals["personality"]
                matches["personality"] += 1
    

    schoolDict = {} #contains all the matching schools for each user (user : [school])
    thisUserEducationTagIDs = user.rtn_education()
    thisUserEducationTagIDs = [edu.id for edu in thisUserEducationTagIDs] #get the ids

    for u in users:
        for educ in u.rtn_education(): #cycle thru each user education
            educationTags = EducationTag.query.filter_by(educationID=educ.educationID).all()
            for edTag in educationTags: #go thru all the educationTags (the ones related to each user ans unique to each input)
                if edTag.id in thisUserEducationTagIDs:
                    if schoolDict.__contains__(u): #add user to the dict
                        schoolDict[u].append(edTag.entered_name)
                    else:
                        sArr = [edTag.entered_name] #not already in the dict --> add a new array
                        schoolDict[u] = sArr

                    #now update match amount in user dict
                    userDict[u] = userDict[u]+heuristicVals["education"]
                    matches["education"] += 1


    interestTitleDict = {} #contains all the matching tags for each user (user : [interest tag titles])
    thisUserInterestTagIDs = user.rtn_interests()
    thisUserInterestTagIDs = [intrst.id for intrst in thisUserInterestTagIDs] #get the ids

    for u in users:
        for intrst in u.rtn_interests(): #cycle thru each user education
            interestTags = InterestTag.query.filter_by(interestID=intrst.interestID).all()
            for intT in interestTags: #go thru all the educationTags (the ones related to each user ans unique to each input)
                if intT.id in thisUserInterestTagIDs:
                    if interestTitleDict.__contains__(u): #add user to the dict
                        interestTitleDict[u].append(intT.entered_name)
                    else:
                        iArr = [intT.entered_name] #not already in the dict --> add a new array
                        interestTitleDict[u] = iArr

                    #now update match amount in user dict
                    userDict[u] = userDict[u]+heuristicVals["interest"]
                    matches["interest"] += 1


    careerDict = {} #contains all the matching career tags for each user (user : [career experience/interest title])
    thisUserCareerInterestIDs = user.rtn_career_interests()
    thisUserCareerInterestIDs = [cInt.id for cInt in thisUserCareerInterestIDs] #get the ids

    for u in users:
        for cInt in u.rtn_career_interests(): #cycle thru each user education
            careerInterestTags = CareerInterestTag.query.filter_by(careerInterestID=cInt.careerInterestID).all()
            for cInt in careerInterestTags: #go thru all the educationTags (the ones related to each user ans unique to each input)
                if cInt.id in thisUserCareerInterestIDs:
                    if careerDict.__contains__(u): #add user to the dict
                        careerDict[u].append(cInt.entered_name)
                    else:
                        cArr = [cInt.entered_name] #not already in the dict --> add a new array
                        careerDict[u] = cArr

                    #now update match amount in user dict
                    userDict[u] = userDict[u]+heuristicVals["career"]
                    matches["career"] += 1


    sortedDict = sorted(userDict.items(), key=lambda item: item[1], reverse=True) #is now a list of tuples
    #sort userDict by value (the number of matches it got in the db.)

    userDictUsefulInfo = {} # { user : { match name : [ matches for this user ] } }
    
    for u in userDict.keys():
        usefulInfo = {}
        usefulInfo['userFn'] = u.first_name
        usefulInfo['userLn'] = u.last_name
        usefulInfo['userBio'] = u.bio
        usefulInfo['userProfilePicture'] = u.profile_picture
        usefulInfo['userIntroVideo'] = u.intro_video
        usefulInfo['userCurrentOccupation'] = u.current_occupation
        usefulInfo['userIsStudent'] = u.is_student
        usefulInfo['resumeURL'] = create_resume_link(u)
        usefulInfo['score'] = userDict[u]

        
        #so there is probably a better way of doing this without making two dicts but I'll implement that later
        if interestTitleDict.__contains__(u):
            usefulInfo['interest matches'] = interestTitleDict[u]
        else:
            usefulInfo['interest matches'] = [] #if no matches, empty array.

        if careerDict.__contains__(u):
            usefulInfo['career matches'] = careerDict[u]
        else:
            usefulInfo['career matches'] = [] #if no matches, empty array.

        if schoolDict.__contains__(u):
            usefulInfo['school matches'] = schoolDict[u]
        else:
            usefulInfo['school matches'] = [] #if no matches, empty array.

        userDictUsefulInfo[str(u.id)] = usefulInfo

    rtnUserArr = [] #array of the users (sorted, unlike the dict)
    for tup in sortedDict: #(key,value)
        rtnUserArr.append(tup[0].id)

    dictItems = {}
    dictItems['userDictUsefulInfo'] = userDictUsefulInfo
    dictItems['userArr'] = rtnUserArr
    
    dictLog = {}
    dictLog["numMatches"] = len(userDict.keys())
    dictLog["sortedWeights"] = [tup[1] for tup in sortedDict]
    dictLog["sortedUserIDs"] = [tup[0].id for tup in sortedDict]
    dictLog["matches"] = matches #nested json object

    logData(13,json.dumps(dictLog)) #log feed get

    return jsonify(dictItems)


def mentorSelected(mentorId): #if this mentor has been selected already
    if Select.query.filter_by(mentor_id=mentorId).first() != None:
        return True
    return False


@app.route('/mentor', methods=['POST'])
def feedPost():
    #A mentee chose a mentor --> post the form with the mentor information

    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))

    form = request.form

    if form.get('userID') == None:
        flash(u'Something went wrong.', 'feedError')
        return redirect(url_for('mentor'))
    
    userMatchID = form.get('userID')

    if Select.query.filter_by(mentor_id=userMatchID).first() != None: 
        #somebody selected this mentor while the current user was on this page
        flash(u'That mentor has been selected already.', 'feedError')
        return redirect(url_for('mentor'))


    newSelect = Select(mentee_id=session.get('userID'), mentor_id=userMatchID)
    #selection will only be made by the user logged in - the mentee.

    db.session.add(newSelect)
    db.session.commit()
    print("successfully made new selection with", User.query.filter_by(id=userMatchID).first())
    
    dictLog = {}
    dictLog["userID"] = userMatchID
    dictLog["score"] = form.get('score')
    dictLog["index"] = form.get('userIdx')
    logData(14,json.dumps(dictLog))

    return redirect(url_for("progress"))

""" NO LONGER IN USE
@app.route('/my-connections', methods=['GET'])
def my_connections():
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))

    user = User.query.filter_by(id=session.get('userID')).first()

    selectUser = None

    isMentee = user.is_student #user.is_mentee

    if isMentee: 
        selectUser = Select.query.filter_by(mentee_id=user.id).first()
        if selectUser != None:
            selectUser = User.query.filter_by(id=selectUser.mentor_id).first() #get the mentor back from the select
    else:
        selectUser = Select.query.filter_by(mentor_id=user.id).first()
        if selectUser != None:
            selectUser = User.query.filter_by(id=selectUser.mentee_id).first() #get the mentee back from the select

    return render_template('my_network.html', isMentee=isMentee, selectUser=selectUser, userID=session.get('userID'))
"""

def userLoggedIn():
    
    #Checks if the user is actually logged in -- commented out for easier testing
    #userID = SessionTokens.query.filter_by(sessionID=sessionID1).first()
    if session.get('userID'): #valid session token -- user already logged in
        if User.query.filter_by(id=session['userID']).first() == None:
            return False
        return True

    return False

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    dictLog = {}
    dictLog['desc'] = e.description
    logData(17,json.dumps(dictLog))
    return render_template('csrf_error.html', reason=e.description), 400


"""
NOTE ABOUT THE HANDLER FOR 413:
The config MAX_CONTENT_LENGTH is set, so the connection will close before the file can be sent.
This means that it will immediately abort and not run the errorhandler.
This might be fixed in the future? 
This should be handled client-side, since there is already a bit of code in my js file to gaurd against big files.
"""

@app.errorhandler(413)
def size_error(e):
    print("logging error 413")
    logData(18,"[Image is too big (max 5 MB)]")
    flash(u'Image is too big (max 5 MB).', 'imageError')
    return redirect(url_for('editProfile'))


@app.errorhandler(404)
# inbuilt function which takes error as parameter
def not_found(e):
    # defining function
    dictLog = {}
    dictLog['code'] = 404
    dictLog['desc'] = "404 error"
    logData(16,json.dumps(dictLog))
    return render_template("404_error.html")

@app.errorhandler(Exception)
# inbuilt function which takes error as parameter
def error_handler(e):
    code = 500 #problem with my code
    if isinstance(e, HTTPException):
        code = e.code
    if code == 404:
        return render_template("404_error.html")
    if code == 500:
        db.session.rollback()
    if code != 200: #response OK
        dictLog = {}
        dictLog['code'] = code
        dictLog['desc'] = str(e)
        logData(16,json.dumps(dictLog))
    
    return render_template("general_error.html", code=code)

def logData(num, msg):
    if str(app.config['LOG_DATA']) == "True":
        newEvent = Event(userID=session.get('userID'), action=num, message=msg)
        db.session.add(newEvent)
        db.session.commit()