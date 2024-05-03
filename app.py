"""Python Flask WebApp Grocery Shop!"""

import config
from config import app
import routes
from models import db, User
from werkzeug.security import generate_password_hash


## This section creates the database models
with app.app_context():
    db.create_all()   ##creates the database
    # checks if admin user exist, else creates one if it doesn't exist
    admin = User.query.filter_by(is_admin=True).first() ## query to check admin user exist, if it does, store it in the variable admin.
    if not admin:
        password = generate_password_hash('admin')
        admin = User(username='admin', hashed_password=password, is_admin=True, name='admin')
        db.session.add(admin)
        db.session.commit()


if __name__ == '__main__':
    app.run(debug=True)
