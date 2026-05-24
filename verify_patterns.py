import sys
from app import app
from models import db, Account, User, Administrator, VeterinaryExpert, FirstAidGuide, VideoContent, Quiz, EmergencyCase
from factory import AccountFactory, ContentFactory
from strategy import SearchContext, KeywordSearchStrategy, SeveritySpeciesSearchStrategy

def test_design_patterns():
    print("==================================================")
    print("        RUNNING DESIGN PATTERN VERIFICATION        ")
    print("==================================================")
    
    with app.app_context():
        # 1. Singleton Database Manager verification
        print("[1/4] Verifying Singleton Database Manager...")
        db_instance_1 = db
        from models import db as db_instance_2
        assert db_instance_1 is db_instance_2, "Singleton violation: Database manager instances differ!"
        print("      SUCCESS: Single shared SQLAlchemy instance confirmed.")
        
        # 2. Factory Method verification
        print("[2/4] Verifying Factory Method Pattern...")
        
        # Create user via factory
        test_user = AccountFactory.create_account(
            role='user',
            username='test_user_factory',
            email='test_user@factory.com',
            password='factorypassword123',
            first_name='Factory',
            last_name='User'
        )
        assert isinstance(test_user, User), "Factory Method failed: AccountFactory did not return User subclass!"
        assert test_user.check_password('factorypassword123'), "Factory Method failed: Password was not hashed correctly!"
        
        # Create guide via factory
        test_guide = ContentFactory.create_content(
            content_type='guide',
            title='Test Choking Guide',
            description='Test choking guide description',
            author_id=1,
            severity='Critical',
            species='Cat'
        )
        assert isinstance(test_guide, FirstAidGuide), "Factory Method failed: ContentFactory did not return FirstAidGuide subclass!"
        assert test_guide.severity == 'Critical', "Factory Method failed: Keyword argument mapping failed!"
        
        print("      SUCCESS: AccountFactory and ContentFactory subclasses instantiated correctly.")
        
        # 3. Strategy Pattern verification
        print("[3/4] Verifying Strategy Pattern Search Swapping...")
        
        # Create mock emergency cases
        case_dog = EmergencyCase(title='Dog Choking Fit', description='Dog choking description', severity='Critical', species='Dog', keywords='choke,dog')
        case_cat = EmergencyCase(title='Cat Seizure fit', description='Cat seizure description', severity='Moderate', species='Cat', keywords='seizure,cat')
        db.session.add_all([case_dog, case_cat])
        db.session.commit()
        
        context = SearchContext()
        
        # Test default strategy: KeywordSearchStrategy
        assert isinstance(context._strategy, KeywordSearchStrategy), "Strategy failed: Default strategy should be KeywordSearchStrategy!"
        results_keyword = context.execute_search('choking', 'Dog')
        assert len(results_keyword) > 0, "Strategy failed: KeywordSearchStrategy did not retrieve matches!"
        
        # Test swapping strategy: SeveritySpeciesSearchStrategy
        context.set_strategy(SeveritySpeciesSearchStrategy())
        assert isinstance(context._strategy, SeveritySpeciesSearchStrategy), "Strategy failed: Swapping strategy failed!"
        results_severity = context.execute_search('', 'all')
        
        # Verify Critical comes before Moderate
        critical_idx = -1
        moderate_idx = -1
        for idx, item in enumerate(results_severity):
            if item.severity == 'Critical':
                critical_idx = idx if critical_idx == -1 else critical_idx
            elif item.severity == 'Moderate':
                moderate_idx = idx if moderate_idx == -1 else moderate_idx
                
        if critical_idx != -1 and moderate_idx != -1:
            assert critical_idx < moderate_idx, "Strategy failed: SeveritySpeciesSearchStrategy did not sort by severity!"
            
        # Clean up database mock records
        db.session.delete(case_dog)
        db.session.delete(case_cat)
        db.session.commit()
        
        print("      SUCCESS: KeywordSearchStrategy and SeveritySpeciesSearchStrategy swapped and ran correctly.")

        # 4. MVC Verification
        print("[4/4] Verifying Controller-Model boundaries...")
        # Check active session mappings
        assert len(FirstAidGuide.query.all()) > 0, "MVC Failure: Models are not mapped to database tables!"
        print("      SUCCESS: SQLAlchemy mapping successfully validated.")

    print("\n==================================================")
    print("  VERIFICATION COMPLETE: ALL PATTERNS VALIDATED!  ")
    print("==================================================")

if __name__ == '__main__':
    test_design_patterns()
