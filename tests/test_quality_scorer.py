"""Tests for QualityScorer service."""
import pytest
from backend.app.services.quality_scorer import QualityScorer


@pytest.fixture
def scorer():
    return QualityScorer()


@pytest.fixture
def good_test_code():
    return """import XCTest

final class LoginTests: XCTestCase {
    func testLoginWithValidCredentials() throws {
        let app = XCUIApplication()
        app.launchArguments = ["-AppleLanguages", "(en)", "-AppleLocale", "en_US"]
        app.launch()
        
        // Enter email
        let emailField = app.textFields["emailTextField"]
        XCTAssertTrue(emailField.waitForExistence(timeout: 5))
        emailField.tap()
        emailField.typeText("test@example.com")
        
        // Enter password
        let passwordField = app.secureTextFields["passwordTextField"]
        XCTAssertTrue(passwordField.waitForExistence(timeout: 5))
        passwordField.tap()
        passwordField.typeText("password123")
        
        // Tap login button
        let loginButton = app.buttons["loginButton"]
        XCTAssertTrue(loginButton.waitForExistence(timeout: 5))
        loginButton.tap()
        
        // Verify success
        let itemList = app.tables["itemList"]
        XCTAssertTrue(itemList.waitForExistence(timeout: 10))
    }
}
"""


@pytest.fixture
def poor_test_code():
    return """import XCTest

class BadTest: XCTestCase {
    func test() {
        let app = XCUIApplication()
        app.launch()
        sleep(3)
        app.buttons["someButton"].tap()
    }
}
"""


def test_score_good_test(scorer, good_test_code):
    """Test scoring of a well-written test."""
    result = scorer.score(good_test_code, "test login with valid credentials")
    
    assert "overall_score" in result
    assert "confidence" in result
    assert "scores" in result
    assert "recommendations" in result
    assert "grade" in result
    
    # Good test should score high
    assert result["overall_score"] >= 80
    assert result["grade"] in ["A", "B"]
    assert result["confidence"] in ["High", "Medium"]


def test_score_poor_test(scorer, poor_test_code):
    """Test scoring of a poorly-written test."""
    result = scorer.score(poor_test_code, "test something")
    
    # Poor test should score low
    assert result["overall_score"] < 70
    assert result["grade"] in ["C", "D", "F"]
    assert result["confidence"] == "Low"
    
    # Should have recommendations
    assert len(result["recommendations"]) > 0


def test_best_practices_score(scorer, good_test_code):
    """Test best practices scoring."""
    report = scorer.score(good_test_code, "test login")
    bp_score = report["scores"]["best_practices"]
    
    assert bp_score["score"] >= 80
    assert bp_score["checks"]["uses_waits"] is True
    assert bp_score["checks"]["has_assertions"] is True
    assert bp_score["checks"]["locale_configured"] is True
    assert bp_score["checks"]["no_sleep"] is True


def test_structure_score(scorer, good_test_code):
    """Test structure scoring."""
    report = scorer.score(good_test_code, "test login")
    struct_score = report["scores"]["structure"]
    
    assert struct_score["score"] == 100
    assert struct_score["checks"]["has_import_xctest"] is True
    assert struct_score["checks"]["has_class_definition"] is True
    assert struct_score["checks"]["has_test_method"] is True
    assert struct_score["checks"]["balanced_braces"] is True


def test_maintainability_score(scorer, good_test_code):
    """Test maintainability scoring."""
    report = scorer.score(good_test_code, "test login")
    maint_score = report["scores"]["maintainability"]
    
    assert maint_score["score"] >= 70
    assert maint_score["checks"]["has_comments"] is True
    assert maint_score["checks"]["reasonable_length"] is True
    assert maint_score["lines_of_code"] > 0
    assert maint_score["comment_lines"] > 0


def test_coverage_score_login(scorer):
    """Test coverage scoring for login test."""
    code = """
    let emailField = app.textFields["emailTextField"]
    emailField.typeText("test@example.com")
    let passwordField = app.secureTextFields["passwordTextField"]
    passwordField.typeText("password123")
    app.buttons["loginButton"].tap()
    XCTAssertTrue(app.tables["itemList"].waitForExistence(timeout: 10))
    """
    
    report = scorer.score(code, "test login with email and password")
    cov_score = report["scores"]["coverage"]
    
    # Should detect login, type, tap, verify actions
    assert cov_score["score"] >= 60


def test_recommendations_for_missing_waits(scorer):
    """Test that missing waits generate recommendations."""
    code = """
    import XCTest
    class Test: XCTestCase {
        func testSomething() {
            let app = XCUIApplication()
            app.launch()
            app.buttons["btn"].tap()
        }
    }
    """
    
    result = scorer.score(code, "test tap button")
    
    # Should recommend adding waits
    assert any("waitForExistence" in rec for rec in result["recommendations"])


def test_recommendations_for_sleep(scorer):
    """Test that sleep() usage triggers strong recommendation."""
    code = """
    import XCTest
    class Test: XCTestCase {
        func testSomething() {
            let app = XCUIApplication()
            app.launch()
            sleep(3)
            app.buttons["btn"].tap()
        }
    }
    """
    
    result = scorer.score(code, "test something")
    
    # Should flag sleep as bad practice
    assert any("sleep" in rec.lower() for rec in result["recommendations"])
    assert result["scores"]["best_practices"]["checks"]["no_sleep"] is False


def test_grade_calculation(scorer):
    """Test grade calculation."""
    assert scorer._score_to_grade(95) == "A"
    assert scorer._score_to_grade(85) == "B"
    assert scorer._score_to_grade(75) == "C"
    assert scorer._score_to_grade(65) == "D"
    assert scorer._score_to_grade(50) == "F"


def test_confidence_calculation(scorer):
    """Test confidence level calculation."""
    # High confidence: perfect structure + high overall
    scores = {
        "structure": {"score": 100},
        "best_practices": {"score": 90},
    }
    assert scorer._calculate_confidence(scores, 85) == "High"
    
    # Low confidence: poor structure
    scores = {
        "structure": {"score": 60},
        "best_practices": {"score": 80},
    }
    assert scorer._calculate_confidence(scores, 70) == "Low"
    
    # Medium confidence: decent but not perfect
    scores = {
        "structure": {"score": 90},
        "best_practices": {"score": 75},
    }
    assert scorer._calculate_confidence(scores, 75) == "Medium"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
