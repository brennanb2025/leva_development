from app.input_sets.models import User, Tag, InterestTag, EducationTag, School, CareerInterest, \
        CareerInterestTag, Select, Business, Event, ProgressMeeting, ProgressMeetingCompletionInformation, \
        UserFeedWeights

from app import app, db

import os
import json
import imghdr

import app.model.AWS as AWS
import app.model.userUtilities as utilities

#returns (tags, careerInterests, schools) - the 500 most used tags from each category.
def get_popular_tags(): 
    tags = Tag.query.order_by(Tag.num_use.desc()).limit(500).all() #sort by num_use and limit to 200
    carInts = CareerInterest.query.order_by(CareerInterest.num_use.desc()).limit(500).all()
    schools = School.query.order_by(School.num_use.desc()).limit(500).all()
    return (tags, carInts, schools)



def registerValidate1(email):
    errors = {}
    success = True
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

    return success, errors


def registerValidate2(business):
    errors = {}
    success = True
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

    return success, errors


class register_post_response:
    def __init__(self):
        self.emailError_email_taken = False
        self.emailError_email_not_entered = False
        self.firstNameError = False
        self.lastNameError = False
        self.passwordError = False
        self.passwordReenterError_not_entered = False
        self.passwordReenterError_do_not_match = False
        self.divisionError = False
        self.cityNameError = False
        self.numPairingsError_not_entered = False
        self.numPairingsError_zero = False
        self.numPairingsError_non_integer = False
        self.bioError = False

        self.interestError = False
        self.educationError = False
        self.careerInterestError = False
        self.phoneError = False
        self.mentorPreferenceError = False
        self.genderIdentityError = False
        self.divisionPreferenceError = False
        self.personalityError = False
        self.currentOccupationError = False
        self.businessError_not_entered = False
        self.businessError_not_registered = False
        self.businessError_spots_filled = False
        self.resumeError_unreadable = False
        self.resumeError_too_big = False
        self.resumeError_file_type_not_found = False
        self.resumeError_bad_file_type = False
        self.resumeError_bad_file_type_message = ""
        self.imageError_unknown_size = False
        self.imageError_bad_file_type = False
        self.imageError_bad_file_type_message = ""


#TODO: add data from sliders
def registerPost(form, resume, img):

    resp = register_post_response()

    if form.get("radio_mentor_mentee") == "mentee":
        isMentee = True
    else: #== "mentor"
        isMentee = False

    (success, errors, resp) = checkBasicInfo(form, resp)

    if int(form.get('num_tags')) == 0:
        success = False
        resp.interestError = True
        #flash(u'Please enter at least one interest.', 'interestError')
        errors.append("num_tags")

    if int(form.get('num_education_listings')) == 0:
        success = False
        resp.educationError = True
        #flash(u'Please enter at least one school.', 'educationError')
        errors.append("num_education_listings")

    if int(form.get('num_career_interests')) == 0:
        success = False
        resp.careerInterestError = True
        #flash(u'Please enter at least one career interest.', 'careerInterestError')
        errors.append("num_career_interests")

    if form.get('radio_contact') == 'Phone number' and form.get('phoneNumber') == "": #user chose to be contacted by phone
        resp.phoneError = True
        #flash(u'Your phone number cannot be empty.', 'phoneError')
        success = False

    if isMentee == None:
        success = False

    # if the user submitted the request through the webpage, these sliders should have default values.
    if (not form.get("personalitySlider") or not form.get("interestSlider")
            or not form.get("careerSlider") or not form.get("educationSlider")
            or not form.get("genderSlider")):
        success = False

    if str(app.config['MATCHING_FLAG_MENTOR_GENDER_PREFERENCE']) == "True": #if gender preference should be taken into account, check it.
        if isMentee and form.get("radio_gender_preference") == None: #mentee and mentor preference empty
            resp.mentorPreferenceError = True
            #flash(u"Please enter a preference for your mentor's gender.", 'mentor_preference_error')
            success = False
        if not isMentee and form.get("radio_gender_identity") == None: #mentor and gender identity not entered
            resp.genderIdentityError = True
            #flash(u"Please enter your gender identity.", 'gender_identity_error')
            success = False
    
    """
    if str(app.config['MATCHING_FLAG_DIVISION_PREFERENCE']) == "True": #if division preference should be taken into account, check it.
        if form.get("divisionPreference") == None: #mentee and mentor division preference empty or mentor and mentee division preference empty
            resp.divisionPreferenceError = True
            #flash(u"Please enter a preference for your division.", 'division_preference_error')
            success = False
    """

    if str(app.config['MATCHING_FLAG_PERSONALITY']) == "True": #if personality should be taken into account, check it.
        if form.get('personality1') != None and form.get('personality2') != None and form.get('personality3') != None:
            if form.get('personality1').strip() == "" or form.get('personality2').strip() == "" or form.get('personality3').strip() == "":
                resp.personalityError = True
                #flash(u"Please enter three words or phrases that describe you.", 'personality_error')
                success = False
        else:
            resp.personalityError = True
            #flash(u"Please enter three words or phrases that describe you.", 'personality_error')
            success = False


    """
    if form.get('current_occupation') == '':
        success = False
        resp.currentOccupationError = True
        #flash(u'Please enter your current occupation.', 'currentOccupationError')
        errors.append("current_occupation")
    """


    if form.get('business') == '' or form.get('business') == None:
        success = False
        resp.businessError_not_entered = True
        #flash(u'Please enter the company you are a part of.', 'businessError')
    else:
        businessRegisteredUnder = Business.query.filter_by(name=form.get('business')).first()
        if businessRegisteredUnder == None: #business doesn't exist in database
            success = False
            resp.businessError_not_registered = True
            #flash(u'That business is not registered.', 'businessError') 
        else:
            if businessRegisteredUnder.number_employees_maximum == businessRegisteredUnder.number_employees_currently_registered:
                #every spot is taken in this business. 
                success = False
                resp.businessError_spots_filled = True
                #flash(u'That business has no spots left for more users.', 'businessError')

    #resume pdf
    if resume:
        #remove cropping
        #if img and int((img.getbuffer().nbytes/1024)/1024) > 5:

        resumeSize = -1
        if resume:
            resume.seek(0, os.SEEK_END)
            resumeSize = resume.tell()
            resume.seek(0)
        
        if resumeSize == -1:
            resp.resumeError_unreadable = True
            #flash(u"Couldn't read resume.", 'resumeError')
            success = False
        elif (resumeSize/1024)/1024 > 5:
            resp.resumeError_too_big = True
            #flash(u'Resume is too big (max 5 MB).', 'resumeError')
            success = False
        elif resume.filename == '':
            resp.resumeError_unreadable = True
            #flash(u'Could not read resume', 'resumeError')
            success = False
        else:
            file_ext = os.path.splitext(resume.filename)[1]
            if file_ext == None:
                success = False
                resp.resumeError_file_type_not_found = True
                #flash(u"Could not assess file type properties", 'resumeError')
            elif file_ext not in json.loads(app.config['UPLOAD_EXTENSIONS_RESUME']):
                resp.resumeError_bad_file_type = True
                resp.resumeError_bad_file_type_message = 'Accepted file type: .pdf. You uploaded a', file_ext + "."
                #flash(u'Accepted file type: .pdf. You uploaded a', file_ext + ".", 'resumeError')
                success = False
    #else: didn't input a resume. That's ok, they're optional.

    #if "file" in request.files and request.files["file"]:
    #errorMsg = ""

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
        """if img.filename == '':
            errorMsg = errorMsg + "[Could not read image filename]"
            flash(u'Could not read image filename', 'imageError')
            success = False
        else:"""

        #TODO: Do I check for image size?
        imgType = utilities.validate_image(img.stream)
        if imgType == None:
            #errorMsg = errorMsg + "[Could not assess image size]"
            #flash(u'Could not assess image size.', 'imageError')
            resp.imgError_unknown_size = True
            success = False
        elif imgType not in json.loads(app.config['UPLOAD_EXTENSIONS']):
            #errorMsg = errorMsg + "[Wrong image type]"
            #flash(u'Accepted file types: .png, .jpg. You uploaded a ' + imgType + ".", 'imageError')
            resp.imageError_bad_file_type = True
            resp.imageError_bad_file_type_message = 'Accepted file types: .png, .jpg. You uploaded a ' + imgType + "."
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

        mentor_gender_preferenceForm = form.get("radio_gender_preference")
        if not isMentee: #or str(app.config['MATCHING_FLAG_MENTOR_GENDER_PREFERENCE']) == "False":
            mentor_gender_preferenceForm = None #if mentor OR gender should not be taken into account, this should not be entered.

        gender_identityForm = form.get("radio_gender_identity")
        if isMentee: #or str(app.config['MATCHING_FLAG_MENTOR_GENDER_PREFERENCE']) == "False":
            gender_identityForm = None #if mentee, this should not be entered.

        #changed division form to be 1:Freshman, 2:Sophomore, etc.
        #TODO undid this change
        
        #division_set = form.get('division').strip()
        """
        if division_set == "1":
            division_set = "Freshman"
        elif division_set == "2":
            division_set = "Sophomore"
        elif division_set == "3":
            division_set = "Junior"
        else:
            division_set = "Senior"
        """

        #division_preference_set = form.get("divisionPreference")
        #if str(app.config['MATCHING_FLAG_DIVISION_PREFERENCE']) == "False":
            #if division preference should not be taken into account, set it to None
            #division_preference_set = None

        personality_1_set = personality_2_set = personality_3_set = None
        #if str(app.config['MATCHING_FLAG_PERSONALITY']) == "True":
        personality_1_set = form.get("personality1").strip()
        personality_2_set = form.get("personality2").strip()
        personality_3_set = form.get("personality3").strip()

        businessRegisteredUnder = Business.query.filter_by(name=form.get('business')).first()
        businessRegisteredUnder.inc_number_employees_currently_registered() #increment number of users registered for this user

        user = User(email=form.get('email'), first_name=form.get('first_name'), last_name=form.get('last_name'), 
                    is_student=isMentee, bio=form.get('bio'), email_contact=True, phone_number=None,
                    #city_name=form.get('city_name'), current_occupation=form.get('current_occupation'),
                    business_id=businessRegisteredUnder.id, 
                    num_pairings_can_make=int(form.get('num_pairings')) if not isMentee else 1, # hard set to 1 if mentee
                    mentor_gender_preference=mentor_gender_preferenceForm,
                    gender_identity=gender_identityForm,
                    #division_preference=division_preference_set, division=division_set,
                    personality_1=personality_1_set, personality_2=personality_2_set,
                    personality_3=personality_3_set)
        
        db.session.add(user) #add to database
        user.set_password(form.get('password')) #must set pwd w/ hashing method
        db.session.commit()

        if form.get('radio_contact') == 'Phone number': #set phone number
            user.set_phone(form.get('phoneNumber'))

        #get interests
        #I don't actually need num_tags since I can not iterate thru getlist, 
        # but I can see it being useful/efficient for future features.
        interestArr = form.getlist("tagName")
        for i in range(int(form.get('num_tags'))):
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
        for i in range(int(form.get('num_education_listings'))):
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
        for i in range(int(form.get('num_career_interests'))):
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
        if img:
            output, filename = AWS.upload_media_file_to_s3(img, user)
            user.set_profile_picture(output, filename) #set the user profile picture link
            db.session.commit()

        """if "videoFile" in request.files:
            vid = request.files["videoFile"]
            if vid:
                vid.seek(0) #I read the file before to check the length so I must put the cursor at the beginning in order to upload it.
                output, filename = upload_media_file_to_s3(vid, user)
                user.set_intro_video(output, filename) #set the user profile picture link
                db.session.commit()"""

        if resume:
            resume.seek(0) #I read the file before to check the length so I must put the cursor at the beginning in order to upload it.
            output, filename = AWS.upload_resume_file_to_s3(resume, user)
            user.set_resume(output, filename) #set the user resume
            db.session.commit()


        addFeedWeight(user.id, personality=form.get("personalitySlider"), 
                mentor_gender_preference=form.get("genderSlider"),
                interests=form.get("interestSlider"), career_interests=form.get("careerSlider"),
                education=form.get("educationSlider"))

        db.session.commit()


    return success, errors, resp
    


# weights are all on a 0-10 scale
def addFeedWeight(id, personality, mentor_gender_preference, interests, career_interests, education):
    newWeights = UserFeedWeights(user_id=id, personality=personality, 
            mentor_gender_preference=mentor_gender_preference,
            interests=interests, career_interests=career_interests, education=education)

    db.session.add(newWeights)
    db.session.commit()
    

    #checks the basic registration information.
def checkBasicInfo(form, resp):
    errors = []
    success = True
    if User.query.filter_by(email=form.get('email')).first() != None: #email taken
        success = False
        resp.emailError_email_taken = True
        #flash(u'Email taken. Please enter a different email.', 'emailError')
        errors.append("email")
    if form.get('email') == '':
        success = False
        resp.emailError_email_not_entered = True
        #flash(u'Please enter an email.', 'emailError')
        errors.append("email")
    """else:
        regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$' #if it isn't a valid email address
        if(not(re.search(regex,form.get('email')))):
            flash('Invalid email address', 'emailError')
            success = False
            errors.append("email")"""
    if form.get('first_name') == '':
        success = False
        resp.firstNameError = True
        #flash(u'Please enter a first name.', 'first_nameError')
        errors.append("first name")
    if form.get('last_name') == '':
        success = False
        resp.lastNameError = True
        #flash(u'Please enter a last name.', 'last_nameError')
        errors.append("last name")
    if form.get('password') == '':
        success = False
        resp.passwordError = True
        #flash(u'Please enter a password.', 'passwordError')
        #errors.append("password") not used for anything - passwords are wiped anyway
    if form.get('password2') == '':
        success = False
        resp.passwordReenterError_not_entered
        #flash(u'Please reenter your password.', 'password2Error')
        #errors.append("password") not used for anything - passwords are wiped anyway
    if success: #did enter everything
        if form.get('password') != form.get('password2'): #passwords don't match
            success = False
            resp.passwordReenterError_do_not_match = True
            #flash(u'Passwords do not match.', 'password2Error')
            #errors.append("password") not used for anything - passwords are wiped anyway

    """
    if form.get('division') == '':
        success = False
        resp.divisionError = True
        #flash(u'Please enter your division within the company.', 'division_error')
        errors.append("division")
    
    if form.get('city_name') == '':
        success = False
        resp.cityNameError = True
        #flash(u'Please enter a city.', 'cityNameError')
        errors.append("city_name")
    """
    
    if form.get('num_pairings') == '':
        success = False
        resp.numPairingsError_not_entered = True
        #flash(u'Please enter the amount of mentors/mentees you are willing to have.')
        errors.append("num_pairings")
    else:
        if form.get('num_pairings') == '0':
            success = False
            resp.numPairingsError_zero = True
            #flash(u'The number of mentors/mentees you are willing to have cannot be 0.')
            errors.append("num_pairings")
        else:
            try:
                int(form.get('num_pairings')) #try to parse the int field
            except:
                success = False
                resp.numPairingsError_non_integer = True
                #flash(u'The number of mentors/mentees you are willing to have must be an integer.')
                errors.append("num_pairings")

    if form.get('bio') == '':
        success = False
        resp.bioError = True
        #flash(u'Your bio cannot be empty.', 'bioError')
        errors.append("bio")

    return (success, errors, resp)