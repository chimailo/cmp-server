from sqlalchemy import exc
from api import db as _db
from api.models import Question


def register(app):
    @app.cli.group()
    def seed():
        """Database tables seed commands."""
        pass


    @seed.command()
    def db():
        """Seeds the database."""
        _db.drop_all()
        _db.create_all()
        _db.session.commit()
        questions_table()
        
    def questions_table():
        """Seeds the questions table."""
        questions = [
            "What was the happiest moment of your life",
            "What was your first nickname"
        ]
        
        q1 = Question()
        q1.text = questions[0]
        q2 = Question()
        q2.text = questions[1]

        try:
            _db.session.add_all([q1, q2])
            _db.session.commit()
        except exc.IntegrityError as error:
            _db.session.rollback()
            print(f'Error: {error}')
