import app.input_sets.models as m
"""m.InterestTag.query.delete()
m.Tag.query.delete()
m.EducationTag.query.delete()
m.School.query.delete()
m.CareerInterest.query.delete()
m.CareerInterestTag.query.delete()
m.Select.query.delete()
#m.Business.query.delete()
m.User.query.delete()
"""
from app import db

#m.Select.query.delete() #delete all selects

#print(m.Business.query.all())

#print(m.Business.query.filter_by(id=1).first())
"""for i in range(1,6):
    for u in m.User.query.filter_by(business_id=i).all():
        m.InterestTag.query.filter_by(user_id=u.id).delete()
        m.EducationTag.query.filter_by(user_id=u.id).delete()
        m.CareerInterestTag.query.filter_by(user_id=u.id).delete()
    m.User.query.filter_by(business_id=i).delete()
    m.Business.query.filter_by(id=i).delete()"""
    
#print(m.User.query.all())
print(m.Business.query.all())
#m.Tag.query.filter_by(title="hobbyTest").delete()
#print(m.Tag.query.all())

#m.School.query.filter_by(title="educationTest").delete()

"""print(m.User.query.filter_by(id = m.EducationTag.query.filter_by(educationID = m.School.query.filter_by(title="northwestern university ").first().id).first().user_id).first())
m.EducationTag.query.filter_by(educationID = m.School.query.filter_by(title="northwestern university ").first().id).first().entered_name = "northwestern university"
m.EducationTag.query.filter_by(educationID = m.School.query.filter_by(title="northwestern university ").first().id).first().educationID = 4


m.School.query.filter_by(id=3).delete()
print(m.School.query.all())
print(m.EducationTag.query.all())"""



#m.CareerInterest.query.filter_by(title = "fdsafdsafd jsaf;djksal; fjkdl as;jfkds;aj fiodspa jf9dpsaj89f pd").delete()

#m.User.query.filter_by(business_id=1).delete()