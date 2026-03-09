"""Test Quality Scorer — analyzes generated Swift test code and assigns quality scores.

Evaluates:
- Best practices (waits, assertions, error handling)
- Code structure (imports, class definition, test methods)
- XCUITest patterns (app launch, element queries, navigation)
- Maintainability (comments, naming)
"""
import re
from typing import Dict, Any


class QualityScorer:
    """Analyzes Swift XCUITest code and returns quality metrics."""

    def score(self, swift_code: str, test_description: str) -> Dict[str, Any]:
        """Analyze test code and return quality scores.

        Args:
            swift_code: Generated Swift test code
            test_description: Original test description

        Returns:
            Dict with scores and recommendations
        """
        scores = {
            "best_practices": self._score_best_practices(swift_code),
            "structure": self._score_structure(swift_code),
            "maintainability": self._score_maintainability(swift_code),
            "coverage": self._score_coverage(swift_code, test_description),
        }

        # Overall score (weighted average)
        overall = (
            scores["best_practices"]["score"] * 0.40 +
            scores["structure"]["score"] * 0.25 +
            scores["maintainability"]["score"] * 0.15 +
            scores["coverage"]["score"] * 0.20
        )

        # Confidence level
        confidence = self._calculate_confidence(scores, overall)

        # Recommendations
        recommendations = self._generate_recommendations(scores)

        return {
            "overall_score": round(overall, 1),
            "confidence": confidence,
            "scores": scores,
            "recommendations": recommendations,
            "grade": self._score_to_grade(overall),
        }

    def _score_best_practices(self, code: str) -> Dict[str, Any]:
        """Score XCUITest best practices (0-100)."""
        checks = {
            "uses_waits": bool(re.search(r"waitForExistence\s*\(", code)),
            "has_assertions": bool(re.search(r"XCTAssert", code)),
            "locale_configured": bool(re.search(r'launchArguments.*AppleLanguages', code)),
            "app_launched": bool(re.search(r"app\.launch\(\)", code)),
            "no_sleep": "sleep(" not in code,
            "springboard_handling": "springboard" in code.lower() or "alert" in code.lower(),
        }

        score = sum(checks.values()) / len(checks) * 100
        issues = [k for k, v in checks.items() if not v]

        return {
            "score": round(score, 1),
            "checks": checks,
            "issues": issues,
        }

    def _score_structure(self, code: str) -> Dict[str, Any]:
        """Score code structure (0-100)."""
        checks = {
            "has_import_xctest": "import XCTest" in code,
            "has_class_definition": bool(re.search(r"class\s+\w+\s*:\s*XCTestCase", code)),
            "has_test_method": bool(re.search(r"func\s+test\w+\(", code)),
            "xcuiapplication_created": "XCUIApplication()" in code,
            "balanced_braces": code.count("{") == code.count("}"),
            "balanced_parens": code.count("(") == code.count(")"),
        }

        score = sum(checks.values()) / len(checks) * 100
        issues = [k for k, v in checks.items() if not v]

        return {
            "score": round(score, 1),
            "checks": checks,
            "issues": issues,
        }

    def _score_maintainability(self, code: str) -> Dict[str, Any]:
        """Score maintainability (0-100)."""
        lines = code.split("\n")
        non_empty_lines = [l for l in lines if l.strip()]
        comment_lines = [l for l in lines if l.strip().startswith("//")]

        checks = {
            "has_comments": len(comment_lines) > 0,
            "reasonable_length": 20 <= len(non_empty_lines) <= 200,
            "descriptive_class_name": bool(re.search(r"class\s+\w{5,40}Tests", code)),
            "no_hardcoded_waits": "sleep(" not in code,
            "descriptive_test_name": bool(re.search(r"func\s+test\w{10,}", code)),
        }

        # Comment ratio (aim for 10-30%)
        if non_empty_lines:
            comment_ratio = len(comment_lines) / len(non_empty_lines)
            checks["good_comment_ratio"] = 0.05 <= comment_ratio <= 0.30
        else:
            checks["good_comment_ratio"] = False

        score = sum(checks.values()) / len(checks) * 100
        issues = [k for k, v in checks.items() if not v]

        return {
            "score": round(score, 1),
            "checks": checks,
            "issues": issues,
            "lines_of_code": len(non_empty_lines),
            "comment_lines": len(comment_lines),
        }

    def _score_coverage(self, code: str, description: str) -> Dict[str, Any]:
        """Score how well the test covers the description (0-100)."""
        desc_lower = description.lower()
        code_lower = code.lower()

        # Extract key actions from description
        action_keywords = {
            "tap": ["tap", "click", "press"],
            "type": ["type", "enter", "input", "fill"],
            "scroll": ["scroll", "swipe"],
            "verify": ["verify", "check", "assert", "expect"],
            "navigate": ["navigate", "go to", "open"],
            "login": ["login", "sign in", "authenticate"],
        }

        coverage_checks = {}
        for action, keywords in action_keywords.items():
            if any(kw in desc_lower for kw in keywords):
                # Check if code implements this action
                if action == "tap":
                    coverage_checks[f"implements_{action}"] = ".tap()" in code_lower
                elif action == "type":
                    coverage_checks[f"implements_{action}"] = "typetext" in code_lower
                elif action == "scroll":
                    coverage_checks[f"implements_{action}"] = "swipe" in code_lower
                elif action == "verify":
                    coverage_checks[f"implements_{action}"] = "xctassert" in code_lower
                elif action == "navigate":
                    coverage_checks[f"implements_{action}"] = any(
                        x in code_lower for x in ["tap", "button", "tab"]
                    )
                elif action == "login":
                    coverage_checks[f"implements_{action}"] = any(
                        x in code_lower for x in ["email", "password", "login"]
                    )

        if not coverage_checks:
            # No specific actions detected in description
            score = 80.0  # Default neutral score
            coverage_checks["general_test"] = True
        else:
            score = sum(coverage_checks.values()) / len(coverage_checks) * 100

        return {
            "score": round(score, 1),
            "checks": coverage_checks,
        }

    def _calculate_confidence(self, scores: Dict, overall: float) -> str:
        """Calculate confidence level (High/Medium/Low)."""
        # High confidence if all structure checks pass and overall > 80
        if scores["structure"]["score"] == 100 and overall >= 80:
            return "High"
        # Low confidence if structure or best practices are poor
        elif scores["structure"]["score"] < 70 or scores["best_practices"]["score"] < 60:
            return "Low"
        else:
            return "Medium"

    def _generate_recommendations(self, scores: Dict) -> list:
        """Generate actionable recommendations based on scores."""
        recommendations = []

        # Best practices issues
        bp_issues = scores["best_practices"]["issues"]
        if "uses_waits" in bp_issues:
            recommendations.append(
                "⚠️ Add waitForExistence() calls before interacting with elements"
            )
        if "has_assertions" in bp_issues:
            recommendations.append("⚠️ Add XCTAssert statements to verify test outcomes")
        if "locale_configured" in bp_issues:
            recommendations.append(
                "⚠️ Set app.launchArguments for English locale to prevent keyboard switching"
            )
        if "no_sleep" in bp_issues:
            recommendations.append("❌ Remove sleep() calls — use waitForExistence() instead")

        # Structure issues
        struct_issues = scores["structure"]["issues"]
        if struct_issues:
            recommendations.append(
                f"⚠️ Fix structure issues: {', '.join(struct_issues)}"
            )

        # Maintainability issues
        maint_issues = scores["maintainability"]["issues"]
        if "has_comments" in maint_issues:
            recommendations.append("💡 Add comments to explain test logic")
        if "reasonable_length" in maint_issues:
            loc = scores["maintainability"]["lines_of_code"]
            if loc > 200:
                recommendations.append("💡 Test is too long — consider splitting into smaller tests")
            elif loc < 20:
                recommendations.append("💡 Test is too short — may not be comprehensive enough")

        # All good!
        if not recommendations:
            recommendations.append("✅ Test looks great! Ready to use.")

        return recommendations

    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
