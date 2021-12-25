import app.input_sets.models as m
m.InterestTag.query.delete()
m.Tag.query.delete()
m.EducationTag.query.delete()
m.School.query.delete()
m.CareerInterest.query.delete()
m.CareerInterestTag.query.delete()
m.Select.query.delete()
#m.Business.query.delete()
m.User.query.delete()
from app import db
db.session.commit()