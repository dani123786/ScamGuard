"""
Audit Logger

Records all content create/update/delete/rollback operations
into the content_versions table for a full audit trail.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

class AuditLogger:
    """
    Writes audit records to the content_versions table.

    Each method accepts the Supabase client, the table name, the record id,
    the acting user, and (where applicable) old/new values.
    """

    def __init__(self, db_client, changed_by: str = 'system'):
        """
        Args:
            db_client: Supabase client instance (may be None — logs are skipped gracefully).
            changed_by: Default username / identifier for the actor.
        """
        self.db = db_client
        self.default_user = changed_by

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log_create(
        self,
        table_name: str,
        record_id: int,
        new_value: Dict[str, Any],
        changed_by: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> bool:
        """Record a CREATE operation."""
        return self._write(
            table_name=table_name,
            record_id=record_id,
            change_type='CREATE',
            old_value=None,
            new_value=new_value,
            changed_by=changed_by,
            reason=reason,
        )

    def log_update(
        self,
        table_name: str,
        record_id: int,
        old_value: Dict[str, Any],
        new_value: Dict[str, Any],
        changed_by: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> bool:
        """Record an UPDATE operation, capturing both old and new values."""
        return self._write(
            table_name=table_name,
            record_id=record_id,
            change_type='UPDATE',
            old_value=old_value,
            new_value=new_value,
            changed_by=changed_by,
            reason=reason,
        )

    def log_delete(
        self,
        table_name: str,
        record_id: int,
        old_value: Dict[str, Any],
        changed_by: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> bool:
        """Record a DELETE (soft or hard) operation."""
        return self._write(
            table_name=table_name,
            record_id=record_id,
            change_type='DELETE',
            old_value=old_value,
            new_value=None,
            changed_by=changed_by,
            reason=reason,
        )

    def log_rollback(
        self,
        table_name: str,
        record_id: int,
        old_value: Dict[str, Any],
        new_value: Dict[str, Any],
        changed_by: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> bool:
        """
        Record a ROLLBACK operation.

        old_value = the state being reverted FROM.
        new_value = the state being restored TO (the previous version).
        """
        return self._write(
            table_name=table_name,
            record_id=record_id,
            change_type='ROLLBACK',
            old_value=old_value,
            new_value=new_value,
            changed_by=changed_by,
            reason=reason,
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _write(
        self,
        table_name: str,
        record_id: int,
        change_type: str,
        old_value: Optional[Dict[str, Any]],
        new_value: Optional[Dict[str, Any]],
        changed_by: Optional[str],
        reason: Optional[str],
    ) -> bool:
        """
        Insert a row into content_versions.

        Returns True on success, False if the DB is unavailable or the
        insert fails (so callers can log a warning without crashing).
        """
        if self.db is None:
            return False

        actor = changed_by or self.default_user

        record = {
            'table_name': table_name,
            'record_id': record_id,
            'change_type': change_type,
            'old_value': old_value,
            'new_value': new_value,
            'changed_by': actor,
            'changed_at': datetime.now(timezone.utc).isoformat(),
        }
        if reason:
            record['change_reason'] = reason

        try:
            self.db.table('content_versions').insert(record).execute()
            return True
        except Exception as exc:
            # Never let audit failures crash the main operation
            print(f"[AuditLogger] WARNING: failed to write audit record: {exc}")
            return False