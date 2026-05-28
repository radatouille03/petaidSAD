import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from config import Config
from models import db, Account, User, Administrator, VeterinaryExpert, Content, FirstAidGuide, VideoContent, Quiz, Pet, InstructionStep, QuizQuestion, QuizResult, EmergencyCase
from factory import AccountFactory, ContentFactory
from strategy import SearchContext, KeywordSearchStrategy, SeveritySpeciesSearchStrategy
from seed import seed_database

app = Flask(__name__)
app.config.from_object(Config)

# Initialize SQLAlchemy Singleton db instance
db.init_app(app)

# Helper function to check login
def login_required(role=None):
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'danger')
                return redirect(url_for('login_route'))
            if role and session.get('role') != role:
                flash('Unauthorized access.', 'danger')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = Account.query.get(user_id)


# ==========================================
# 1. PUBLIC ROUTES
# ==========================================
@app.route('/')
def home():
    if session.get('role') == 'user':
        return redirect(url_for('dashboard'))
    elif session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif session.get('role') == 'vet':
        return redirect(url_for('vet_dashboard'))
    return render_template('home_register_login.html', active_view='home')


@app.route('/register', methods=['GET', 'POST'])
def register_route():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        phone_number = request.form.get('phone_number', '').strip()
        
        errors = {}
        # Validation checks
        if not first_name:
            errors['first_name'] = 'First name is required.'
        if not last_name:
            errors['last_name'] = 'Last name is required.'
        if not username:
            errors['username'] = 'Username is required.'
        elif Account.query.filter_by(username=username).first():
            errors['username'] = 'Username is already taken.'
        if not email:
            errors['email'] = 'Email is required.'
        elif Account.query.filter_by(email=email).first():
            errors['email'] = 'Email is already registered.'
        if len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters.'
        elif password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match.'
            
        if errors:
            return render_template('home_register_login.html', active_view='register', errors=errors, values=request.form)
            
        # Create User via Factory
        try:
            user = AccountFactory.create_account(
                role='user',
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number
            )
            db.session.add(user)
            db.session.commit()
            
            # Log in the user
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = 'user'
            session['first_name'] = user.first_name
            session['last_name'] = user.last_name
            
            flash('Account created successfully! Welcome to PetAid.', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            return render_template('home_register_login.html', active_view='register', values=request.form)

    return render_template('home_register_login.html', active_view='register', values={})


@app.route('/login', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        errors = {}
        account = Account.query.filter_by(email=email).first()
        
        if not account or not account.check_password(password):
            errors['email'] = 'Invalid email or password.'
            errors['password'] = 'Invalid email or password.'
            return render_template('home_register_login.html', active_view='login', errors=errors, values=request.form)
            
        # Store user details in session
        session['user_id'] = account.id
        session['username'] = account.username
        session['role'] = account.role
        session['first_name'] = account.first_name
        session['last_name'] = account.last_name
        
        flash(f'Welcome back, {account.first_name}!', 'success')
        
        if account.role == 'user':
            return redirect(url_for('dashboard'))
        elif account.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif account.role == 'vet':
            return redirect(url_for('vet_dashboard'))

    return render_template('home_register_login.html', active_view='login', values={})


@app.route('/logout')
def logout():
    session.clear()
    flash('You have logged out successfully.', 'success')
    return redirect(url_for('home'))


# ==========================================
# 2. PET OWNER ROUTES (Dashboard, Profile, Pets)
# ==========================================
@app.route('/dashboard')
@login_required('user')
def dashboard():
    pets = Pet.query.filter_by(owner_id=g.user.id).all()
    # Get user quiz attempts
    quiz_results = QuizResult.query.filter_by(user_id=g.user.id).order_by(QuizResult.timestamp.desc()).all()
    return render_template('dashboard_profile_pet.html', active_tab='dashboard', pets=pets, quiz_results=quiz_results)


@app.route('/profile', methods=['GET', 'POST'])
@login_required('user')
def profile():
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        
        if form_type == 'profile_info':
            g.user.first_name = request.form.get('first_name', '').strip()
            g.user.last_name = request.form.get('last_name', '').strip()
            g.user.email = request.form.get('email', '').strip()
            g.user.phone_number = request.form.get('phone_number', '').strip()
            
            try:
                db.session.commit()
                # Update session values
                session['first_name'] = g.user.first_name
                session['last_name'] = g.user.last_name
                flash('Profile updated successfully.', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Error updating profile: Email might be already in use.', 'danger')
                
        elif form_type == 'password_change':
            current_pw = request.form.get('current_password', '')
            new_pw = request.form.get('new_password', '')
            confirm_new_pw = request.form.get('confirm_new_password', '')
            
            if not g.user.check_password(current_pw):
                flash('Incorrect current password.', 'danger')
            elif len(new_pw) < 8:
                flash('New password must be at least 8 characters.', 'danger')
            elif new_pw != confirm_new_pw:
                flash('Confirm password does not match.', 'danger')
            else:
                try:
                    g.user.set_password(new_pw)
                    db.session.commit()
                    flash('Password changed successfully.', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash('Error changing password.', 'danger')
                    
        return redirect(url_for('profile'))

    return render_template('dashboard_profile_pet.html', active_tab='profile', user=g.user)


@app.route('/pets')
@login_required('user')
def pets_list():
    edit_id = request.args.get('edit_id')
    editing_pet = None
    if edit_id:
        editing_pet = Pet.query.filter_by(id=edit_id, owner_id=g.user.id).first()
        
    pets = Pet.query.filter_by(owner_id=g.user.id).all()
    return render_template('dashboard_profile_pet.html', active_tab='pets', pets=pets, editing_pet=editing_pet)


@app.route('/pets/add', methods=['POST'])
@login_required('user')
def add_pet_post():
    name = request.form.get('name', '').strip()
    species = request.form.get('species', '').strip()
    breed = request.form.get('breed', '').strip()
    age = request.form.get('age', '').strip()
    weight_raw = request.form.get('weight', '0')
    medical_notes = request.form.get('medical_notes', '').strip()
    
    try:
        weight = float(weight_raw)
        if not name or not species or not breed or not age or weight <= 0:
            raise ValueError("Invalid parameters.")
            
        pet = Pet(
            name=name,
            species=species,
            breed=breed,
            age=age,
            weight=weight,
            medical_notes=medical_notes,
            owner_id=g.user.id
        )
        db.session.add(pet)
        db.session.commit()
        flash(f'Pet "{name}" registered successfully!', 'success')
    except Exception as e:
        flash('Failed to add pet. Please ensure values are correct.', 'danger')
        
    return redirect(url_for('pets_list'))


@app.route('/pets/edit/<int:pet_id>', methods=['POST'])
@login_required('user')
def edit_pet_post(pet_id):
    pet = Pet.query.filter_by(id=pet_id, owner_id=g.user.id).first_or_404()
    
    pet.name = request.form.get('name', '').strip()
    pet.species = request.form.get('species', '').strip()
    pet.breed = request.form.get('breed', '').strip()
    pet.age = request.form.get('age', '').strip()
    weight_raw = request.form.get('weight', '0')
    pet.medical_notes = request.form.get('medical_notes', '').strip()
    
    try:
        pet.weight = float(weight_raw)
        db.session.commit()
        flash('Pet profile updated successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to update pet details.', 'danger')
        
    return redirect(url_for('pets_list'))


@app.route('/pets/delete/<int:pet_id>', methods=['POST'])
@login_required('user')
def delete_pet(pet_id):
    pet = Pet.query.filter_by(id=pet_id, owner_id=g.user.id).first()
    if pet:
        try:
            db.session.delete(pet)
            db.session.commit()
            flash('Pet profile deleted successfully.', 'success')
        except Exception:
            db.session.rollback()
            flash('Error deleting pet profile.', 'danger')
    else:
        flash('Pet profile already deleted or not found.', 'warning')
    return redirect(url_for('pets_list'))


# ==========================================
# 3. SEARCH & CONTENT CONSUMPTION (User)
# ==========================================
@app.route('/search')
@login_required('user')
def search_emergency():
    query = request.args.get('query', '').strip()
    species_filter = request.args.get('species', 'all').strip()
    strategy_mode = request.args.get('strategy', 'keyword').strip()
    
    # Instantiate Context and swap strategies
    if strategy_mode == 'severity':
        context = SearchContext(SeveritySpeciesSearchStrategy())
    else:
        context = SearchContext(KeywordSearchStrategy())
        
    results = context.execute_search(query, species_filter)
    
    return render_template(
        'search_guide_video.html',
        active_tab='search',
        query=query,
        active_species=species_filter,
        strategy_mode=strategy_mode,
        results=results
    )


@app.route('/guides')
@login_required('user')
def guides_list():
    # Only show approved guides to users
    guides = FirstAidGuide.query.filter_by(verification_status='Approved').all()
    return render_template('search_guide_video.html', active_tab='guides', guides=guides, guide=None)


@app.route('/guides/<int:guide_id>')
@login_required('user')
def view_guide(guide_id):
    guide = FirstAidGuide.query.filter_by(id=guide_id, verification_status='Approved').first_or_404()
    
    # Load related guides (same species, excluding current)
    related_guides = FirstAidGuide.query.filter(
        FirstAidGuide.id != guide.id,
        FirstAidGuide.species.ilike(guide.species),
        FirstAidGuide.verification_status == 'Approved'
    ).limit(3).all()
    
    # Load related video (first video matching current guide species)
    related_video = VideoContent.query.filter(
        VideoContent.species.ilike(guide.species),
        VideoContent.verification_status == 'Approved'
    ).first()
    
    return render_template(
        'search_guide_video.html',
        active_tab='guides',
        guide=guide,
        related_guides=related_guides,
        related_video=related_video
    )


@app.route('/videos')
@login_required('user')
def videos_list():
    videos = VideoContent.query.filter_by(verification_status='Approved').all()
    return render_template('search_guide_video.html', active_tab='videos', videos=videos, video=None)


@app.route('/videos/<int:video_id>')
@login_required('user')
def view_video(video_id):
    video = VideoContent.query.filter_by(id=video_id, verification_status='Approved').first_or_404()
    videos = VideoContent.query.filter(VideoContent.id != video.id, VideoContent.verification_status == 'Approved').all()
    return render_template('search_guide_video.html', active_tab='videos', video=video, videos=videos)


# ==========================================
# 4. QUIZ ROUTES (User)
# ==========================================
@app.route('/quizzes')
@login_required('user')
def quizzes_list():
    quizzes = Quiz.query.filter_by(verification_status='Approved').all()
    
    # Fetch last scores
    last_scores = {}
    for q in quizzes:
        last_attempt = QuizResult.query.filter_by(user_id=g.user.id, quiz_id=q.id)\
            .order_by(QuizResult.timestamp.desc()).first()
        if last_attempt:
            last_scores[q.id] = {
                'score': last_attempt.score,
                'total': last_attempt.total_questions
            }
            
    return render_template('quiz_result.html', active_tab='quizzes', quizzes=quizzes, last_scores=last_scores)


@app.route('/quiz/start/<int:quiz_id>')
@login_required('user')
def start_quiz(quiz_id):
    quiz = Quiz.query.filter_by(id=quiz_id, verification_status='Approved').first_or_404()
    
    if not quiz.questions:
        flash('This quiz has no questions yet.', 'warning')
        return redirect(url_for('quizzes_list'))
        
    session['quiz_id'] = quiz.id
    session['quiz_answers'] = {}
    session['quiz_question_idx'] = 0
    return redirect(url_for('take_quiz'))


@app.route('/quiz/take')
@login_required('user')
def take_quiz():
    quiz_id = session.get('quiz_id')
    if not quiz_id:
        return redirect(url_for('quizzes_list'))
        
    quiz = Quiz.query.get(quiz_id)
    idx = session.get('quiz_question_idx', 0)
    
    if idx < 0 or idx >= len(quiz.questions):
        return redirect(url_for('quizzes_list'))
        
    question = quiz.questions[idx]
    saved_answer = session.get('quiz_answers', {}).get(str(question.id))
    
    return render_template(
        'quiz_result.html',
        active_tab='quiz_take',
        quiz=quiz,
        question=question,
        question_index=idx,
        total_questions=len(quiz.questions),
        saved_answer=saved_answer
    )


@app.route('/quiz/prev')
@login_required('user')
def prev_question():
    idx = session.get('quiz_question_idx', 0)
    if idx > 0:
        session['quiz_question_idx'] = idx - 1
    return redirect(url_for('take_quiz'))


@app.route('/quiz/submit', methods=['POST'])
@login_required('user')
def submit_question():
    quiz_id = session.get('quiz_id')
    if not quiz_id:
        return redirect(url_for('quizzes_list'))
        
    quiz = Quiz.query.get(quiz_id)
    idx = session.get('quiz_question_idx', 0)
    question = quiz.questions[idx]
    
    ans = request.form.get('answer')
    if ans:
        # Save in answers dict
        answers = session.get('quiz_answers', {})
        answers[str(question.id)] = ans
        session['quiz_answers'] = answers
        
    # Go to next question or evaluate
    if idx + 1 < len(quiz.questions):
        session['quiz_question_idx'] = idx + 1
        return redirect(url_for('take_quiz'))
    else:
        # End of quiz - evaluate and save
        score, total = quiz.evaluate_answers(session['quiz_answers'])
        
        result = QuizResult(
            score=score,
            total_questions=total,
            user_id=g.user.id,
            quiz_id=quiz.id
        )
        db.session.add(result)
        db.session.commit()
        
        result_id = result.id
        # Save answers to show on result page
        session['last_quiz_answers'] = session['quiz_answers']
        # Clear quiz state
        session.pop('quiz_id', None)
        session.pop('quiz_answers', None)
        session.pop('quiz_question_idx', None)
        
        flash('Quiz completed successfully!', 'success')
        return redirect(url_for('view_quiz_result', result_id=result_id))


@app.route('/quiz/result/<int:result_id>')
@login_required('user')
def view_quiz_result(result_id):
    result = QuizResult.query.filter_by(id=result_id, user_id=g.user.id).first_or_404()
    quiz = result.quiz
    
    # Load user historical attempts for this specific quiz
    history = QuizResult.query.filter(
        QuizResult.user_id == g.user.id,
        QuizResult.quiz_id == quiz.id,
        QuizResult.id != result.id
    ).order_by(QuizResult.timestamp.desc()).all()
    
    # Load user answers from session
    user_answers = session.get('last_quiz_answers', {})
    
    return render_template(
        'quiz_result.html',
        active_tab='quiz_result',
        result=result,
        quiz=quiz,
        history=history,
        questions_review=quiz.questions,
        user_answers=user_answers
    )


# ==========================================
# 5. ADMINISTRATOR ROUTES (Content CRUD)
# ==========================================
@app.route('/admin')
@login_required('admin')
def admin_dashboard():
    # Counts
    guides_count = FirstAidGuide.query.count()
    pending_guides_count = FirstAidGuide.query.filter_by(verification_status='Pending').count()
    videos_count = VideoContent.query.count()
    pending_videos_count = VideoContent.query.filter_by(verification_status='Pending').count()
    quizzes_count = Quiz.query.count()
    pending_quizzes_count = Quiz.query.filter_by(verification_status='Pending').count()
    users_count = User.query.count()
    
    # Load pending items
    pending_items = Content.query.filter_by(verification_status='Pending')\
        .order_by(Content.publish_date.desc()).all()
        
    return render_template(
        'admin_screens.html',
        active_tab='dashboard',
        guides_count=guides_count,
        pending_guides_count=pending_guides_count,
        videos_count=videos_count,
        pending_videos_count=pending_videos_count,
        quizzes_count=quizzes_count,
        pending_quizzes_count=pending_quizzes_count,
        users_count=users_count,
        pending_items=pending_items
    )


@app.route('/admin/manage/<ctype>')
@login_required('admin')
def admin_manage(ctype):
    status_filter = request.args.get('status', 'all')
    
    if ctype == 'guide':
        query = FirstAidGuide.query
        active_tab = 'guides'
    elif ctype == 'video':
        query = VideoContent.query
        active_tab = 'videos'
    elif ctype == 'quiz':
        query = Quiz.query
        active_tab = 'quizzes'
    else:
        return redirect(url_for('admin_dashboard'))
        
    if status_filter != 'all':
        query = query.filter_by(verification_status=status_filter)
        
    items = query.order_by(Content.publish_date.desc()).all()
    return render_template('admin_screens.html', active_tab=active_tab, items=items, ctype=ctype)


@app.route('/admin/add/<ctype>', methods=['GET'])
@login_required('admin')
def admin_add(ctype):
    if ctype not in ['guide', 'video', 'quiz']:
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_screens.html', active_tab='add_edit', ctype=ctype, item=None)


@app.route('/admin/add/<ctype>', methods=['POST'])
@login_required('admin')
def admin_add_post(ctype):
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    species = request.form.get('species', '').strip()
    status = request.form.get('verification_status', 'Pending')
    
    kwargs = {'species': species}
    
    if ctype == 'guide':
        kwargs['severity'] = request.form.get('severity', 'Minor')
    elif ctype == 'video':
        kwargs['video_url'] = request.form.get('video_url', '').strip()
        kwargs['duration'] = request.form.get('duration', '0:00').strip()
        kwargs['transcript'] = request.form.get('transcript', '').strip()
        kwargs['severity'] = request.form.get('severity', 'Minor')
        
    try:
        # Create Content via Factory
        item = ContentFactory.create_content(
            content_type=ctype,
            title=title,
            description=description,
            author_id=g.user.id,
            **kwargs
        )
        item.verification_status = status
        db.session.add(item)
        db.session.commit()
        
        # Save specific steps/questions
        if ctype == 'guide':
            steps_raw = request.form.get('steps_raw', '')
            for line in steps_raw.split('\n'):
                if '|' in line and ':' in line:
                    prefix, step_desc = line.split('|', 1)
                    step_num, step_title = prefix.split(':', 1)
                    step = InstructionStep(
                        guide_id=item.id,
                        step_number=int(step_num.strip()),
                        title=step_title.strip(),
                        description=step_desc.strip()
                    )
                    db.session.add(step)
            db.session.commit()
            
        elif ctype == 'quiz':
            q_raw = request.form.get('questions_raw', '')
            for line in q_raw.split('\n'):
                parts = line.split('|')
                if len(parts) >= 6:
                    q = QuizQuestion(
                        quiz_id=item.id,
                        question_text=parts[0].strip(),
                        option_a=parts[1].strip(),
                        option_b=parts[2].strip(),
                        option_c=parts[3].strip(),
                        option_d=parts[4].strip(),
                        correct_option=parts[5].strip().upper()
                    )
                    db.session.add(q)
            db.session.commit()
            
        flash(f'{ctype.capitalize()} created successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating content: {str(e)}', 'danger')
        
    return redirect(url_for('admin_manage', ctype=ctype))


@app.route('/admin/edit/<ctype>/<int:content_id>', methods=['GET'])
@login_required('admin')
def admin_edit(ctype, content_id):
    if ctype == 'guide':
        item = FirstAidGuide.query.get_or_404(content_id)
        active_tab = 'add_edit'
    elif ctype == 'video':
        item = VideoContent.query.get_or_404(content_id)
        active_tab = 'add_edit'
    elif ctype == 'quiz':
        item = Quiz.query.get_or_404(content_id)
        active_tab = 'add_edit'
    else:
        return redirect(url_for('admin_dashboard'))
        
    return render_template('admin_screens.html', active_tab='add_edit', ctype=ctype, item=item)


@app.route('/admin/edit/<ctype>/<int:content_id>', methods=['POST'])
@login_required('admin')
def admin_edit_post(ctype, content_id):
    if ctype == 'guide':
        item = FirstAidGuide.query.get_or_404(content_id)
        item.severity = request.form.get('severity', 'Minor')
    elif ctype == 'video':
        item = VideoContent.query.get_or_404(content_id)
        item.video_url = request.form.get('video_url', '').strip()
        item.duration = request.form.get('duration', '0:00').strip()
        item.transcript = request.form.get('transcript', '').strip()
        item.severity = request.form.get('severity', 'Minor')
    elif ctype == 'quiz':
        item = Quiz.query.get_or_404(content_id)
    else:
        return redirect(url_for('admin_dashboard'))
        
    item.title = request.form.get('title', '').strip()
    item.description = request.form.get('description', '').strip()
    item.species = request.form.get('species', '').strip()
    item.verification_status = request.form.get('verification_status', 'Pending')
    
    # If the content was previously rejected, resubmitting clears the rejection feedback
    if item.verification_status == 'Pending':
        item.rejection_feedback = None
        
    try:
        db.session.commit()
        
        # Save specific steps/questions
        if ctype == 'guide':
            InstructionStep.query.filter_by(guide_id=item.id).delete()
            steps_raw = request.form.get('steps_raw', '')
            for line in steps_raw.split('\n'):
                if '|' in line and ':' in line:
                    prefix, step_desc = line.split('|', 1)
                    step_num, step_title = prefix.split(':', 1)
                    step = InstructionStep(
                        guide_id=item.id,
                        step_number=int(step_num.strip()),
                        title=step_title.strip(),
                        description=step_desc.strip()
                    )
                    db.session.add(step)
            db.session.commit()
            
        elif ctype == 'quiz':
            QuizQuestion.query.filter_by(quiz_id=item.id).delete()
            q_raw = request.form.get('questions_raw', '')
            for line in q_raw.split('\n'):
                parts = line.split('|')
                if len(parts) >= 6:
                    q = QuizQuestion(
                        quiz_id=item.id,
                        question_text=parts[0].strip(),
                        option_a=parts[1].strip(),
                        option_b=parts[2].strip(),
                        option_c=parts[3].strip(),
                        option_d=parts[4].strip(),
                        correct_option=parts[5].strip().upper()
                    )
                    db.session.add(q)
            db.session.commit()
            
        flash(f'{ctype.capitalize()} updated successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to update content: {str(e)}', 'danger')
        
    return redirect(url_for('admin_manage', ctype=ctype))


@app.route('/admin/delete-confirm/<ctype>/<int:content_id>', methods=['GET'])
@login_required('admin')
def admin_delete_confirm(ctype, content_id):
    item = Content.query.get_or_404(content_id)
    return render_template('admin_screens.html', active_tab='delete_confirm', ctype=ctype, item=item)


@app.route('/admin/delete/<ctype>/<int:content_id>', methods=['POST'])
@login_required('admin')
def admin_delete_post(ctype, content_id):
    item = Content.query.get_or_404(content_id)
    try:
        db.session.delete(item)
        db.session.commit()
        flash(f'{ctype.capitalize()} content deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting content.', 'danger')
    return redirect(url_for('admin_manage', ctype=ctype))


@app.route('/admin/users')
@login_required('admin')
def admin_users():
    accounts = Account.query.all()
    return render_template(
        'admin_screens.html',
        active_tab='users',
        accounts=accounts
    )


@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@login_required('admin')
def admin_delete_user(user_id):
    if user_id == session.get('user_id'):
        flash('You cannot delete your own admin account.', 'danger')
        return redirect(url_for('admin_users'))

    user_to_delete = Account.query.get(user_id)
    if user_to_delete:
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash('Account removed successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error removing account: {str(e)}', 'danger')
    else:
        flash('Account already removed or not found.', 'warning')

    return redirect(url_for('admin_users'))


# ==========================================
# 6. VETERINARY EXPERT ROUTES (Reviews)
# ==========================================
@app.route('/vet')
@login_required('vet')
def vet_dashboard():
    # Load all pending content items
    pending = Content.query.filter_by(verification_status='Pending')\
        .order_by(Content.publish_date.desc()).all()
        
    # Get approved and rejected counts verified by Vets
    approved_count = Content.query.filter_by(verification_status='Approved').count()
    rejected_count = Content.query.filter_by(verification_status='Rejected').count()
    
    return render_template(
        'vet_screens.html',
        active_tab='dashboard',
        pending=pending,
        approved_count=approved_count,
        rejected_count=rejected_count
    )


@app.route('/vet/pending')
@login_required('vet')
def vet_pending():
    pending = Content.query.filter_by(verification_status='Pending')\
        .order_by(Content.publish_date.desc()).all()
    return render_template('vet_screens.html', active_tab='pending', pending=pending)


@app.route('/vet/history/<status>')
@login_required('vet')
def vet_history(status):
    if status not in ['Approved', 'Rejected']:
        return redirect(url_for('vet_dashboard'))
        
    history_items = Content.query.filter_by(verification_status=status)\
        .order_by(Content.publish_date.desc()).all()
        
    active_tab = 'approved' if status == 'Approved' else 'rejected'
    return render_template('vet_screens.html', active_tab=active_tab, history_items=history_items)


@app.route('/vet/review/<int:content_id>')
@login_required('vet')
def vet_review(content_id):
    item = Content.query.get_or_404(content_id)
    return render_template('vet_screens.html', active_tab='review', item=item)


@app.route('/vet/decision/<int:content_id>', methods=['POST'])
@login_required('vet')
def vet_decision(content_id):
    item = Content.query.get_or_404(content_id)
    decision = request.form.get('decision')
    feedback = request.form.get('feedback', '').strip()
    
    if decision == 'approve':
        item.verification_status = 'Approved'
        item.rejection_feedback = None
        flash(f'"{item.title}" has been approved and published.', 'success')
    elif decision == 'reject':
        if not feedback:
            flash('Feedback is required when rejecting medical content.', 'danger')
            return redirect(url_for('vet_review', content_id=content_id))
        item.verification_status = 'Rejected'
        item.rejection_feedback = feedback
        flash(f'"{item.title}" has been returned to drafts with feedback.', 'warning')
        
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('An error occurred during verification.', 'danger')
        
    return redirect(url_for('vet_pending'))


# ==========================================
# 7. APP BOOTSTRAP INIT
# ==========================================
if __name__ == '__main__':
    with app.app_context():
        # Create SQLite tables
        db.create_all()
        # Seed default mockup databases
        seed_database()
        
    # Start dev server locally on port 5000
    app.run(host='127.0.0.1', port=5000, debug=True)
