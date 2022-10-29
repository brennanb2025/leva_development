from app import db
from app.input_sets.models import Event, Select, Business, User

for b in Business.query.all():
    print(b)

for u in User.query.all():
    print(u)
    

"""
Event.query.filter_by(action=16).delete()
db.session.commit()

print(Event.query.filter_by(action=18).all())
print(str(len(Event.query.all())))
"""