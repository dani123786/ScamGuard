"""
Simple test script to verify the application is working correctly
"""

import sys
import os

def test_imports():
    """Test if all required modules are available"""
    print("Testing imports...")
    try:
        import flask
        print("✓ Flask is installed")
        return True
    except ImportError:
        print("✗ Flask is NOT installed")
        print("  Run: pip install -r requirements.txt")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        'templates/base.html',
        'templates/index.html',
        'templates/awareness.html',
        'templates/scam_detail.html',
        'templates/quiz.html',
        'templates/checker.html',
        'templates/resources.html',
        'templates/report.html',
        'static/css/style.css'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - MISSING!")
            all_exist = False
    
    return all_exist

def test_app_configuration():
    """Test if app.py is properly configured"""
    print("\nTesting app configuration...")
    
    try:
        from app import app
        from data.scams import SCAMS_DATA
        from data.quiz_questions import QUIZ_QUESTIONS
        
        # Test scams data
        if len(SCAMS_DATA) >= 9:
            print(f"✓ Scams data loaded ({len(SCAMS_DATA)} scam types)")
        else:
            print(f"✗ Expected at least 9 scam types, found {len(SCAMS_DATA)}")
            return False
        
        # Test quiz questions
        if len(QUIZ_QUESTIONS) >= 3:
            print(f"✓ Quiz questions loaded ({len(QUIZ_QUESTIONS)} difficulty levels)")
        else:
            print(f"✗ Expected 3 difficulty levels, found {len(QUIZ_QUESTIONS)}")
            return False
        
        # Test routes
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        required_routes = ['/', '/awareness', '/quiz', '/checker', '/resources', '/report']
        
        missing_routes = []
        for route in required_routes:
            if route in routes:
                print(f"✓ Route {route} exists")
            else:
                print(f"✗ Route {route} - MISSING!")
                missing_routes.append(route)
        
        return len(missing_routes) == 0
        
    except Exception as e:
        print(f"✗ Error loading app: {e}")
        return False

def test_templates():
    """Test if templates can be rendered"""
    print("\nTesting template rendering...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test main pages
            pages = [
                ('/', 'Home'),
                ('/awareness', 'Awareness'),
                ('/quiz', 'Quiz'),
                ('/checker', 'Checker'),
                ('/resources', 'Resources'),
                ('/report', 'Report')
            ]
            
            all_ok = True
            for url, name in pages:
                response = client.get(url)
                if response.status_code == 200:
                    print(f"✓ {name} page ({url}) - OK")
                else:
                    print(f"✗ {name} page ({url}) - Status {response.status_code}")
                    all_ok = False
            
            return all_ok
            
    except Exception as e:
        print(f"✗ Error testing templates: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("ScamGuard Application Test Suite")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("File Structure", test_file_structure),
        ("App Configuration", test_app_configuration),
        ("Template Rendering", test_templates)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your application is ready to run.")
        print("\nTo start the application, run:")
        print("  python app.py")
        print("\nThen open your browser to:")
        print("  http://localhost:5000")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
