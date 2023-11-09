"""
Functions to add:
sign_inPost

"""


from app.input_sets.models import User, Tag, InterestTag, EducationTag, School, CareerInterest, \
        CareerInterestTag, Select, Business, Event, ProgressMeeting, \
        ProgressMeetingCompletionInformation, AdminUser


class sign_in_post_response:
    def __init__(self):
        self.email_not_entered = False
        self.password_not_entered = False
        self.email_not_found = False
        self.incorrect_password = False

def sign_in_post(email, password):
    success = True
    resp = sign_in_post_response()
    if email == "": #no email entered
        success = False
        resp.email_not_entered = True
    if password == "": #no password entered
        resp.password_not_entered = True
        success = False
    if success: #they entered an email and password - now check them
        if User.query.filter_by(email=email).first() == None: #email entered but not found
            success = False
            resp.email_not_found = True
        elif not User.query.filter_by(email=email).first().check_password(password): #email and password do not match
            resp.incorrect_password = True
            success = False

    return success, resp



def admin_login_post(email, password):
    success = True
    resp = sign_in_post_response()
    if email == "": #no email entered
        success = False
        resp.email_not_entered = True
    if password == "": #no password entered
        resp.password_not_entered = True
        success = False
    if success: #they entered an email and password - now check them
        adminUser = AdminUser.query.filter_by(email=email).first()
        if adminUser == None: #email entered but not found
            success = False
            resp.email_not_found = True
        elif not adminUser.check_password(password): #email and password do not match
            resp.incorrect_password = True
            success = False

    return success, resp