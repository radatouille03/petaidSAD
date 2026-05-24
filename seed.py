from datetime import datetime, timedelta
from models import db, Account, Pet, InstructionStep, QuizQuestion, QuizResult, EmergencyCase
from factory import AccountFactory, ContentFactory

def seed_database():
    # 1. Check if database already has data to prevent duplicate seeding
    if Account.query.first() is not None:
        print("Database already seeded. Skipping...")
        return

    print("Seeding database with default accounts and mockup content...")

    # ==========================================
    # 1. Accounts Seeding
    # ==========================================
    # Admin
    admin = AccountFactory.create_account(
        role='admin',
        username='admin',
        email='admin@petaid.com',
        password='admin123',
        first_name='Admin',
        last_name='Admin'
    )
    db.session.add(admin)
    db.session.commit()  # commit to get the admin's ID
    admin_id = admin.id

    # Vet Expert Dr. Lim
    vet = AccountFactory.create_account(
        role='vet',
        username='Dr. Lim',
        email='vet@petaid.com',
        password='vet123',
        first_name='Lim',
        last_name='Vet'
    )
    db.session.add(vet)

    # User Radzien
    user1 = AccountFactory.create_account(
        role='user',
        username='Radzien',
        email='rad@email.com',
        password='user123',
        first_name='Radzien',
        last_name='Jawharee',
        phone_number='+60 12 345 6789'
    )
    db.session.add(user1)

    # User ysx
    user2 = AccountFactory.create_account(
        role='user',
        username='ysx',
        email='yongsx@email.com',
        password='user123',
        first_name='Suen Xuen',
        last_name='Yong'
    )
    db.session.add(user2)
    db.session.commit()
    user_id = user1.id

    # ==========================================
    # 2. Pets Seeding
    # ==========================================
    vigo = Pet(
        name='Vigo',
        species='Cat',
        breed='tuxedo cat',
        age='8 months',
        weight=4.0,
        medical_notes=None,
        owner_id=user_id
    )
    db.session.add(vigo)

    # ==========================================
    # 3. First-Aid Guides Seeding (Content subclass)
    # ==========================================
    # Guide 1: Dog Choking (Approved)
    guide_dog_choking = ContentFactory.create_content(
        content_type='guide',
        title='What to do if your dog is choking',
        description='Choking in dogs is a life-threatening emergency. Act quickly but stay calm. Follow these steps immediately.',
        author_id=admin_id,
        severity='Critical',
        species='Dog'
    )
    guide_dog_choking.verification_status = 'Approved'
    db.session.add(guide_dog_choking)
    db.session.commit()  # get ID

    steps_dog = [
        InstructionStep(guide_id=guide_dog_choking.id, step_number=1, title='Stay calm and restrain your dog', description='A choking dog may panic and bite. Speak calmly and gently hold your dog still before attempting anything.'),
        InstructionStep(guide_id=guide_dog_choking.id, step_number=2, title='Check the mouth', description='Open the mouth carefully and look inside. If you can clearly see and safely reach the object, try to remove it with two fingers. Do not do a blind finger sweep.'),
        InstructionStep(guide_id=guide_dog_choking.id, step_number=3, title='Apply back blows', description='Tilt the dog forward and give up to 5 firm blows between the shoulder blades using the heel of your hand.'),
        InstructionStep(guide_id=guide_dog_choking.id, step_number=4, title='Apply abdominal thrusts', description='Stand behind your dog, make a fist and place it just below the rib cage. Pull sharply inward and upward up to 5 times.'),
        InstructionStep(guide_id=guide_dog_choking.id, step_number=5, title='Call a vet immediately', description='Even if the object is removed, take your dog to a vet right away to check for internal damage.')
    ]
    db.session.add_all(steps_dog)

    # Guide 2: Cat Choking (Approved)
    guide_cat_choking = ContentFactory.create_content(
        content_type='guide',
        title='Cat choking — signs and immediate response',
        description='Recognise choking symptoms in cats and apply the correct first-aid response.',
        author_id=admin_id,
        severity='Critical',
        species='Cat'
    )
    guide_cat_choking.verification_status = 'Approved'
    db.session.add(guide_cat_choking)
    db.session.commit()

    steps_cat = [
        InstructionStep(guide_id=guide_cat_choking.id, step_number=1, title='Stay calm and secure', description='Calm your cat and wrap them gently in a towel to prevent scratching and biting.'),
        InstructionStep(guide_id=guide_cat_choking.id, step_number=2, title='Open the mouth', description='Tilt the head back slightly and open the jaw. Check for any visible blockages at the back of the throat.'),
        InstructionStep(guide_id=guide_cat_choking.id, step_number=3, title='Sweep carefully', description='If you can see the object, pull it out carefully with tweezers or your fingers. Do not force it back.'),
        InstructionStep(guide_id=guide_cat_choking.id, step_number=4, title='Apply gentle chest thrusts', description='Place your hands on either side of the cat\'s chest wall and apply 4-5 quick squeeze-releases.'),
        InstructionStep(guide_id=guide_cat_choking.id, step_number=5, title='Transport to clinic', description='Rush to the nearest veterinary center immediately.')
    ]
    db.session.add_all(steps_cat)

    # Guide 3: Rabbit Choking (Approved)
    guide_rabbit_choking = ContentFactory.create_content(
        content_type='guide',
        title='Rabbit choking on food — what to do',
        description='How to identify and respond to a rabbit choking on food or a foreign object.',
        author_id=admin_id,
        severity='Moderate',
        species='Rabbit'
    )
    guide_rabbit_choking.verification_status = 'Approved'
    db.session.add(guide_rabbit_choking)
    db.session.commit()
    
    steps_rab = [
        InstructionStep(guide_id=guide_rabbit_choking.id, step_number=1, title='Keep calm', description='Panicking will stress the rabbit, worsening respiratory distress.'),
        InstructionStep(guide_id=guide_rabbit_choking.id, step_number=2, title='Check nose and mouth', description='Rabbits are obligate nasal breathers. Make sure nostrils are clear.'),
        InstructionStep(guide_id=guide_rabbit_choking.id, step_number=3, title='The Centrifugal Swing', description='Hold the rabbit firmly, supporting its back and neck, and swing them down in a wide arc once to clear the airway. Perform with extreme caution.')
    ]
    db.session.add_all(steps_rab)

    # Guide 4: Hamster Choking (Approved)
    guide_hamster_choking = ContentFactory.create_content(
        content_type='guide',
        title='Hamster choking prevention and response',
        description='Tips to prevent choking in hamsters and what to do if it occurs.',
        author_id=admin_id,
        severity='Moderate',
        species='Hamster'
    )
    guide_hamster_choking.verification_status = 'Approved'
    db.session.add(guide_hamster_choking)
    db.session.commit()
    
    steps_ham = [
        InstructionStep(guide_id=guide_hamster_choking.id, step_number=1, title='Differentiate from pouching', description='Ensure the hamster is choking rather than just storing food in cheek pouches.'),
        InstructionStep(guide_id=guide_hamster_choking.id, step_number=2, title='Gentle back rubs', description='Gently rub the hamster\'s back downward to assist swallowing.'),
        InstructionStep(guide_id=guide_hamster_choking.id, step_number=3, title='Moisten mouth', description='Use a tiny drop of water if food is stuck dry, but avoid blocking airway.')
    ]
    db.session.add_all(steps_ham)

    # Guide 5: Rabbit Seizure (Pending - For Vet Review workflow)
    guide_rabbit_seizure = ContentFactory.create_content(
        content_type='guide',
        title='Rabbit seizure — immediate response',
        description='A rabbit seizure can be frightening but knowing how to respond can help keep your rabbit safe. Follow these steps carefully.',
        author_id=admin_id,
        severity='Moderate',
        species='Rabbit'
    )
    guide_rabbit_seizure.verification_status = 'Pending'
    db.session.add(guide_rabbit_seizure)
    db.session.commit()

    steps_seizure = [
        InstructionStep(guide_id=guide_rabbit_seizure.id, step_number=1, title='Stay calm and do not restrain', description='Restraining a seizing rabbit can cause bone fractures or internal injury.'),
        InstructionStep(guide_id=guide_rabbit_seizure.id, step_number=2, title='Clear the area', description='Remove any hard or sharp objects that could cause injury during the seizure.'),
        InstructionStep(guide_id=guide_rabbit_seizure.id, step_number=3, title='Time the seizure', description='Note when it started and how long it lasts — this is important information for your vet.'),
        InstructionStep(guide_id=guide_rabbit_seizure.id, step_number=4, title='Keep warm and dark', description='Place a soft cloth nearby but do not cover the rabbit\'s face. Dim the lights.'),
        InstructionStep(guide_id=guide_rabbit_seizure.id, step_number=5, title='Contact a vet', description='Contact a vet immediately after the seizure ends, even if the rabbit appears to recover.')
    ]
    db.session.add_all(steps_seizure)


    # ==========================================
    # 4. Video Content Seeding
    # ==========================================
    video_dog_choking = ContentFactory.create_content(
        content_type='video',
        title='Dog choking — visual guide',
        description='Watch how to perform the Heimlich maneuver on a choking dog.',
        author_id=admin_id,
        video_url='https://www.youtube.com/embed/placeholder1',
        duration='4:32',
        transcript='Welcome to the PetAid visual guide. If your dog is choking, stay calm. In this video we show the correct hand placements for abdominal thrusts based on dog size...',
        species='Dog',
        severity='Critical'
    )
    video_dog_choking.verification_status = 'Approved'

    video_cat_choking = ContentFactory.create_content(
        content_type='video',
        title='Cat choking — signs and response',
        description='Instructional video detailing response signs for choking felines.',
        author_id=admin_id,
        video_url='https://www.youtube.com/embed/placeholder2',
        duration='3:15',
        transcript='Choking signs in cats include pawing at the mouth, coughing, and blue gums. Watch this step-by-step demonstration...',
        species='Cat',
        severity='Critical'
    )
    video_cat_choking.verification_status = 'Approved'

    video_dog_cpr = ContentFactory.create_content(
        content_type='video',
        title='Dog CPR — step by step',
        description='Visual guide on administering Cardiopulmonary Resuscitation on dogs.',
        author_id=admin_id,
        video_url='https://www.youtube.com/embed/placeholder3',
        duration='5:48',
        transcript='In this video, we cover chest compressions and rescue breaths. Check for breathing, place hands over the heart...',
        species='Dog',
        severity='Critical'
    )
    video_dog_cpr.verification_status = 'Approved'

    video_rabbit_seizure = ContentFactory.create_content(
        content_type='video',
        title='How to handle a rabbit seizure',
        description='Watch what to do when a rabbit undergoes a seizure.',
        author_id=admin_id,
        video_url='https://www.youtube.com/embed/placeholder4',
        duration='2:50',
        transcript='First rule: do not touch or restrain. Simply move hard objects away...',
        species='Rabbit',
        severity='Moderate'
    )
    video_rabbit_seizure.verification_status = 'Approved'

    video_wound_care = ContentFactory.create_content(
        content_type='video',
        title='Wound care for cats and dogs',
        description='Step-by-step treatment of cuts, scrapes, and bleeding.',
        author_id=admin_id,
        video_url='https://www.youtube.com/embed/placeholder5',
        duration='4:10',
        transcript='Clean with sterile water, apply direct pressure, and wrap carefully without cutting off circulation...',
        species='Dog, Cat',
        severity='Moderate'
    )
    video_wound_care.verification_status = 'Approved'

    # Video 6: Hamster wound care (Pending - Vet Review workflow)
    video_hamster_wound = ContentFactory.create_content(
        content_type='video',
        title='Hamster wound care — visual guide',
        description='How to treat minor cuts on a hamster safely.',
        author_id=admin_id,
        video_url='https://www.youtube.com/embed/placeholder6',
        duration='3:40',
        transcript='Hamsters require very delicate care. Clean the wound using a cotton swab and diluted antiseptic...',
        species='Hamster',
        severity='Moderate'
    )
    video_hamster_wound.verification_status = 'Pending'

    db.session.add_all([
        video_dog_choking, video_cat_choking, video_dog_cpr,
        video_rabbit_seizure, video_wound_care, video_hamster_wound
    ])
    db.session.commit()

    # ==========================================
    # 5. Quizzes Seeding
    # ==========================================
    # Quiz 1: Dog Emergency Basics (Approved)
    quiz_dog = ContentFactory.create_content(
        content_type='quiz',
        title='Dog Emergency Basics',
        description='Test your knowledge on basic first-aid for dogs, including choking and CPR.',
        author_id=admin_id,
        species='Dog'
    )
    quiz_dog.verification_status = 'Approved'
    db.session.add(quiz_dog)
    db.session.commit()

    questions_dog = [
        QuizQuestion(
            quiz_id=quiz_dog.id,
            question_text='What is the first sign of choking in a dog?',
            option_a='Sleeping excessively',
            option_b='Pawing at the mouth',
            option_c='Wagging tail rapidly',
            option_d='Running in circles',
            correct_option='B'
        ),
        QuizQuestion(
            quiz_id=quiz_dog.id,
            question_text='How many back blows should you apply to a choking dog?',
            option_a='Up to 5',
            option_b='Exactly 10',
            option_c='None, back blows are dangerous',
            option_d='Continuous blows until clear',
            correct_option='A'
        ),
        QuizQuestion(
            quiz_id=quiz_dog.id,
            question_text='What is the first thing you should do if your dog is choking and you can see the object in its mouth?',
            option_a='Do a blind finger sweep to remove the object',
            option_b='Carefully try to remove it with two fingers if safely reachable',
            option_c='Immediately apply abdominal thrusts',
            option_d='Give the dog water to try to dislodge the object',
            correct_option='B'
        ),
        QuizQuestion(
            quiz_id=quiz_dog.id,
            question_text='What should you do after successfully removing a choking object?',
            option_a='Nothing, the dog is fine',
            option_b='Take the dog to a vet immediately to check for internal damage',
            option_c='Feed them a large treat',
            option_d='Let them run around to recover',
            correct_option='B'
        ),
        QuizQuestion(
            quiz_id=quiz_dog.id,
            question_text='Where do you place your fist when applying abdominal thrusts on a dog?',
            option_a='Directly on the throat',
            option_b='On the chest bone',
            option_c='Just below the rib cage',
            option_d='On the lower back',
            correct_option='C'
        )
    ]
    db.session.add_all(questions_dog)

    # Quiz 2: Cat Emergency Basics (Approved)
    quiz_cat = ContentFactory.create_content(
        content_type='quiz',
        title='Cat Emergency Basics',
        description='Test your knowledge on common cat emergency responses.',
        author_id=admin_id,
        species='Cat'
    )
    quiz_cat.verification_status = 'Approved'
    db.session.add(quiz_cat)
    db.session.commit()

    q_cat = QuizQuestion(
        quiz_id=quiz_cat.id,
        question_text='What should you do first when a cat is choking?',
        option_a='Gently wrap the cat in a towel to restrain it safely',
        option_b='Shake the cat by its hind legs',
        option_c='Pour water down its throat',
        option_d='Leave it alone to see if it clears itself',
        correct_option='A'
    )
    db.session.add(q_cat)

    # Quiz 3: Rabbit and Hamster Care (Approved)
    quiz_rabbit = ContentFactory.create_content(
        content_type='quiz',
        title='Rabbit and Hamster Care',
        description='Test your knowledge on caring for small pets in medical emergencies.',
        author_id=admin_id,
        species='Rabbit, Hamster'
    )
    quiz_rabbit.verification_status = 'Approved'
    db.session.add(quiz_rabbit)
    db.session.commit()

    q_rab = QuizQuestion(
        quiz_id=quiz_rabbit.id,
        question_text='Should you put anything in a rabbit\'s mouth during a active seizure?',
        option_a='Yes, a spoon to prevent tongue biting',
        option_b='No, never put anything in their mouth',
        option_c='Yes, small drops of water to soothe them',
        option_d='Yes, soft leafy greens',
        correct_option='B'
    )
    db.session.add(q_rab)

    # Quiz 4: General Pet First-Aid (Pending - Vet Review workflow)
    quiz_general = ContentFactory.create_content(
        content_type='quiz',
        title='General Pet First-Aid',
        description='Comprehensive quiz on general first-aid principles for all pets.',
        author_id=admin_id,
        species='All pets'
    )
    quiz_general.verification_status = 'Pending'
    db.session.add(quiz_general)
    db.session.commit()

    q_gen = QuizQuestion(
        quiz_id=quiz_general.id,
        question_text='What is the primary rule in any pet emergency?',
        option_a='Panic immediately',
        option_b='Stay calm and ensure the environment is safe',
        option_c='Administer human painkillers',
        option_d='Wait 24 hours before taking action',
        correct_option='B'
    )
    db.session.add(q_gen)
    db.session.commit()

    # ==========================================
    # 6. Quiz Results History Seeding
    # ==========================================
    # Let's seed attempts for John Doe (user_id)
    attempt1 = QuizResult(
        score=3,
        total_questions=5,
        timestamp=datetime.utcnow() - timedelta(days=3),
        user_id=user_id,
        quiz_id=quiz_dog.id
    )
    attempt2 = QuizResult(
        score=4,
        total_questions=5,
        timestamp=datetime.utcnow() - timedelta(hours=2),
        user_id=user_id,
        quiz_id=quiz_dog.id
    )
    attempt3 = QuizResult(
        score=1,
        total_questions=1,
        timestamp=datetime.utcnow() - timedelta(days=1),
        user_id=user_id,
        quiz_id=quiz_cat.id
    )
    db.session.add_all([attempt1, attempt2, attempt3])

    # ==========================================
    # 7. Emergency Cases Seeding
    # ==========================================
    case1 = EmergencyCase(
        title='What to do if your dog is choking',
        description='Step-by-step guide to clear airway obstruction in dogs safely and quickly.',
        severity='Critical',
        species='Dog',
        keywords='choking, dog, blow, thrust, airway, biscuit',
        guide_id=guide_dog_choking.id,
        video_id=video_dog_choking.id
    )
    case2 = EmergencyCase(
        title='Cat choking — signs and immediate response',
        description='Recognise choking symptoms in cats and apply the correct first-aid response.',
        severity='Critical',
        species='Cat',
        keywords='choking, cat, block, air, throat, mochi',
        guide_id=guide_cat_choking.id,
        video_id=video_cat_choking.id
    )
    case3 = EmergencyCase(
        title='Rabbit choking on food — what to do',
        description='How to identify and respond to a rabbit choking on food or a foreign object.',
        severity='Moderate',
        species='Rabbit',
        keywords='choking, rabbit, pellet, swing, centi',
        guide_id=guide_rabbit_choking.id,
        video_id=video_rabbit_seizure.id  # Related video
    )
    case4 = EmergencyCase(
        title='Hamster choking prevention and response',
        description='Tips to prevent choking in hamsters and what to do if it occurs.',
        severity='Moderate',
        species='Hamster',
        keywords='choking, hamster, cheeks, seeds, pouch',
        guide_id=guide_hamster_choking.id
    )
    case5 = EmergencyCase(
        title='Rabbit seizure — immediate response',
        description='Recognise seizure symptoms in rabbits and clear the environment.',
        severity='Moderate',
        species='Rabbit',
        keywords='seizure, rabbit, shaking, fit',
        guide_id=guide_rabbit_seizure.id,
        video_id=video_rabbit_seizure.id
    )
    db.session.add_all([case1, case2, case3, case4, case5])
    db.session.commit()

    print("Database seeding completed successfully!")
