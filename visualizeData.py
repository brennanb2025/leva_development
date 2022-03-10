from app import db
from app.input_sets.models import Event, Select

Event.query.filter_by(action=16).delete()
db.session.commit()

print(str(len(Event.query.filter_by(action=16).all())))