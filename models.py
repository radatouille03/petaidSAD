from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# ==========================================
# 1. ACCOUNT CLASSES (Actors)
# Joined Table Inheritance for Accounts
# ==========================================
class Account(db.Model):
    __tablename__ = 'account'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    # Discriminator ('user', 'admin', 'vet')
    role = db.Column(db.String(30), nullable=False)

    __mapper_args__ = {
        'polymorphic_on': role,
        'polymorphic_identity': 'account'
    }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class User(Account):
    __tablename__ = 'user_account'
    id = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)

    pets = db.relationship(
        'Pet',
        backref='owner',
        cascade='all, delete-orphan',
        lazy=True
    )
    quiz_results = db.relationship(
        'QuizResult',
        backref='user',
        cascade='all, delete-orphan',
        lazy=True
    )

    __mapper_args__ = {
        'polymorphic_identity': 'user',
    }


class Administrator(Account):
    __tablename__ = 'admin_account'
    id = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)

    created_content = db.relationship('Content', backref='author', lazy=True)

    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }


class VeterinaryExpert(Account):
    __tablename__ = 'vet_account'
    id = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'vet',
    }


# ==========================================
# 2. CONTENT CLASSES (Educational Materials)
# Joined Table Inheritance for Content
# ==========================================
class Content(db.Model):
    __tablename__ = 'content'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    publish_date = db.Column(db.DateTime, default=datetime.utcnow)
    # 'Draft', 'Pending', 'Approved', 'Rejected'
    verification_status = db.Column(db.String(20), default='Pending')
    rejection_feedback = db.Column(db.Text, nullable=True)
    author_id = db.Column(
        db.Integer,
        db.ForeignKey('admin_account.id'),
        nullable=False
    )
    # Discriminator ('guide', 'video', 'quiz')
    content_type = db.Column(db.String(30), nullable=False)

    __mapper_args__ = {
        'polymorphic_on': content_type,
        'polymorphic_identity': 'content'
    }


class FirstAidGuide(Content):
    __tablename__ = 'first_aid_guide'
    id = db.Column(db.Integer, db.ForeignKey('content.id'), primary_key=True)

    severity = db.Column(db.String(20), nullable=False)
    species = db.Column(db.String(50), nullable=False)

    steps = db.relationship(
        'InstructionStep',
        backref='guide',
        cascade='all, delete-orphan',
        order_by='InstructionStep.step_number',
        lazy=True
    )
    emergency_cases = db.relationship(
        'EmergencyCase',
        backref='guide',
        lazy=True
    )

    __mapper_args__ = {
        'polymorphic_identity': 'guide',
    }


class VideoContent(Content):
    __tablename__ = 'video_content'
    id = db.Column(db.Integer, db.ForeignKey('content.id'), primary_key=True)

    video_url = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.String(20), nullable=False)  # e.g., '4:32'
    transcript = db.Column(db.Text, nullable=True)
    species = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)

    emergency_cases = db.relationship(
        'EmergencyCase',
        backref='video',
        lazy=True
    )

    __mapper_args__ = {
        'polymorphic_identity': 'video',
    }


class Quiz(Content):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, db.ForeignKey('content.id'), primary_key=True)

    species = db.Column(db.String(50), nullable=False)

    questions = db.relationship(
        'QuizQuestion',
        backref='quiz',
        cascade='all, delete-orphan',
        lazy=True
    )
    results = db.relationship(
        'QuizResult',
        backref='quiz',
        cascade='all, delete-orphan',
        lazy=True
    )

    __mapper_args__ = {
        'polymorphic_identity': 'quiz',
    }

    def evaluate_answers(self, user_answers):
        """
        Evaluates user answers dictionary: {question_id: 'A'/'B'/'C'/'D'}
        Returns (score, total_questions)
        """
        score = 0
        total = len(self.questions)
        for q in self.questions:
            user_ans = user_answers.get(str(q.id)) or user_answers.get(q.id)
            if user_ans:
                u_ans = user_ans.strip().upper()
                c_ans = q.correct_option.strip().upper()
                if u_ans == c_ans:
                    score += 1
        return score, total


# ==========================================
# 3. DOMAIN ENTITIES
# ==========================================
class Pet(db.Model):
    __tablename__ = 'pet'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # 'Dog', 'Cat', 'Rabbit', 'Hamster', 'Other'
    species = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(100), nullable=False)
    age = db.Column(db.String(50), nullable=False)      # e.g., '3 years'
    weight = db.Column(db.Float, nullable=False)        # in kg
    medical_notes = db.Column(db.Text, nullable=True)
    owner_id = db.Column(
        db.Integer,
        db.ForeignKey('user_account.id'),
        nullable=False
    )


class InstructionStep(db.Model):
    __tablename__ = 'instruction_step'

    id = db.Column(db.Integer, primary_key=True)
    guide_id = db.Column(
        db.Integer,
        db.ForeignKey('first_aid_guide.id'),
        nullable=False
    )
    step_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)


class QuizQuestion(db.Model):
    __tablename__ = 'quiz_question'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(
        db.Integer,
        db.ForeignKey('quiz.id'),
        nullable=False
    )
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    # 'A', 'B', 'C', 'D'
    correct_option = db.Column(db.String(5), nullable=False)


class QuizResult(db.Model):
    __tablename__ = 'quiz_result'

    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user_account.id'),
        nullable=False
    )
    quiz_id = db.Column(
        db.Integer,
        db.ForeignKey('quiz.id'),
        nullable=False
    )


class EmergencyCase(db.Model):
    __tablename__ = 'emergency_case'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    # 'Critical', 'Moderate', 'Minor'
    severity = db.Column(db.String(20), nullable=False)
    species = db.Column(db.String(50), nullable=False)
    # Comma-separated strings
    keywords = db.Column(db.String(255), nullable=False)

    guide_id = db.Column(
        db.Integer,
        db.ForeignKey('first_aid_guide.id'),
        nullable=True
    )
    video_id = db.Column(
        db.Integer,
        db.ForeignKey('video_content.id'),
        nullable=True
    )
