from app import db
from app.input_sets.models import Event

print(Event.query.filter_by(action=9).all())