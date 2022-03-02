from app import db
from app.input_sets.models import Event, Select

#print(Event.query.filter_by(action=16).all())

Select.query.filter_by(id=5).first().inc_current_meeting_ID()
db.session.commit()