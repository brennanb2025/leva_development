#This file is the python flask backend
from flask import request, render_template, flash, redirect, url_for, session, make_response, send_file, send_from_directory
from app import app, db#, s3_client#, oauth
#import lm as well?^
from app.input_sets.forms import LoginForm, EditPasswordForm, RegistrationForm
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
import io

import app.model.admin as admin
import app.model.progress as progressFuncs
import app.model.login as login
import app.model.register as registerFuncs
import app.model.editProfile as editProfileFuncs
import app.model.feed as feed
import app.model.AWS as AWS
import app.model.view as viewFuncs

#TODO: ADD  and form.validate():   to protect forms

# session timeout


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(
        hours=10)  # 10 hours until need to resign in

# different urls that application implements
# @'s are decorators, modifies function that follows it. Creates association between URL and function.


# index page GET.
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index1.html', userID=session.get('userID'))
    # return render_template('index.html', userID=session.get('userID')) (old)


@app.route('/portal')
def portal():
    return render_template('portal.html', userID=session.get('userID'))


@app.route("/admin", methods = ['GET'])
def admin_login():
    return render_template("admin_login.html")

@app.route("/admin", methods = ['POST'])
def admin_login_post():
    # check to see if the login credentials are correct, then
    #if username and password match...
    if admin.admin_validate_login(request.form.get("username"), request.form.get("password")):
        session["userID"] = request.form.get("username") #put the username in the session
        return redirect(url_for("admin_data"))
    return redirect(url_for("index"))


@app.route("/admin-data", methods=['GET'])
def admin_data():
    # This will only be true if they went through the admin login
    if session["userID"] == str(app.config['ADMIN_USERNAME']):
        return render_template("admin.html")
    else:
        return redirect(url_for("index"))


@app.route("/admin-lookup-user", methods=['GET'])
def admin_lookup_user():
    # This will only be true if they went through the admin login
    if session["userID"] != str(app.config['ADMIN_USERNAME']):
        return

    userId = request.args.get("userId")
    firstName = request.args.get("firstName")
    lastName = request.args.get("lastName")
    email = request.args.get("email")

    users = admin.admin_lookup_user(userId, firstName, lastName, email)
    return jsonify([{"id":u.id,
            "email":u.email,
            "name":u.first_name + " " + u.last_name}
        for u in users])


@app.route("/admin-lookup-users-in-business", methods=['GET'])
def admin_lookup_users_in_business():
    # This will only be true if they went through the admin login
    if session["userID"] != str(app.config['ADMIN_USERNAME']):
        return

    businessId = request.args.get("businessId")

    return jsonify([{"id":u.id,
                    "name":u.first_name+ " " + u.last_name,
                    "email":u.email,
                    "mentor_or_mentee": "mentee" if u.is_student else "mentor"
                    } for u in admin.admin_lookup_users_in_business(businessId)])

# TODO: test this


@app.route("/admin-selects-info", methods=['GET'])
def admin_selects_info():  # mentees true = search for mentees, false = mentors
    # This will only be true if they went through the admin login
    if session["userID"] != str(app.config['ADMIN_USERNAME']):
        return

    businessId = request.args.get("businessId")
    
    unmatchedUsers, arrInfo = admin.selects_info(businessId)
    
    dictRtn = {
        "unmatchedUsers": [{"id": u.id,
                            "name": u.first_name + " " + u.last_name,
                            "email": u.email,
                            "mentor_or_mentee": "mentee" if u.is_student else "mentor"
                            } for u in unmatchedUsers],
        "matchesInfo": [{
            "Select": {
                        "id": select.id,
                        "current_meeting_number_mentor": select.current_meeting_number_mentor,
                        "current_meeting_number_mentee": select.current_meeting_number_mentee
                        },
            "mentee": {
                "id": mentee.id,
                "name": mentee.first_name + " " + mentee.last_name,
                "email": mentee.email
            },
            "mentor": {
                "id": mentor.id,
                "name": mentor.first_name + " " + mentor.last_name,
                "email": mentor.email
            }
        } for (select, mentee, mentor) in arrInfo]
    }

    return jsonify(dictRtn)

# TODO: Test this


@app.route("/admin-user-matches", methods=['GET'])
def admin_user_matches():  # mentees true = search for mentees, false = mentors
    # This will only be true if they went through the admin login
    if session["userID"] != str(app.config['ADMIN_USERNAME']):
        return

    businessId = request.args.get("businessId")

    dictMenteeToMentor = admin.user_matches(businessId)

    return jsonify([
        {
            "mentee_id": u.id,
            "mentee_email": u.email,
            "mentors": [
                {
                    "mentor_id": m.id,
                    "mentor_email": m.email
                }
                for m in dictMenteeToMentor[u]
            ]
        }
        for u in dictMenteeToMentor.keys()
    ])


@app.route("/admin-lookup-business", methods=['GET'])
def admin_lookup_business():
    # This will only be true if they went through the admin login
    if session["userID"] != str(app.config['ADMIN_USERNAME']):
        return

    data = request.args

    business = admin.lookup_business(data.get("businessId"), data.get("businessString"))
    
    return jsonify(
        {
            "id": business.id,
            "name": business.name,
            "number_employees_maximum": business.number_employees_maximum,
            "number_employees_currently_registered": business.number_employees_currently_registered
        })


@app.route("/admin-all-businesses", methods=['GET'])
def admin_all_businesses():
    # This will only be true if they went through the admin login
    if session["userID"] != str(app.config['ADMIN_USERNAME']):
        return

    return jsonify([
            {
                "id":b.id, 
                "name":b.name, 
                "number_employees_maximum":b.number_employees_maximum, 
                "number_employees_currently_registered":b.number_employees_currently_registered
            } 
                for b in admin.all_businesses()])

@app.route("/admin-events-exceptions", methods = ['GET'])
def admin_get_events_exceptions():
    if session["userID"] != str(app.config['ADMIN_USERNAME']): #This will only be true if they went through the admin login
        return

    startTime = datetime.datetime.strptime(
        request.args.get("startTime"), '%Y-%m-%d %H:%M:%S')
    endTime = datetime.datetime.strptime(
        request.args.get("endTime"), '%Y-%m-%d %H:%M:%S')
    action = request.args.get("action")

    print(startTime, endTime)

    return jsonify([
            {
                "id":e.id, 
                "user id":e.userID, 
                "message":e.message, 
                "timestamp":e.timestamp
            } 
                for e in admin.get_events(action, startTime, endTime)])


@app.route("/admin-lookup-user-feed", methods = ['GET'])
def admin_lookup_user_feed():
    if session["userID"] != str(app.config['ADMIN_USERNAME']): #This will only be true if they went through the admin login
        return

    userId = request.args.get("userid")
    matches = admin.get_potential_matches(userId)
    jsonRtn = {
        "userId":matches.userId,
        "matches":
        [
            {
                "mentor": m.mentor.id,
                "mentorInterestMatches": m.mentorInterestMatches,
                "mentorCareerMatches": m.mentorCareerMatches,
                "mentorEducationMatches": m.mentorEducationMatches,
                "score": m.score
            }
            for m in matches.matches
        ]
    }


    return jsonify(jsonRtn)


@app.route("/admin-lookup-user-feed-all", methods = ['GET'])
def admin_lookup_user_feed_all():
    if session["userID"] != str(app.config['ADMIN_USERNAME']): #This will only be true if they went through the admin login
        return

    userId = request.args.get("userid")
    allMatches = admin.get_all_matches(userId)
    jsonRtn = {
        "userId":allMatches.userId,
        "matches":
        [
            {
                "mentor": m.mentor.id,
                "mentorInterestMatches": m.mentorInterestMatches,
                "mentorCareerMatches": m.mentorCareerMatches,
                "mentorEducationMatches": m.mentorEducationMatches,
                "score": m.score
            }
            for m in allMatches.matches
        ]
    }

    return jsonify(jsonRtn)

@app.route("/admin-delete-match", methods = ['POST'])
def admin_delete_match():
    if session["userID"] != str(app.config['ADMIN_USERNAME']): #This will only be true if they went through the admin login
        return

    menteeId = request.form.get("menteeId")
    mentorId = request.form.get("mentorId")

    if menteeId is None or mentorId is None:
        return jsonify({"success":False})

    success = admin.deleteMatch(menteeId, mentorId)

    return jsonify({"success":success})


@app.route("/business-excel")
def admin_get_business_excel():
    if session["userID"] != str(app.config['ADMIN_USERNAME']): #This will only be true if they went through the admin login
        return

    businessId = request.args.get("businessId")
    filename = admin.createExcelSheet(businessId)

    print("filename:",filename)

    return_data = io.BytesIO()
    with open(filename, 'rb') as fo:
        return_data.write(fo.read())
    # (after writing, cursor will be at last byte, so move it to start)
    return_data.seek(0)

    os.remove(filename)

    return send_file(return_data, 
            attachment_filename=filename, 
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True)


@app.route('/mentor')
def mentor():
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))

    user = User.query.filter_by(id=session.get('userID')).first()

    if Select.query.filter_by(mentee_id=user.id).first() != None or Select.query.filter_by(mentor_id=user.id).first() != None:
        # user already selected a mentor
        return render_template('mentor.html', isStudent=user.is_student, userID=session.get('userID'), find_match=False)

    return render_template('mentor.html', isStudent=user.is_student, userID=session.get('userID'), find_match=True)


@app.route('/progress', methods=['GET'])
def progress():

    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))

    user = User.query.filter_by(id=session.get('userID')).first()
    
    selectEntry, select_mentor_mentee, progressDone, currMeetingInfo, prevMeetingInfo, futureMeetingInfo = \
            progressFuncs.get_progress_info(user)

    admin.logData(session.get('userId'),15,"")
    
    #TODO redo this
    return render_template('progress.html', selectEntry=selectEntry, isMentee=user.is_student, \
            #selectMentorMentee=select_mentor_mentee,
            matchedUsers = [select_mentor_mentee], userID=user.id, progressDone=progressDone, \
            matchToMeetingInfo={
                select_mentor_mentee.id: {"prev_meeting_info":prevMeetingInfo, "curr_meeting_info":currMeetingInfo, "progress_done":progressDone}})
            #currMeetingInfo=currMeetingInfo, prevMeetingInfo=prevMeetingInfo, futureMeetingInfo=futureMeetingInfo)


@app.route('/progress', methods=['POST'])
def currentMeetingSetDone():
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))
    
    form = request.form
    user = User.query.filter_by(id=session.get('userID')).first()
    meetingNotes = form.get("meetingNotes")

    progressFuncs.set_current_info_meeting_done(user, meetingNotes)

    return progress()  # send to progress page


# sign-in page GET.
@app.route('/sign-in', methods=['GET'])
def sign_in():

    if userLoggedIn():  # valid session token -- user already logged in
        return redirect(url_for('view', id=session['userID']))

    form = LoginForm()
    title = "Sign in"

    return render_template('sign_in.html', form=form, title=title)

# sign-in page POST. Checks each input from the form.
# If the user correctly inputs their information, makes a new cookie and adds the user to the session. Then sends them to the view GET.


@app.route('/sign-in', methods=['POST'])
def sign_inPost():

    form1 = request.form 
    
    success, response = login.sign_in_post(form1.get('email'), form1.get('password'))
    if response.email_not_entered:
        flash(u'Please enter an email', 'emailError')
    if response.password_not_entered:
        flash(u'Please enter a password', 'passwordError')
    if response.email_not_found:
        flash(u'User does not exist. If you are a new user, click the "Make an Account" button below.', 'emailError')
    if response.incorrect_password:
        flash(u'Incorrect password', 'passwordError')

    #TODO: Check logic separation here
    if success: 
        user = User.query.filter_by(email=form1.get('email')).first()
        id = user.id
        # get view should send to main page
        resp = make_response(redirect(url_for('view', id=id)))
        resp.set_cookie('userID', str(id))

        session["userID"] = id
        #newToken = SessionTokens(sessionID=sessionToken) #make a new token
        #db.session.add(newToken) #add to database
        admin.logData(session.get('userId'),4,"") #log in post success
        return resp
    else:
        admin.logData(session.get('userId'),3,"") #log in post failure
        return redirect(url_for('sign_in')) #failure


#register GET. Creates a registration form and passes popular tags as suggestions.
@app.route('/register', methods=['GET'])
def register():

    # publicVisitorIP = request.remote_addr #no host proxy

    # Attempts to register an email/password pair.
    form = RegistrationForm()

    if userLoggedIn():
        return redirect(url_for('view', id=session.get('userID')))

    interestTags, careerInterests, schools = registerFuncs.get_popular_tags()

    resp = make_response(render_template('register1.html', interestTags=interestTags, careerInterests=careerInterests, schools=schools,
                                         interestList=list(), educationList=list(), careerInterestList=list(), form=form))
    # return render_template('register_first_access.html', interestTags=interestTags, careerInterests=careerInterests, schools=schools, form=form)

    # record the current time as a string
    resp.set_cookie('initialTimestampGET', str(datetime.datetime.utcnow()))

    admin.logData(session.get('userId'),0,"") #log data: register get

    return resp  # return the template with the cookie


# post register page 1
@app.route('/register/validate/1', methods=['POST'])
def registerValidate1():
    #email checking
    email = request.json['email'] 
    
    success, errors = registerFuncs.registerValidate1(email)

    return json.dumps({
        'success': success,
        'errors': json.dumps(errors)
    })


# post register page 2
@app.route('/register/validate/2', methods=['POST'])
def registerValidate2():
    #email checking

    business = request.json['business'] 
    success, errors = registerFuncs.registerValidate1(business)

    return json.dumps({
        'success': success,
        'errors': json.dumps(errors)
    })

#register POST. Checks form input. If it is correctly input, creates a new user. Then sends them to the sign-in page.
#Current file size limited to 5 MB.
@app.route('/register', methods=['POST'])
def registerPost():

    form1 = request.form   
    
    #resume pdf
    if "resume" in request.files and request.files["resume"]:
        resume = request.files["resume"]

    if "croppedImgFile" in request.files and request.files.get("croppedImgFile").filename != '':
        img = request.files.get("croppedImgFile")
    
    success, resp = registerFuncs.registerPost(form1, resume, img)
    
    if success:

        timeDiff = str(datetime.datetime.utcnow() - datetime.datetime.strptime(
            request.cookies.get('initialTimestampGET'), "%Y-%m-%d %H:%M:%S.%f"))
        dataDict = {}
        dataDict["registerTimeDiff"] = timeDiff
        admin.logData(session.get('userId'),2, json.dumps(dataDict))

        # success: get request to sign_in page
        resp = make_response(redirect(url_for('sign_in')))

        resp.set_cookie('initialTimestampGET', '', expires=0)  # delete cookie

        return resp
    else:
        flash(u'We encountered an error registering you. Please fix any errors in the following pages.', 'generalError')
        return registerPreviouslyFilledOut(form1, resp, request)


#gets all the values from the form that was previously filled out, so that they can be sent back and autofilled into a new form.
def registerPreviouslyFilledOut(form, resp, request):

    #TODO: Change errors to resp

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

    if "email" in errors:  # if error - make it blank.
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

    register_type = form.get("radio_mentor_mentee")  # student or mentor
    # ^v will be none if somehow they messed with it
    if form.get('radio_contact') == 'Phone number':
        email_or_phone = "phone"
        phone_num = form.get('phoneNumber')

    mentorGenderIdentity = form.get("radio_gender_identity")
    menteeGenderPreference = form.get("radio_gender_preference")
    textPersonality1 = form.get("personality1")
    textPersonality2 = form.get("personality2")
    textPersonality3 = form.get("personality3")
    divisionPreference = form.get("divisionPreference")

    # get all the input attributes
    interestInputs = []
    if not "num_tags" in errors:
        interestInputs = form.getlist("tagName")

    eduInputs = []
    if not "num_education_listings" in errors:
        eduInputs = form.getlist("educationName")

    carIntInputs = []
    if not "num_education_listings" in errors:
        carIntInputs = form.getlist("careerInterestName")

    # v load the register page
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

    resp.set_cookie('initialTimestampGET', request.cookies.get(
        'initialTimestampGET'))  # return with the initial time

    timeDiff = str(datetime.datetime.utcnow() - datetime.datetime.strptime(
        request.cookies.get('initialTimestampGET'), "%Y-%m-%d %H:%M:%S.%f"))
    dataDict = {}
    dataDict["registerTimeDiff"] = timeDiff
    dataDict["errors"] = errors
    admin.logData(session.get('userId'),1, json.dumps(dataDict)) #log data: register post error
    

    return resp





# edit-profile GET. Readies edit profile forms and user information.
@app.route('/edit-profile', methods=['GET'])
def editProfile():

    if not userLoggedIn():
        return redirect(url_for('sign_in'))

    formPwd = EditPasswordForm()

    user = User.query.filter_by(id=session.get('userID')).first()

    readyProfileResp = editProfileFuncs.readyUserProfile(session.get('userID'))
    interestTags, careerInterests, schools = registerFuncs.get_popular_tags()
    resumeUrl = AWS.create_resume_link(user)

    admin.logData(session.get('userId'),5,"") #log data edit profile get


    title="Edit profile Page"
    #return render_template('edit_profile.html', intro_video=intro_video_link, 
    #return render_template('editProfileNew.html', intro_video=intro_video_link, 
    return render_template('edit_profile_revised.html', intro_video=user.intro_video, 
            contact_method=user.email_contact, phone_num=user.phone_number, profile_picture=user.profile_picture, 
            interestTags=interestTags, careerInterests=careerInterests, schools=schools, 
            title=title, bio=user.bio, 
            interestList=readyProfileResp.interestList, 
            careerInterestList=readyProfileResp.careerInterestList, 
            educationList=readyProfileResp.educationList, 
            personality_1=user.personality_1, personality_2=user.personality_2, personality_3=user.personality_3, 
            division=user.division, resumeUrl=resumeUrl, 
            divisionPreference=readyProfileResp.divisionPreference,
            mentorGenderPreference=readyProfileResp.mentorGenderPreference, 
            genderIdentity=readyProfileResp.genderIdentity,
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

    admin.logData(session.get('userId'),5,"") #log data edit profile get

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


@app.route('/edit-profile', methods=['POST'])
def editProfilePost():

    if not userLoggedIn():
        return redirect(url_for('sign_in'))

    form = request.form

    if form.get("submitBtn") == "editResume":  # different types of submissions
        editProfResume()
    elif form.get("submitBtn") == "deleteResume":
        deleteResume()

    id=session['userID']

    success = True
    u = User.query.filter_by(id=id).first()

    changedFnSuccess = False #init as false in case they didn't change it
    if form.get("first_name") != u.first_name: #changed first name --> check it
        changedFnSuccess=editProfileFuncs.checkFirstName(form.get("first_name"))
        if not changedFnSuccess: #changed first name unsuccessful.
            success = False
            flash(u'Please enter a new first name.', 'firstNameError')

    changedLnSuccess = False #init as false in case they didn't change it
    if form.get("last_name") != u.last_name: #changed last name --> check it
        changedLnSuccess=editProfileFuncs.checkLastName(form.get("last_name"))
        if not changedLnSuccess: #change unsuccessful.
            success = False
            flash(u'Please enter a new last name.', 'lastNameError')

    changedCitySuccess = False #init as false in case they didn't change it
    if form.get("city_name") != u.city_name: #changed city name --> check it
        changedCitySuccess=editProfileFuncs.checkCityName(form.get("city_name"))
        if not changedCitySuccess: #change unsuccessful.
            success = False
            flash(u'Please enter a new city name.', 'cityNameError')
    
    changedOccupationSuccess = False #init as false in case they didn't change it
    if form.get("current_occupation") != u.current_occupation: #changed current occupation --> check it
        changedOccupationSuccess=editProfileFuncs.checkCurrentOccupationName(form.get("current_occupation"))
        if not changedOccupationSuccess: #change unsuccessful.
            success = False
            flash(u'Please enter a new current occupation.', 'currentOccupationError')

    changedBioSuccess = False #init as false in case they didn't change it
    if form.get("bio") != u.bio: #changed bio --> check it
        changedBioSuccess=editProfileFuncs.checkBio(form.get("bio") )
        if not changedBioSuccess: #change unsuccessful.
            success = False
            flash(u'Your bio cannot be empty.', 'bioError')
    
    changedMentorGenderSuccess = False
    if u.is_student and form.get("radio_gender_preference") != None:
        #ensuring that this form actually exists
        if form.get("radio_gender_preference") != u.mentor_gender_preference: #changed preference --> check it
            changedMentorGenderSuccess=editProfileFuncs.checkMentorGenderPreference(form.get("radio_gender_preference"))
            if not changedMentorGenderSuccess: #change unsuccessful.
                success = False
                flash(u"Please enter a preference for your mentor's gender.", 'mentor_preference_error')

    changedGenderIdentitySuccess = False
    if not u.is_student and form.get("radio_gender_identity") != None:
        if form.get("radio_gender_identity") != u.gender_identity: #changed gender identity --> check it
            changedGenderIdentitySuccess=editProfileFuncs.checkGenderIdentity(form.get("radio_gender_identity"))
            if not changedGenderIdentitySuccess: #change unsuccessful.
                success = False
                flash(u"Please enter your gender identity.", 'gender_identity_error')
            
    changedInputsSuccess = False
    if form.get("changedAttributes") == "True": #changed attributes --> check them
        resp = changedInputsSuccess=editProfileFuncs.checkAttributes(form.get('num_tags'),
                                                         form.get('num_education_listings'),
                                                         form.get('num_career_interests'), 
                                                         u.is_student)
        if not resp.success: #change unsuccessful.
            success = False
            if resp.interestError:
                flash(u'Please enter at least one interest.', 'interestError')
            if resp.educationError:
                flash(u'Please enter at least one school.', 'educationError')
            if resp.careerInterestError:
                flash(u''+resp.careerInterestErrorMessage, 'careerInterestError')
    
        
    changedPersonalitySuccess = False
    if form.get("personality1") != u.personality_1 or form.get("personality2") != u.personality_2 or form.get("personality3") != u.personality_3: #changed --> check it
        changedPersonalitySuccess=editProfileFuncs.checkPersonality(form.get("personality1"), form.get("personality2"), form.get("personality3"))
        if not changedPersonalitySuccess: #change unsuccessful.
            success = False
            flash(u'You must input 3 personality traits/phrases.', 'personalityError')
    
    changedDivisionSuccess = False
    if form.get("division") != u.division: #changed --> check it
        changedDivisionSuccess=editProfileFuncs.checkDivision(form.get('division'))
        if not changedDivisionSuccess: #change unsuccessful.
            success = False
            flash(u'You must input what division you are in.', 'divisionError')
    
    changedDivisionPreferenceSuccess = False
    if form.get("divisionPreference") != u.division_preference: #changed --> check it
        changedDivisionPreferenceSuccess=editProfileFuncs.checkDivisionPreference(form.get("divisionPreference"))
        if not changedDivisionPreferenceSuccess: #change unsuccessful.
            success = False
            if u.is_student:
                flash(u"Please enter a preference for your mentor's division.", 'divisionPreferenceError')
            else:
                flash(u"Please enter a preference for your mentee's division.", 'divisionPreferenceError')

    changedContactMethodSuccess = False
    if form.get("radio_contact") == "Phone number" and u.email_contact \
                or form.get("radio_contact") == "Email" and not u.email_contact: #changed --> check it
        changedContactMethodSuccess=editProfileFuncs.checkContactPreference(form.get("radio_contact"), form.get('phoneNumber'))
        if not changedContactMethodSuccess: #change unsuccessful.
            success = False
            flash(u'Your phone number cannot be empty.', 'phoneError')

    if success:
        # set here
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
            editProfileFuncs.changeAttributes(form.getlist("tagName"), form.getlist("educationName"), form.getlist("careerInterestName"), u)
        if changedPersonalitySuccess:
            u.set_personality(form.get('personality1').strip(), form.get(
                'personality2').strip(), form.get('personality3').strip())
        if changedDivisionSuccess:
            u.set_division(form.get("division").strip())
        if changedDivisionPreferenceSuccess:
            u.set_division_preference(form.get("divisionPreference"))
        if changedContactMethodSuccess:
            if form.get('radio_contact') == 'Email':  # checked the email box
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
        
        admin.logData(session.get('userId'),7,json.dumps(dataChangedDict)) #log data edit profile success

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
        admin.logData(session.get('userId'),6,json.dumps(dataChangedDict)) #log data edit profile error
        return redirect(url_for('editProfile'))


#edit-profile-password POST.
#changes the user's password if it is input correctly. Then sends the user back to view.
@app.route('/edit-profile-password', methods = ['POST'])
def editProfilePassword():

    if not userLoggedIn():
        return redirect(url_for('sign_in'))

    form = request.form

    resp = editProfileFuncs.editPassword(form.get('password'), form.get('password2'), session['userID'])

    if resp.success:
        return redirect(url_for('view', id=session.get('userID')))
    else: 
        if resp.passwordError:
            flash(u'Please enter a password.', 'passwordError')
        if resp.password2Error:
            flash(u''+resp.password2ErrorMessage, 'password2Error')

        return redirect(url_for('editProfile'))


@app.route('/edit-profile-picture', methods=['POST'])
def editProfPic():
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))
    
    if "croppedImgFile" in request.files:
        img = request.files.get("croppedImgFile")
    
    resp = editProfileFuncs.editProfilePicture(img, session['userID'])
    
    if not resp.success:
        if resp.fileNotFound:
            flash(u'Please select a file.', 'pictureError')
        if resp.imageUnreadable:
            flash(u'Could not read image', 'imageError')
        if resp.imageSizeUnreadable:
            flash(u'Could not assess image size.', 'imageError')
        if resp.badFileType:
            flash(u''+resp.badFileTypeMessage, 'imageError')
        admin.logData(session.get('userId'),18,resp.errorMsg)

    return redirect(url_for('editProfile'))


@app.route('/delete-profile-picture', methods=['POST'])
def deleteProfPic():
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))

    user = User.query.filter_by(id=session.get('userID')).first()
    AWS.delete_profile_picture(user)

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

# @app.route('/delete-resume', methods=['POST'])


def deleteResume():
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))

    user = User.query.filter_by(id=session.get('userID')).first()

    AWS.delete_resume(user)

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

# @app.route('/edit-profile-resume', methods=['POST'])


def editProfResume():
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))

    user = User.query.filter_by(id=session.get('userID')).first()

    # resume pdf
    if "resume" in request.files and request.files["resume"]:
        resume = request.files["resume"]
        resp = editProfileFuncs.editProfileResume(user, resume)

        if resp.resumeNotInput:
            flash(u"No resume input.", 'resumeError')

        if resp.unreadable:
            flash(u"Couldn't read resume.", 'resumeError')

        if resp.tooBig:
            flash(u'Resume is too big (max 5 MB).', 'resumeError')

        if resp.noFilename:
            flash(u'Could not read resume', 'resumeError')
        
        if resp.fileTypeUnreadable:
            flash(u"Could not assess file type properties", 'resumeError')

        if resp.fileTypeNotAllowed:
            flash(u"" + resp.fileTypeError, 'resumeError')

    else:
        flash(u"No resume input.", 'resumeError')

    return redirect(url_for('editProfile'))


# takes one arg = user.id. This is the user that the person logged in is viewing. Doesn't have to be the same user.
@app.route('/view', methods=['GET'])
def view():
    # sessionID1 = request.cookies.get("user") #get the session token from the previous page cookies

    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))

    # they went to view get without a user id in the request args
    if request.args.get("id") == None:
        return redirect(url_for('index'))

    id = request.args.get("id")
    resp = viewFuncs.create_user_page(id)
    user = resp.user
    if user == None:
        return not_found("404")

    this_user_is_logged_in = (user.id == session.get('userID'))
    #^if the user looking at this person's profile page is the one who is currently logged in, 
    # let them logout from or delete their account.
    title = "Profile Page"

    if this_user_is_logged_in:
        admin.logData(session.get('userId'),9,"")
    else:
        admin.logData(session.get('userId'),10,"")

    return render_template('profile.html', title=title, profile_picture=user.profile_picture, intro_video=user.intro_video,
                bio=user.bio, logged_in=this_user_is_logged_in, resumeUrl=resp.resumeUrl,
                interestList=resp.interestList, careerInterestList=resp.careerInterestList, educationList=resp.educationList, 
                genderIdentity=resp.genderIdentity, divisionPreference=resp.divisionPreference,
                isStudent=user.is_student, mentorGenderPreference=resp.mentorGenderPreference, user=user, userID=session.get('userID'))
    #user logged in: show profile page.



"""def createCookie(resp, id):
    #sessionTokenKey = str(uuid4())
    resp.set_cookie(key="user", value=id, max_age=None)
    return resp"""


@app.route('/logout', methods=['GET'])
def logout():
    # sessionID1 = request.cookies.get('user') #get the session token
    # means they hit logout btn
    if session.get('userID'):  # valid session token -- user already logged in
        session.pop('userID', None)
        # db.session.commit() #remove this user's session token from the dict

    admin.logData(session.get('userId'),11,"")

    return redirect(url_for('index'))


@app.route('/deleteProfile', methods=['POST'])  # need to check security
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
        session.pop('userID', None)

        editProfileFuncs.deleteProfile(user)

        admin.logData(session.get('userId'),12,"")

        return render_template('delete-profile-success.html')
    else:
        flash(u'Incorrect first name.', 'deletionError')
        return redirect(url_for('editProfile'))

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
    """
    user = User.query.filter_by(id=session.get('userID')).first()

    return feedMentee(user)
    """

    userId = session.get('userID')

    dictFeed = feed.feedMenteeOld(userId)
    if dictFeed == None:
        return None
    return jsonify(dictFeed)


@app.route('/mentor', methods=['POST'])
def feedPost():
    # A mentee chose a mentor --> post the form with the mentor information

    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))

    form = request.form

    if form.get('userID') == None:
        flash(u'Something went wrong.', 'feedError')
        return redirect(url_for('mentor'))

    userMatchID = form.get('userID')

    if not feed.feedPost(session.get('userId'), userMatchID):
        flash(u'That mentor has been selected already.', 'feedError')
        return redirect(url_for('mentor'))
    
    dictLog = {}
    dictLog["userID"] = userMatchID
    dictLog["score"] = form.get('userScore')
    dictLog["index"] = form.get('userIdx')
    admin.logData(session.get('userId'),14,json.dumps(dictLog))

    return redirect(url_for("progress"))

@app.route('/react-test/<path:path>')
def react_test_static(path):
    return send_from_directory("../frontend/build", path)

@app.route('/react-test')
def react_test():
    return send_from_directory("../frontend/build", 'index.html')

# @app.route('/react-routing-test')
# def react_test():
#     return send_from_directory("../frontend/build", 'index.html')

@app.route("/test-endpoint", methods=["GET"])
def test_endpoint():
    res = {
        "status": "SUCCESS",
        "message": "send help"
    }
    return res

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

    # Checks if the user is actually logged in -- commented out for easier testing
    #userID = SessionTokens.query.filter_by(sessionID=sessionID1).first()
    if session.get('userID'):  # valid session token -- user already logged in
        if User.query.filter_by(id=session['userID']).first() == None:
            return False
        return True

    return False


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    dictLog = {}
    dictLog['desc'] = e.description
    admin.logData(session.get('userId'),17,json.dumps(dictLog))
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
    admin.logData(session.get('userId'),18,"[Image is too big (max 5 MB)]")
    flash(u'Image is too big (max 5 MB).', 'imageError')
    return redirect(url_for('editProfile'))


@app.errorhandler(404)
# inbuilt function which takes error as parameter
def not_found(e):
    # defining function
    # dictLog = {}
    # dictLog['code'] = 404
    # dictLog['desc'] = "404 error"
    # logData(16, json.dumps(dictLog))
    # return render_template("404_error.html")

    return send_from_directory("../frontend/build", 'index.html')


"""
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
        admin.logData(session.get('userId'),16,json.dumps(dictLog))
    
    return render_template("general_error.html", code=code)
"""