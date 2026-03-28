"""
Content Validator

Validates content data before saving to the database.
Enforces field length, format, and integrity constraints
matching the SQL CHECK constraints in the schema.
"""

import re
from typing import Any, Dict, List, Tuple

# Regex for kebab-case scam type identifiers
SCAM_TYPE_RE = re.compile(r'^[a-z0-9-]+$')
# Hex colour: #RGB, #RRGGBB, #RGBA, #RRGGBBAA
HEX_COLOR_RE = re.compile(r'^#([0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$')
# Basic CSS named colours (non-exhaustive but covers common ones)
CSS_NAMED_COLORS = {
    'red', 'green', 'blue', 'yellow', 'orange', 'purple', 'pink',
    'black', 'white', 'gray', 'grey', 'cyan', 'magenta', 'brown',
    'lime', 'navy', 'teal', 'silver', 'gold', 'coral', 'salmon',
    'violet', 'indigo', 'maroon', 'olive', 'aqua', 'fuchsia',
}

ValidationResult = Tuple[bool, List[str]]


class ContentValidator:
    """
    Validates content items against schema constraints and business rules.

    All validate_* methods return (is_valid: bool, errors: list[str]).
    """

    # ------------------------------------------------------------------
    # Quiz question validation  (Req 11.1, 11.2, 11.3)
    # ------------------------------------------------------------------

    def validate_quiz_question(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate a quiz question dict.

        Required keys: question_text (or 'question'), option_1..option_4
        (or 'options' list), correct_answer_index (or 'correct'), explanation,
        difficulty.
        """
        errors: List[str] = []

        # Normalise: accept both DB-column names and API-format names
        question_text = data.get('question_text') or data.get('question', '')
        explanation = data.get('explanation', '')
        difficulty = data.get('difficulty', '')
        correct = data.get('correct_answer_index')
        if correct is None:
            correct = data.get('correct')

        # Options: accept list or individual columns
        if 'options' in data:
            options = data['options']
        else:
            options = [
                data.get('option_1', ''),
                data.get('option_2', ''),
                data.get('option_3', ''),
                data.get('option_4', ''),
            ]

        # question_text: 10–500 chars
        if not isinstance(question_text, str) or not (10 <= len(question_text) <= 500):
            errors.append(
                f"question_text must be between 10 and 500 characters "
                f"(got {len(question_text) if isinstance(question_text, str) else type(question_text).__name__})"
            )

        # options: exactly 4, each 1–200 chars
        if not isinstance(options, list) or len(options) != 4:
            errors.append("options must be a list of exactly 4 items")
        else:
            for i, opt in enumerate(options):
                if not isinstance(opt, str) or not (1 <= len(opt) <= 200):
                    errors.append(
                        f"option_{i+1} must be between 1 and 200 characters "
                        f"(got {len(opt) if isinstance(opt, str) else type(opt).__name__})"
                    )

        # correct_answer_index: 0–3
        if not isinstance(correct, int) or not (0 <= correct <= 3):
            errors.append("correct_answer_index must be an integer between 0 and 3")

        # explanation: 10–1000 chars
        if not isinstance(explanation, str) or not (10 <= len(explanation) <= 1000):
            errors.append(
                f"explanation must be between 10 and 1000 characters "
                f"(got {len(explanation) if isinstance(explanation, str) else type(explanation).__name__})"
            )

        # difficulty: enum
        if difficulty not in ('easy', 'medium', 'difficult'):
            errors.append(
                f"difficulty must be one of 'easy', 'medium', 'difficult' (got '{difficulty}')"
            )

        return len(errors) == 0, errors

    # ------------------------------------------------------------------
    # Scam definition validation  (Req 6.5, 11.4, 11.5)
    # ------------------------------------------------------------------

    def validate_scam_definition(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate a scam definition dict.

        Required keys: scam_type, title, icon, color, description,
        warning_signs, prevention_tips (or 'prevention').
        """
        errors: List[str] = []

        scam_type = data.get('scam_type', '')
        title = data.get('title', '')
        icon = data.get('icon', '')
        color = data.get('color', '')
        description = data.get('description', '')
        warning_signs = data.get('warning_signs', [])
        prevention = data.get('prevention_tips') or data.get('prevention', [])

        # scam_type: kebab-case, 1–50 chars
        if not isinstance(scam_type, str) or not scam_type:
            errors.append("scam_type is required")
        elif len(scam_type) > 50:
            errors.append("scam_type must be at most 50 characters")
        elif not SCAM_TYPE_RE.match(scam_type):
            errors.append(
                "scam_type must contain only lowercase letters, numbers, and hyphens"
            )

        # title: required, non-empty, max 200
        if not isinstance(title, str) or not title.strip():
            errors.append("title is required")
        elif len(title) > 200:
            errors.append("title must be at most 200 characters")

        # icon: required
        if not isinstance(icon, str) or not icon.strip():
            errors.append("icon is required")

        # color: hex or CSS named colour
        if not isinstance(color, str) or not color.strip():
            errors.append("color is required")
        elif not self._is_valid_color(color):
            errors.append(
                f"color must be a valid hex code (e.g. #e74c3c) or CSS color name (got '{color}')"
            )

        # description: 20–2000 chars
        if not isinstance(description, str) or not (20 <= len(description) <= 2000):
            errors.append(
                f"description must be between 20 and 2000 characters "
                f"(got {len(description) if isinstance(description, str) else type(description).__name__})"
            )

        # warning_signs: list of strings
        if not isinstance(warning_signs, list):
            errors.append("warning_signs must be a list")
        else:
            for i, sign in enumerate(warning_signs):
                if not isinstance(sign, str):
                    errors.append(f"warning_signs[{i}] must be a string")

        # prevention: list of strings
        if not isinstance(prevention, list):
            errors.append("prevention_tips must be a list")
        else:
            for i, tip in enumerate(prevention):
                if not isinstance(tip, str):
                    errors.append(f"prevention_tips[{i}] must be a string")

        return len(errors) == 0, errors

    # ------------------------------------------------------------------
    # Practice quiz validation
    # ------------------------------------------------------------------

    def validate_practice_quiz(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate a practice quiz question dict.

        Requires all quiz question fields plus scam_type.
        """
        errors: List[str] = []

        # scam_type is required for practice quizzes
        scam_type = data.get('scam_type', '')
        if not isinstance(scam_type, str) or not scam_type.strip():
            errors.append("scam_type is required for practice quiz questions")
        elif not SCAM_TYPE_RE.match(scam_type):
            errors.append(
                "scam_type must contain only lowercase letters, numbers, and hyphens"
            )

        # Reuse quiz question validation for the rest
        _, q_errors = self.validate_quiz_question(data)
        errors.extend(q_errors)

        return len(errors) == 0, errors

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_valid_color(value: str) -> bool:
        """Return True if value is a valid hex colour or CSS named colour."""
        if HEX_COLOR_RE.match(value):
            return True
        if value.lower() in CSS_NAMED_COLORS:
            return True
        return False