from flask import request, render_template, flash, redirect, url_for, session, make_response, send_from_directory
from app import app, db, s3_client#, oauth
#import lm as well?^
from app.input_sets.forms import EditCityForm, EditCurrentOccupationForm, LoginForm, EditPasswordForm, EditFirstNameForm, EditLastNameForm, EmptyForm, RegistrationForm, EditCityForm, EditCurrentOccupationForm
from uuid import uuid4
from app.input_sets.models import User, Tag, InterestTag, EducationTag, School, CareerInterest, CareerInterestTag, Select
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
heuristicVals["career"] = 2         #career interest should be more important than regular similar interest
heuristicVals["interest"] = 1       #least important of the attributes

#session timeout
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours=10) #10 hours until need to resign in

#different urls that application implements
#v=decorators, modifies function that follows it. Creates association between URL and fxn.
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET']) 
def index():
    
    return render_template('index.html', userID=session.get('userID'))

@app.route('/sign-in', methods=['GET'])
def sign_in():

    if userLoggedIn(): #valid session token -- user already logged in
        return redirect(url_for('view', id=session['userID']))

    form = LoginForm()
    title="Sign in"
    return render_template('sign_in.html', form=form, title=title)

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
        
        return resp
    else:
        return redirect(url_for('sign_in')) #failure


def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')


@app.route('/register', methods=['GET'])
def register():

    # Attempts to register an email/password pair; 
    form = RegistrationForm()

    #sessionID1 = request.cookies.get("user") #get the session token from the previous page cookies
    #userID = SessionTokens.query.filter_by(sessionID=sessionID1).first()
    if userLoggedIn():
        return redirect(url_for('view', id=session.get('userID')))

    interestTags, careerInterests, schools = get_popular_tags()
    
    return render_template('register_first_access.html', interestTags=interestTags, careerInterests=careerInterests, schools=schools, form=form)


def get_popular_tags(): #returns (tags, careerInterests, schools) - 500 most used from each
    tags = Tag.query.order_by(Tag.num_use.desc()).limit(500).all() #sort by num_use and limit to 200
    carInts = CareerInterest.query.order_by(CareerInterest.num_use.desc()).limit(500).all()
    schools = School.query.order_by(School.num_use.desc()).limit(500).all()
    return (tags, carInts, schools)


#Current file size limited to 5 MB - with free tier AWS (5GB S3) this limits to a minimum of 1024 images.
@app.route('/register', methods=['POST'])
def registerPost():

    form1 = request.form   
    
    success = True

    register_type = form1.get("radio_position") #student or mentor

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
    
    if form1.get('bio') == "":
        success = False
        flash(u'Your bio cannot be empty.', 'bioError')

    if form1.get('radio_contact') == 'Phone number' and form1.get('phoneNumber') == "": #user chose to be contacted by phone
        flash(u'Your phone number cannot be empty.', 'phoneError')
        success = False

    if register_type == None:
        success = False

    if form1.get('current_occupation') == '' and register_type=="mentor": #ok if blank if they're a student
        success = False
        flash(u'Please enter your current occupation.', 'currentOccupationError')
        errors.append("current_occupation")

    #remove cropping
    #if "croppedImgFile" in request.files:
        #img = request.files["croppedImgFile"]
    if "file" in request.files and request.files["file"]:
        img = request.files["file"]
        #remove cropping
        #if img and int((img.getbuffer().nbytes/1024)/1024) > 5:

        imgSize = -1
        if img:
            img.seek(0, os.SEEK_END)
            imgSize = img.tell()
            img.seek(0)
        
        if imgSize == -1:
            flash(u"Couldn't read image.", 'imageError')
            success = False
        elif (imgSize/1024)/1024 > 5:
            flash(u'Image is too big (max 5 MB).', 'imageError')
            success = False
        elif img.filename == '':
            flash(u'Could not read image', 'imageError')
            success = False
        else:
            imgType = validate_image(img.stream)
            if imgType == None:
                flash(u'Could not assess image size.', 'imageError')
            elif imgType not in json.loads(app.config['UPLOAD_EXTENSIONS']):
                flash(u'Accepted file types: .png, .jpg. You uploaded a', imgType + ".", 'imageError')
                success = False
    #image is optional
    """else:
        success = False
        flash(u'Please select a file.', 'pictureError')"""

    vid = None
    if "videoFile" in request.files:
        vid = request.files["videoFile"]
    
    #video file optional
    """else:
        success=False
        flash(u'Please select a file.', 'videoError')"""
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

    if success: #success, registering new user
        
        isStudent = True
        if register_type == "student":
            isStudent = True
        else: #== "mentor"
            isStudent = False

        user = User(email=form1.get('email'), first_name=form1.get('first_name'), last_name=form1.get('last_name'), 
                    is_student=isStudent, bio=form1.get('bio'), city_name=form1.get('city_name'), 
                    current_occupation=form1.get('current_occupation'), email_contact=True, phone_number=None)
        
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
            interestTag = InterestTag(
                user_id=user.id,
                entered_name=interestArr[i]
            )
            db.session.add(interestTag)
            db.session.commit() #I have to do this before I set the resource so the id will be set.
            interestTag.set_interestID(interestArr[i], db.session)

        #get education
        eduArr = form1.getlist("educationName")
        for i in range(int(form1.get('num_education_listings'))):
            educationTag = EducationTag(
                user_id=user.id,
                entered_name=eduArr[i]
            )
            db.session.add(educationTag)
            db.session.commit() #I have to do this before I set the resource so the id will be set.
            educationTag.set_educationID(eduArr[i], db.session)

        #get career interests
        cintArr = form1.getlist("careerInterestName")
        for i in range(int(form1.get('num_career_interests'))):
            cintTag = CareerInterestTag(
                user_id=user.id,
                entered_name=cintArr[i]
            )
            db.session.add(cintTag)
            db.session.commit() #I have to do this before I set the resource so the id will be set.
            cintTag.set_careerInterestID(cintArr[i], db.session)
        
        #remove cropping
        #if "croppedImgFile" in request.files:
            #img = request.files["croppedImgFile"]
        if "file" in request.files:
            img = request.files["file"]
            if img and request.files["file"]:
                output, filename = upload_file_to_s3(img, user)
                user.set_profile_picture(output, filename) #set the user profile picture link
                db.session.commit()

        if "videoFile" in request.files:
            vid = request.files["videoFile"]
            if vid:
                vid.seek(0) #I read the file before to check the length so I must put the cursor at the beginning in order to upload it.
                output, filename = upload_file_to_s3(vid, user)
                user.set_intro_video(output, filename) #set the user profile picture link
                db.session.commit()

        db.session.commit()

        return redirect(url_for('sign_in')) #success: get request to sign_in page
    else:
        return registerPreviouslyFilledOut(form1, errors)


def registerPreviouslyFilledOut(form, errors):

    email = form.get("email")
    first_name = form.get("first_name")
    last_name = form.get("last_name")
    bio = form.get("bio")
    email_or_phone = "email"
    phone_num = ""
    city_name = form.get("city_name")
    first_last_error = False
    current_occupation = form.get("current_occupation")

    if "email" in errors: #if error - make it blank.
        email = ""
    elif "city_name" in errors:
        city_name = ""
    elif "current_occupation" in errors:
        current_occupation = ""
    elif "first name" in errors:
        first_name = ""
    elif "last name" in errors:
        last_name = ""
        if "first name" in errors:
            first_last_error = True


    register_type = form.get("radio_position") #student or mentor
    #^v will be none if somehow they messed with it
    if form.get('radio_contact') == 'Phone number':
        email_or_phone = "phone"
        phone_num = form.get('phoneNumber')


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

    return render_template('register.html', email=email, first_name=first_name, last_name=last_name, first_last_error=first_last_error,
                bio=bio, city_name=city_name, current_occupation=current_occupation, email_or_phone=email_or_phone, 
                phone_num=phone_num, register_type=register_type,
                interestList=interestInputs, educationList=eduInputs, careerInterestList=carIntInputs,
                interestTags=interestTags, careerInterests=careerInterests, schools=schools, form=formNew)
    

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
    else:
        regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$' #if it isn't a valid email address
        if(not(re.search(regex,form1.get('email')))):
            flash('Invalid email address', 'emailError')
            success = False
            errors.append("email")
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
    
    if form1.get('city_name') == '':
        success = False
        flash(u'Please enter a city.', 'cityNameError')
        errors.append("city_name")
    
    return (success, errors)

#perhaps combine all these edit profiles into one and determine type of edit made based on input in html form
@app.route('/edit-profile', methods = ['GET'])
def editProfile():

    if not userLoggedIn():
        return redirect(url_for('sign_in'))

    user = User.query.filter_by(id=session.get('userID')).first() #get the correct profile by inputting user id

    formPwd = EditPasswordForm()
    formFn = EditFirstNameForm()
    formLn = EditLastNameForm()
    formCity = EditCityForm()
    formCurrentOccupation = EditCurrentOccupationForm()

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

    interestTags, careerInterests, schools = get_popular_tags()

    title="Edit profile Page"
    return render_template('edit_profile.html', isStudent=user.is_student, intro_video=intro_video_link, 
            contact_method=contact_method, phone_num=phone_num, profile_picture=prof_pic_link, 
            interestTags=interestTags, careerInterests=careerInterests, schools=schools, 
            title=title, bio=bio, interestList=interestList, careerInterestList=careerInterestList, educationList=educationList, 
            formPwd=formPwd, formFn=formFn, formLn=formLn, formCity=formCity, formCurrentOccupation=formCurrentOccupation,
            user=user, userID=session.get('userID'))

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

@app.route('/edit-profile-first-name', methods = ['POST'])
def editProfileFirstName():

    if not userLoggedIn():
        return redirect(url_for('sign_in'))

    success = True

    form = request.form

    if form.get('first_name') == '':
        success = False
        flash(u'Please enter a new first name.', 'firstNameError')
    if success: #did enter everything
        if form.get('first_name') == User.query.filter_by(id=session['userID']).first().first_name: #this is already the name
            success = False
            flash(u'That is already your first name.', 'firstNameError')

    if success:
        User.query.filter_by(id=session['userID']).first().set_first_name(form.get('first_name'))
        db.session.commit()
        return redirect(url_for('view', id=session.get('userID')))
    else: 
        return redirect(url_for('editProfile'))

@app.route('/edit-profile-last-name', methods = ['POST'])
def editProfileLastName():

    if not userLoggedIn():
        return redirect(url_for('sign_in'))

    success = True

    form = request.form

    if form.get('last_name') == '':
        success = False
        flash(u'Please enter a new last name.', 'lastNameError')
    if success: #did enter everything
        if form.get('last_name') == User.query.filter_by(id=session['userID']).first().last_name: #this is already the name
            success = False
            flash(u'That is already your last name.', 'lastNameError')

    if success:
        User.query.filter_by(id=session['userID']).first().set_last_name(form.get('last_name'))
        db.session.commit()
        return redirect(url_for('view', id=session.get('userID')))
    else: 
        return redirect(url_for('editProfile'))

@app.route('/edit-profile-city', methods = ['POST'])
def editProfileCityName():

    if not userLoggedIn():
        return redirect(url_for('sign_in'))

    success = True

    form = request.form

    if form.get('city_name') == '':
        success = False
        flash(u'Please enter a city name.', 'cityNameError')
    if success: #did enter everything
        if form.get('city_name') == User.query.filter_by(id=session['userID']).first().city_name: #this is already the name
            success = False
            flash(u'You already listed that as your current city.', 'cityNameError')

    if success:
        User.query.filter_by(id=session['userID']).first().set_city_name(form.get('city_name'))
        db.session.commit()
        return redirect(url_for('view', id=session.get('userID')))
    else: 
        return redirect(url_for('editProfile'))

@app.route('/edit-profile-current-occupation', methods = ['POST'])
def editProfileCurrentOccupation():

    if not userLoggedIn():
        return redirect(url_for('sign_in'))

    success = True

    form = request.form

    if form.get('current_occupation') == '':
        success = False
        flash(u'Please enter the name of your current occupation.', 'currentOccupationError')
    if success: #did enter everything
        if form.get('current_occupation') == User.query.filter_by(id=session['userID']).first().current_occupation: #this is already the name
            success = False
            flash(u'You already listed that as your current occupation.', 'currentOccupationError')

    if success:
        User.query.filter_by(id=session['userID']).first().set_current_occupation(form.get('current_occupation'))
        db.session.commit()
        return redirect(url_for('view', id=session.get('userID')))
    else: 
        return redirect(url_for('editProfile'))

@app.route('/edit-profile-attributes', methods = ['POST'])
def editProfileAttributes():

    if not userLoggedIn():
        return redirect(url_for('sign_in'))

    user = User.query.filter_by(id=session.get('userID')).first()

    form1 = request.form
    
    success = True

    if int(form1.get('num_tags')) == 0:
        success = False
        flash(u'Please enter at least one interest.', 'interestError')

    if int(form1.get('num_education_listings')) == 0:
        success = False
        flash(u'Please enter at least one school.', 'educationError')

    if int(form1.get('num_career_interests')) == 0:
        success = False
        if user.is_student:
            flash(u'Please enter at least one career interest.', 'careerInterestError')
        else:
            flash(u'Please enter at least one career experience.', 'careerInterestError')
    

    if success: #success, changing user's attributes
        
        #I want to register the new attributes - delete the old ones.
        delete_user_attributes(user.id)

        #get interests
        #I don't actually need num_tags since I can iterate thru getlist, 
        # but I can see it being useful/efficient for future features.
        #ok I'm just going to iterate through the list to protect against index out of bounds exceptions
        interestArr = form1.getlist("tagName")
        #for i in range(int(form1.get('num_tags'))):
        for i in range(len(interestArr)):
            interestTag = InterestTag(
                user_id=user.id,
                entered_name=interestArr[i]
            )
            db.session.add(interestTag)
            db.session.commit() #I have to do this before I set the resource so the id will be set.
            interestTag.set_interestID(interestArr[i], db.session)

        #get education
        eduArr = form1.getlist("educationName")
        #for i in range(int(form1.get('num_education_listings'))):
        for i in range(len(eduArr)):
            educationTag = EducationTag(
                user_id=user.id,
                entered_name=eduArr[i]
            )
            db.session.add(educationTag)
            db.session.commit() #I have to do this before I set the resource so the id will be set.
            educationTag.set_educationID(eduArr[i], db.session)

        #get career interests
        cintArr = form1.getlist("careerInterestName")
        #for i in range(int(form1.get('num_career_interests'))):
        for i in range(len(cintArr)):
            cintTag = CareerInterestTag(
                user_id=user.id,
                entered_name=cintArr[i]
            )
            db.session.add(cintTag)
            db.session.commit() #I have to do this before I set the resource so the id will be set.
            cintTag.set_careerInterestID(cintArr[i], db.session)

        db.session.commit()

    return redirect(url_for('editProfile')) #go back on either success or fail
    
@app.route('/edit-profile-position', methods = ['POST'])
def editProfilePosition():
    if not userLoggedIn():
        return redirect(url_for('sign_in'))
    user = User.query.filter_by(id=session.get('userID')).first()
    form = request.form
    if form.get('radio_isStudent') == 'mentor': #make the user a mentor
        user.set_isStudent(False) 
    else: #make user a student
        user.set_isStudent(True)
        #TODO: caution against doing this before checking matches and then delete all selects with this user as the base

    db.session.commit()
    return redirect(url_for('editProfile'))

@app.route('/edit-profile-bio', methods = ['POST'])
def editProfileBio():
    if not userLoggedIn():
        return redirect(url_for('sign_in'))
    user = User.query.filter_by(id=session.get('userID')).first()
    form = request.form
    if form.get('bio') == "":
        flash(u'Your bio cannot be empty.', 'bioError')
        return redirect(url_for('editProfile'))

    user.set_bio(form.get('bio'))
    db.session.commit()
    return redirect(url_for('editProfile'))

@app.route('/edit-profile-contact', methods = ['POST'])
def editProfileContact():
    if not userLoggedIn():
        return redirect(url_for('sign_in'))
    user = User.query.filter_by(id=session.get('userID')).first()
    form = request.form
    
    if form.get('radio_contact') == 'Phone number' and form.get('phoneNumber') == "": #user chose to be contacted by phone
        flash(u'Your phone number cannot be empty.', 'phoneError')
        return redirect(url_for('editProfile'))

    if form.get('radio_contact') == 'Email': #checked the email box
        user.remove_phone()
    
    if form.get('radio_contact') == 'Phone number':
        user.set_phone(form.get('phoneNumber'))

    db.session.commit()
    return redirect(url_for('editProfile'))

@app.route('/edit-profile-picture', methods=['POST'])
def editProfPic():
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))

    img = None
    success = True

    #remove cropping
    #if "croppedImgFile" in request.files:
        #img = request.files["croppedImgFile"]
    if "file" in request.files:
        img = request.files["file"]
    else:
        success=False
        flash(u'Please select a file.', 'pictureError')
    
    if img:
        #remove cropping
        """if int((img.getbuffer().nbytes/1024)/1024) > 5:
            flash(u'Image is too big (max 5 MB).', 'imageError')
            success = False"""
        

        imgSize = -1
        img.seek(0, os.SEEK_END)
        imgSize = img.tell()
        img.seek(0)
        
        if imgSize == -1:
            flash(u"Couldn't read image.", 'imageError')
            success = False
        elif (imgSize/1024)/1024 > 5:
            flash(u'Image is too big (max 5 MB).', 'imageError')
            success = False
        elif img.filename == '':
            flash(u'Could not read image', 'imageError')
            success = False
        else:
            imgType = validate_image(img.stream)
            if imgType == None:
                flash(u'Could not assess image size.', 'imageError')
            elif imgType not in json.loads(app.config['UPLOAD_EXTENSIONS']):
                flash(u'Accepted file types: .png, .jpg. You uploaded a ' + imgType + ".", 'imageError')
                success = False
    else:
        flash(u'Image could not be found.', 'imageError')
        success = False
    
    if success: 
        if img:
            user = User.query.filter_by(id=session.get('userID')).first()
            delete_profile_picture(user)
            output, filename = upload_file_to_s3(img, user)
            user.set_profile_picture(output, filename) #set the user profile picture link
            db.session.commit()
        else:
            success=False
            flash(u'Please select a file.', 'pictureError')

    return redirect(url_for('editProfile'))


@app.route('/delete-profile-picture', methods=['POST'])
def deleteProfPic():
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))
    
    user = User.query.filter_by(id=session.get('userID')).first()
    delete_profile_picture(user)

    return redirect(url_for('editProfile'))

@app.route('/delete-intro-video', methods=['POST'])
def deleteIntroVid():
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))
    
    user = User.query.filter_by(id=session.get('userID')).first()
    delete_intro_video(user)

    return redirect(url_for('editProfile'))


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
        output, filename = upload_file_to_s3(vid, user)
        user.set_intro_video(output, filename) #set the user profile picture link
        db.session.commit()

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

    this_user_is_logged_in = (user.id == session.get('userID'))
    in_network = False
    if Select.query.filter_by(mentee_id=user.id, mentor_id=session.get('userID')).first() != None or \
        Select.query.filter_by(mentee_id=session.get('userID'), mentor_id=user.id).first() != None:
        in_network = True

    #^if the user looking at this person's profile page is the one who is currently logged in, 
    # let them logout from or delete their account.
    title="Profile Page"
    return render_template('view.html', title=title, profile_picture=prof_pic_link, intro_video=intro_vid_link,
                bio=bio, in_network=in_network, logged_in=this_user_is_logged_in, 
                interestList=interestList, careerInterestList=careerInterestList, educationList=educationList, 
                isStudent=isStudent, user=user, userID=session.get('userID'))
    #user logged in: show profile page.

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
        Select.query.filter_by(mentee_id=user.id).delete()
        Select.query.filter_by(mentor_id=user.id).delete()
        

        User.query.filter_by(id=userID).delete()
        db.session.commit()

        return render_template('delete-profile-success.html')
    else:
        flash(u'Incorrect first name.', 'deletionError')
        return redirect(url_for('editProfile'))


def upload_file_to_s3(file_upload, user):
    filename = ""
    filename+=str(user.id)
    filename+="/"
    filename+=str(uuid4()) #safe file name: uuid4.
    s3_client.put_object(
        Bucket = str(app.config['BUCKET_NAME']),
        Key = filename,
        Body=file_upload,
        ACL=str(app.config['ACL']),
        ContentType = file_upload.content_type
    )
    output = 'https://s3-{}.amazonaws.com/{}/{}'.format(app.config['S3_REGION'], app.config['BUCKET_NAME'], filename)
    print(filename, output, file_upload.content_type)
    db.session.commit() #just in case
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


@app.route('/feed', methods=['GET'])
def feed():
    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))
    
    user = User.query.filter_by(id=session.get('userID')).first()
    return render_template('feed.html', isStudent=user.is_student, userID=session.get('userID'))


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

    schoolDict = {} #contains all the matching schools for each user (user : [school])
    for educ in user.rtn_education():
        school = School.query.filter_by(title=educ.entered_name.lower()).first() #the school with this title - should only be one
        if school != None:  #Extra check if the school entered might not be in the database. It won't, but better safe than sorry.
                            #Data is entered automatically - it will have to be in the database to be searched
            educationTags = EducationTag.query.filter_by(educationID=school.id).all() 
            #TODO: I should be able to skip query for school and do educationID=educ.educationID
            #has the EducationTags that are linked to this school's name
            for edTag in educationTags:
                users = User.query.filter_by(id=edTag.user_id).all() #get the corresponding users
                for u in users:
                    if u.id != user.id and not u.is_student and not mentorSelected(u.id): #don't consider the user logged in - also, only recommend mentors
                        if schoolDict.__contains__(u): #add user to the dict
                            schoolDict[u].append(edTag.entered_name)
                        else:
                            sArr = [edTag.entered_name] #not already in the dict --> add a new array
                            schoolDict[u] = sArr

                        if userDict.__contains__(u): #now update match amount in user dict
                            userDict[u] = userDict[u]+heuristicVals["education"]
                        else:
                            userDict[u] = heuristicVals["education"] #initialize
    

    interestTitleDict = {} #contains all the matching tags for each user (user : [interest tag titles])
    for intrst in user.rtn_interests():
        tag = Tag.query.filter_by(title=intrst.entered_name.lower()).first()
        if tag != None:  #Extra check if the school entered might not be in the database. It won't, but better safe than sorry.
                            #Data is entered automatically - it will have to be in the database to be searched
            #interestTags = InterestTag.query.filter_by(interestID=tag.tagID).all() 
            interestTags = InterestTag.query.filter_by(interestID=tag.id).all() 
            #has the EducationTags that are linked to this school's name
            for intT in interestTags:
                users = User.query.filter_by(id=intT.user_id).all() #get the corresponding users
                for u in users:
                    if u.id != user.id and not u.is_student and not mentorSelected(u.id): #don't consider the user logged in
                        if interestTitleDict.__contains__(u): #add user to the dict
                            interestTitleDict[u].append(intT.entered_name)
                        else:
                            #show the non-lowercase version
                            tArr = [intT.entered_name] #not already in the dict --> add a new array
                            interestTitleDict[u] = tArr

                        if userDict.__contains__(u): #now update match amount in user dict
                            userDict[u] = userDict[u]+heuristicVals["interest"]
                        else:
                            userDict[u] = heuristicVals["interest"] #initialize

    careerDict = {} #contains all the matching career tags for each user (user : [career experience/interest title])
    for careerInt in user.rtn_career_interests():
        career = CareerInterest.query.filter_by(title=careerInt.entered_name.lower()).first()
        if career != None: #Extra check if the school entered might not be in the database. It won't, but better safe than sorry.
                            #Data is entered automatically - it will have to be in the database to be searched
            #cInts = CareerInterestTag.query.filter_by(careerInterestID=career.careerInterestID).all() 
            cInts = CareerInterestTag.query.filter_by(careerInterestID=career.id).all() 
            #has the EducationTags that are linked to this school's name
            for cInt in cInts:
                users = User.query.filter_by(id=cInt.user_id).all() #get the corresponding users
                for u in users:
                    if u.id != user.id and not u.is_student and not mentorSelected(u.id): 
                        #don't consider the user logged in, only consider students, don't consider users who have already been shown to this student.
                        if careerDict.__contains__(u): #add user to the dict
                            careerDict[u].append(cInt.entered_name)
                        else:
                            #show the non-lowercase version
                            cArr = [cInt.entered_name] #not already in the dict --> add a new array
                            careerDict[u] = cArr

                        if userDict.__contains__(u): #now update match amount in user dict
                            userDict[u] = userDict[u]+heuristicVals["career"]
                        else:
                            userDict[u] = heuristicVals["career"] #initialize


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

    return jsonify(dictItems)


def mentorSelected(mentorId): #if this mentor has been selected already
    if Select.query.filter_by(mentor_id=mentorId).first() != None:
        return True
    return False


@app.route('/feed', methods=['POST'])
def feedPost():
    #A mentee chose a mentor --> post the form with the mentor information

    if not(userLoggedIn()):
        flash(u'You must log in.', 'loginRedirectError')
        return redirect(url_for('sign_in'))

    form = request.form

    if form.get('userID') == None:
        flash(u'Something went wrong.', 'feedError')
        return redirect(url_for('feed'))
    
    userMatchID = form.get('userID')

    newSelect = Select(mentee_id=session.get('userID'), mentor_id=userMatchID)
    #selection will only be made by the user logged in - the mentee.

    db.session.add(newSelect)
    db.session.commit()
    
    return redirect(url_for("my_connections"))


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
    return render_template('csrf_error.html', reason=e.description), 400

@app.errorhandler(404)
# inbuilt function which takes error as parameter
def not_found(e):
    # defining function
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
    
    return render_template("general_error.html", code=code)
