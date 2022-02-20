#This file contains information about the database schema.

from app import db, Base
#from sqlalchemy import DateTime, Float, Boolean, ForeignKey
#from sqlalchemy.orm import relationship
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model, Base): #inherits from db.Model, base for flask-SQLAlchemy
    #class User(UserMixin):

    __tablename__ = "User"
    
    id = db.Column(db.Integer, primary_key=True) #id = primary key
    email = db.Column(db.String(64), index=True, unique=True) #defined as strings, max length = ().
    password_hash = db.Column(db.String(128)) #not storing plaintext pwd, hashing first.
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    is_student = db.Column(db.Boolean) #T = mentee, F = mentor. Made this back when it was students/mentors. Now it should be mentees/mentors.
    bio = db.Column(db.Text)
    profile_picture = db.Column(db.Text)
    profile_picture_key = db.Column(db.Text)
    intro_video = db.Column(db.Text)
    intro_video_key = db.Column(db.Text)
    resume = db.Column(db.Text)
    resume_key = db.Column(db.Text)
    email_contact = db.Column(db.Boolean) #true: contact with email. False: contact with phone number
    phone_number = db.Column(db.String(64))
    city_name = db.Column(db.String(128))
    current_occupation = db.Column(db.String(128))
    business_id = db.Column(db.Integer) #the business that this person is registered under
    
    #new stuff:
    mentor_gender_preference = db.Column(db.Text)
    #this is either male, female, or noPreference

    gender_identity = db.Column(db.Text)
    #this is either male, female, nonbinaryNonconforming, or noResponse

    division_preference = db.Column(db.Text)
    #this is either same, different, or noPreference

    personality_1 = db.Column(db.Text)
    personality_2 = db.Column(db.Text)
    personality_3 = db.Column(db.Text)

    division = db.Column(db.Text)
    

 
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    interests = db.relationship(
        'InterestTag',
        backref='User', 
        lazy='dynamic',
        primaryjoin="InterestTag.user_id == User.id" 
    )

    career_interests = db.relationship(
        'CareerInterestTag',
        backref='User', 
        lazy='dynamic',
        primaryjoin="CareerInterestTag.user_id == User.id" 
    )

    education = db.relationship(
        'EducationTag',
        backref='User', 
        lazy='dynamic',
        primaryjoin="EducationTag.user_id == User.id" 
    )


    def rtn_interests(self):
        arr = []
        for interest in self.interests:
            arr.append(interest)
        return arr

    def rtn_education(self):
        arr = []
        for educ in self.education:
            arr.append(educ)
        return arr

    def rtn_career_interests(self):
        arr = []
        for cint in self.career_interests:
            arr.append(cint)
        return arr

    #in case user wants to change profile
    def set_first_name(self, first_name): 
        self.first_name = first_name

    def set_last_name(self, last_name):
        self.last_name = last_name

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def set_isStudent(self, isStudent):
        self.is_student=isStudent

    def set_bio(self, bio):
        self.bio=bio

    def set_city_name(self, city_name):
        self.city_name=city_name
    
    def set_current_occupation(self, current_occupation):
        self.current_occupation = current_occupation

    def set_division(self, division):
        self.division=division

    def set_phone(self, phoneNumber):
        self.phone_number=phoneNumber
        self.email_contact=False

    def remove_phone(self):
        self.phone_number=None
        self.email_contact=True
    
    def set_profile_picture(self, pictureLink, pictureKey):
        self.profile_picture=pictureLink
        self.profile_picture_key=pictureKey

    def set_intro_video(self, videoLink, videoKey):
        self.intro_video=videoLink
        self.intro_video_key=videoKey
    
    def set_resume(self, resumeLink, resumeKey):
        self.resume=resumeLink
        self.resume_key=resumeKey

    def set_personality(self, personality1, personality2, personality3):
        self.personality_1 = personality1
        self.personality_2 = personality2
        self.personality_3 = personality3

    def set_division_preference(self, division_preference):
        self.division_preference = division_preference

    def set_mentor_gender_preference(self, mentor_gender_preference):
        self.mentor_gender_preference = mentor_gender_preference
        
    def set_gender_identity(self, gender_identity):
        self.gender_identity = gender_identity

    def check_password(self, password):
        return check_password_hash(self.password_hash, password) #<^=pwd hashing logic
    
    def __repr__(self):
        return '<User {}>'.format(self.email + " " + self.first_name + " " + self.last_name) #how to print database


class InterestTag(db.Model, Base):

    __tablename__ = "InterestTag"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    entered_name = db.Column(db.String(64)) #the name that the user entered (with capital letters)
    #I don't know exactly why this foreign key shouldn't be in quotes
    interestID = db.Column(db.Integer)
    
    #this doesn't work - says no foreign key
    """tag = db.relationship(
        'Tag',
        backref='InterestTag', 
        lazy='dynamic',
        primaryjoin="Tag.tagID == InterestTag.interestID"
    )"""

    def delete_inc(self):
        searchTag = Tag.query.filter_by(title=self.entered_name.lower()).first() #will exist
        searchTag.dec_num_use()

    def set_interestID(self, tagName, session): #must check for duplicates, else add new tag
        searchTag = Tag.query.filter_by(title=tagName.lower()).first()
        if searchTag == None: #this tag does not yet exist
            t1 = Tag(title=tagName.lower(), num_use=0) #set actual tag saved to lowercase
            session.add(t1)
            session.commit() #have to do this before for the id to set
            """t1.set_tagID()
            session.commit()
            self.interestID = t1.tagID #set this tag to correspond to tag in database"""
            self.interestID = t1.id
            t1.inc_num_use()
            session.commit()
        else:
            #self.interestID = searchTag.tagID
            self.interestID = searchTag.id
            searchTag.inc_num_use()
            session.commit()

class Tag(db.Model, Base):

    __tablename__ = "Tag"

    id = db.Column(db.Integer, primary_key=True)
    #tagID = db.Column(db.Integer, db.ForeignKey("InterestTag.id"))
    #I'm using a column tagID that will always be the same as the id because the primary key can't be the foreign key.
    title = db.Column(db.String(64))
    num_use = db.Column(db.Integer)

    """def set_tagID(self): #this is stupid
        self.tagID = self.id"""
    
    def inc_num_use(self):
        self.num_use = self.num_use+1
    
    def dec_num_use(self):
        self.num_use = self.num_use-1


class EducationTag(db.Model, Base):

    __tablename__ = "EducationTag"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    entered_name = db.Column(db.String(64)) #the name that the user entered (with capital letters)
    #I don't know exactly why this foreign key shouldn't be in quotes
    educationID = db.Column(db.Integer)

    def delete_inc(self):
        searchSchool = School.query.filter_by(title=self.entered_name.lower()).first() #will exist
        searchSchool.dec_num_use()

    def set_educationID(self, schoolName, session): #must check for duplicates, else add new tag
        searchSchool = School.query.filter_by(title=schoolName.lower()).first()
        if searchSchool == None: #this tag does not yet exist
            s1 = School(title=schoolName.lower(), num_use=0)
            session.add(s1)
            session.commit() #have to do this before for the id to set
            """s1.set_schoolID()
            session.commit()
            self.educationID = s1.schoolID #set this tag to correspond to tag in database"""
            self.educationID = s1.id
            s1.inc_num_use()
            session.commit()
        else:
            #self.educationID = searchSchool.schoolID
            self.educationID = searchSchool.id
            searchSchool.inc_num_use()
            session.commit()
        
class School(db.Model, Base):

    __tablename__ = "School"

    id = db.Column(db.Integer, primary_key=True)
    #schoolID = db.Column(db.Integer, db.ForeignKey("EducationTag.id"))
    #I'm using a column tagID that will always be the same as the id because the primary key can't be the foreign key.
    title = db.Column(db.String(64))
    num_use = db.Column(db.Integer)

    """def set_schoolID(self): #this is stupid
        self.schoolID = self.id"""
        
    def inc_num_use(self):
        self.num_use = self.num_use+1
    
    def dec_num_use(self):
        self.num_use = self.num_use-1


class CareerInterestTag(db.Model, Base):

    __tablename__ = "CareerInterestTag"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    entered_name = db.Column(db.String(64)) #the name that the user entered (with capital letters)
    #I don't know exactly why this foreign key shouldn't be in quotes
    careerInterestID = db.Column(db.Integer)

    def delete_inc(self):
        searchCInts = CareerInterest.query.filter_by(title=self.entered_name.lower()).first() #will exist
        searchCInts.dec_num_use()

    def set_careerInterestID(self, cintName, session): #must check for duplicates, else add new tag
        searchCInts = CareerInterest.query.filter_by(title=cintName.lower()).first()
        if searchCInts == None: #this tag does not yet exist
            ci1 = CareerInterest(title=cintName.lower(), num_use=0)
            session.add(ci1)
            session.commit() #have to do this before for the id to set
            """ci1.set_careerInterestID()
            session.commit()
            self.careerInterestID = ci1.careerInterestID #set this tag to correspond to tag in database"""
            self.careerInterestID = ci1.id 
            ci1.inc_num_use()
            session.commit()
        else:
            #self.careerInterestID = searchCInts.careerInterestID
            self.careerInterestID = searchCInts.id
            searchCInts.inc_num_use()
            session.commit()
        

class CareerInterest(db.Model, Base):

    __tablename__ = "CareerInterest"

    id = db.Column(db.Integer, primary_key=True)
    #careerInterestID = db.Column(db.Integer, db.ForeignKey("CareerInterestTag.id"))
    #I'm using a column tagID that will always be the same as the id because the primary key can't be the foreign key.
    title = db.Column(db.String(64))
    num_use = db.Column(db.Integer)

    """def set_careerInterestID(self): #this is stupid
        self.careerInterestID = self.id"""
            
    def inc_num_use(self):
        self.num_use = self.num_use+1
    
    def dec_num_use(self):
        self.num_use = self.num_use-1


class Select(db.Model, Base):
    __tablename__ = "Select"

    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer)
    mentee_id = db.Column(db.Integer)

    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


#Business stores information about each business that has registered users and how many users are currently registered under each one.
class Business(db.Model, Base):
    __tablename__ = "Business"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    number_employees_maximum = db.Column(db.Integer)
    number_employees_currently_registered = db.Column(db.Integer)

    def inc_number_employees_currently_registered(self):
        self.number_employees_currently_registered = self.number_employees_currently_registered+1
    
    def dec_number_employees_currently_registered(self):
        self.number_employees_currently_registered = self.number_employees_currently_registered-1



class Event(db.Model, Base):
    __tablename__ = "Event"

    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer)
    action = db.Column(db.Integer)
    # 0: register page get
    # 1: error on register page post --> redirected back to register page
    # 2: register page post success
    # 3: log in post failure
    # 4: log in post success
    # 5: edit profile get
    # 6: edit profile post error
    # 7: edit profile post success
    # 8: upload file to s3
    # 9: view own profile
    # 10: view other profile
    # 11: logout
    # 12: delete profile
    # 13: get feed (# of matches sent over, 3 highest matches)
    # 14: post feed (rank of mentor match, number value of match)
    # 15: progress view
    # 16: error (message)
    # 17: CSRF error (message)

    message = db.Column(db.String(1024)) #json - use y = json.loads(message) to get it back.

    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Event {}>'.format(str(self.userID) + " " + str(self.action) + " " + self.message) #how to print database