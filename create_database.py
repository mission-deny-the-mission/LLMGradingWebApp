from create_app import create_app
from models import db

app = create_app(run_worker=False)
with app.app_context():
    db.create_all()
