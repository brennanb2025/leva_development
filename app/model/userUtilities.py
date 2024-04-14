import imghdr
import app.model.AWS as AWS

#ensures that the image is valid.
def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

def format_user_as_json(user):
    mentor_gender_pref = user.mentor_gender_preference
    if mentor_gender_pref == "noPreference":
        mentor_gender_pref = "No preference"
    gender_identity = user.gender_identity
    if gender_identity == "nonbinaryNonconforming":
        gender_identity = "Non-binary/non-conforming"
    elif gender_identity == "noResponse":
        gender_identity = "No response"
    return {
            "id":user.id,
            "email":user.email,
            "first_name":user.first_name,
            "last_name": user.last_name,
            "is_mentee": user.is_student,
            "bio": user.bio,
            "profile_picture": user.profile_picture, #the one used for displaying
            "resume": AWS.create_resume_link(user),
            "email_contact": user.email_contact, #true: contact with email. False: contact with phone number
            "phone_number": user.phone_number,
            #"city_name": user.city_name,
            #"current_occupation": user.current_occupation, #pretty sure not in use anymore
            "num_pairings_can_make": user.num_pairings_can_make,
            "mentor_gender_preference": mentor_gender_pref,
            "gender_identity": gender_identity,
            #"division_preference": user.division_preference,
            "personality_1": user.personality_1,
            "personality_2": user.personality_2,
            "personality_3": user.personality_3,
            #"division": user.division,
            "interests": [i.entered_name for i in user.rtn_interests()],
            "career_interests": [i.entered_name for i in user.rtn_career_interests()],
            "education": [i.entered_name for i in user.rtn_education()]
        }

def format_weights_as_json(weights):
    if not weights:
        return {
            "personality":1,
            "mentor_gender_preference":1,
            "interests":1,
            "career_interests":1,
            "education":1
        }
    return {
            "personality":weights.personality,
            "mentor_gender_preference":weights.mentor_gender_preference,
            "interests":weights.interests,
            "career_interests":weights.career_interests,
            "education": weights.education
        }