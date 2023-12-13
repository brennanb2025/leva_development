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
            "city_name": user.city_name,
            "current_occupation": user.current_occupation, #pretty sure not in use anymore
            "num_pairings_can_make": user.num_pairings_can_make,
            "mentor_gender_preference": user.mentor_gender_preference,
            "gender_identity": user.gender_identity,
            "division_preference": user.division_preference,
            "personality_1": user.personality_1,
            "personality_2": user.personality_2,
            "personality_3": user.personality_3,
            "division": user.division,
            "interests": [i.entered_name for i in user.rtn_interests()],
            "career_interests": [i.entered_name for i in user.rtn_career_interests()],
            "education": [i.entered_name for i in user.rtn_education()]
        }