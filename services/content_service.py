"""
Content Service Layer

This module provides the ContentService class which acts as an abstraction layer
between the API endpoints and the database. It handles:
- Database queries using Supabase client
- Caching with configurable TTL
- Data transformation from database format to API format

NOTE: This project runs in database-only mode. The fallback_enabled flag is
kept for API compatibility but defaults to False. If Supabase is unavailable,
endpoints will receive a clean ServiceUnavailableError instead of an
ImportError from non-existent fallback data files.
"""

from typing import Optional, Dict, List, Any


class ServiceUnavailableError(RuntimeError):
    """Raised when the database is unavailable and no fallback is configured."""


class ContentService:
    """
    Service layer for content management with database and caching support.

    Provides methods to retrieve quiz questions, scam definitions, and practice
    quizzes from the database with automatic in-memory caching.
    """

    def __init__(self, supabase_client, cache_manager):
        """
        Initialize the ContentService.

        Args:
            supabase_client: Supabase client instance for database operations
            cache_manager: Cache manager instance for caching results
        """
        self.db = supabase_client
        self.cache = cache_manager
        # Keep this flag False — fallback Python data files do not exist.
        # Set to True only if you add data/quiz_questions.py, data/scams.py,
        # and data/practice_quizzes.py with the appropriate data structures.
        self.fallback_enabled = False

    @staticmethod
    def _normalize_token(value: Optional[str]) -> str:
        return (value or '').strip().lower().replace('-', '_').replace(' ', '_')

    def _difficulty_variants(self, difficulty: str) -> List[str]:
        normalized = self._normalize_token(difficulty)
        variants = [normalized]
        if normalized == 'hard':
            variants.append('difficult')
        elif normalized == 'difficult':
            variants.append('hard')
        return list(dict.fromkeys(v for v in variants if v))

    def _scam_type_variants(self, scam_type: str) -> List[str]:
        normalized = self._normalize_token(scam_type)
        variants = [
            scam_type,
            normalized,
            normalized.replace('_', ' '),
            normalized.replace('_', '-'),
        ]
        return list(dict.fromkeys(v for v in variants if v))

    def get_quiz_questions(self, difficulty: str = 'easy', use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Retrieve quiz questions by difficulty level.

        Args:
            difficulty: 'easy', 'medium', or 'difficult'
            use_cache: Whether to use cached results

        Returns:
            List of question dictionaries in API format
        """
        cache_key = f"quiz_questions:{difficulty}"

        if use_cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached

        try:
            questions = []
            for variant in self._difficulty_variants(difficulty):
                result = self.db.table('quiz_questions') \
                    .select('*') \
                    .eq('difficulty', variant) \
                    .eq('is_active', True) \
                    .execute()
                questions = self._transform_quiz_questions(result.data or [])
                if questions:
                    break
            self.cache.set(cache_key, questions, timeout=3600)
            return questions

        except Exception as e:
            raise ServiceUnavailableError(
                f"Failed to load quiz questions (difficulty={difficulty}): {e}"
            ) from e

    def get_scam_definitions(self, scam_type: Optional[str] = None, use_cache: bool = True) -> Dict[str, Any]:
        """
        Retrieve scam definitions, optionally filtered by type.

        Args:
            scam_type: Optional scam type identifier
            use_cache: Whether to use cached results

        Returns:
            Dictionary of scam definitions, or a single definition dict, or None
        """
        cache_key = f"scam_definitions:{scam_type or 'all'}"

        if use_cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached

        try:
            query = self.db.table('scam_definitions') \
                .select('*') \
                .eq('is_active', True)

            if scam_type:
                result = None
                for variant in self._scam_type_variants(scam_type):
                    result = self.db.table('scam_definitions') \
                        .select('*') \
                        .eq('is_active', True) \
                        .eq('scam_type', variant) \
                        .execute()
                    if result.data:
                        break
            else:
                result = query.execute()

            scams = self._transform_scam_definitions((result.data or []) if result else [], scam_type)
            self.cache.set(cache_key, scams, timeout=3600)
            return scams

        except Exception as e:
            raise ServiceUnavailableError(
                f"Failed to load scam definitions (scam_type={scam_type}): {e}"
            ) from e

    def get_practice_quizzes(self, scam_type: str, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Retrieve practice quiz questions for a specific scam type.

        Args:
            scam_type: Scam type identifier
            use_cache: Whether to use cached results

        Returns:
            List of practice question dictionaries in API format
        """
        cache_key = f"practice_quizzes:{scam_type}"

        if use_cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached

        try:
            questions = []
            for variant in self._scam_type_variants(scam_type):
                result = self.db.table('practice_quizzes') \
                    .select('*') \
                    .eq('scam_type', variant) \
                    .eq('is_active', True) \
                    .order('display_order') \
                    .execute()
                questions = self._transform_practice_quizzes(result.data or [])
                if questions:
                    break
            self.cache.set(cache_key, questions, timeout=3600)
            return questions

        except Exception as e:
            raise ServiceUnavailableError(
                f"Failed to load practice quizzes (scam_type={scam_type}): {e}"
            ) from e

    # ---------------------------------------------------------------------------
    # Transform helpers
    # ---------------------------------------------------------------------------

    def _transform_quiz_questions(self, db_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform database rows to API format for quiz questions."""
        return [
            {
                'question': row['question_text'],
                'options': [
                    row['option_1'],
                    row['option_2'],
                    row['option_3'],
                    row['option_4']
                ],
                'correct': row['correct_answer_index'],
                'explanation': row['explanation']
            }
            for row in db_rows
        ]

    def _transform_scam_definitions(self, db_rows: List[Dict[str, Any]], single_type: Optional[str] = None) -> Dict[str, Any]:
        """Transform database rows to API format for scam definitions."""
        scams = {}
        for row in db_rows:
            scams[row['scam_type']] = {
                'title': row['title'],
                'icon': row['icon'],
                'color': row['color'],
                'description': row['description'],
                'warning_signs': row['warning_signs'],
                'prevention': row['prevention_tips'],
                # Include video_url if present (used by the awareness/scam_detail pages)
                'video_url': row.get('video_url'),
            }

        if single_type:
            return scams.get(single_type)
        return scams

    def _transform_practice_quizzes(self, db_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform database rows to API format for practice quizzes."""
        return [
            {
                'question': row['question_text'],
                'options': [
                    row['option_1'],
                    row['option_2'],
                    row['option_3'],
                    row['option_4']
                ],
                'correct': row['correct_answer_index'],
                'explanation': row['explanation']
            }
            for row in db_rows
        ]
