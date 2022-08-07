from api import create_app, cli, db
from api.models import Answer, Question, Sentence, User

app = create_app()
cli.register(app)

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Answer': Answer,
        'Question': Question,
        'Sentence': Sentence
    }
