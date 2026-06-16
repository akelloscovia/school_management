import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app, db
from app.models import User, Role, Student, Class, Subject, Attendance, Marks, Message, Announcement

app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Role': Role,
        'Student': Student,
        'Class': Class,
        'Subject': Subject,
        'Attendance': Attendance,
        'Marks': Marks,
        'Message': Message,
        'Announcement': Announcement
    }

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=debug_mode,
        use_reloader=False
    )
