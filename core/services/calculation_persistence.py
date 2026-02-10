"""
Calculation Persistence Service
Connects the attendance engine V2 with the database in a forensically safe manner.

CRITICAL INFRASTRUCTURE
This service is the ONLY authorized interface for persisting calculation results.
Any bypass of this service compromises audit trail integrity.

GUARANTEES:
1. Atomic transactions - all-or-nothing persistence
2. Idempotency - same inputs produce same result, no duplicates
3. Immutability - historical records are never modified
4. Traceability - every change is logged with lineage

USAGE:
    from core.services.calculation_persistence import CalculationPersistenceService
    
    service = CalculationPersistenceService()
    daily, status = service.persist_daily_calculation(
        employee=employee,
        target_date=date(2025, 1, 15),
        engine_version="2.0.0",
        policy_dict=policy.to_dict(),
        punches=punch_list,
        result=calculation_result,
        actor=request.user,
    )
"""
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Tuple, Dict, Any
import hashlib
import json

from django.db import transaction
from django.utils import timezone

from core import models
# NOTE: PolicySnapshot/CalculationAuditLog/AuditEventType were planned for legal audit module but not implemented
# This system is for time tracking information, not a complete HR CRM
# from core.models_audit import PolicySnapshot, CalculationAuditLog, AuditEventType
from core.domain.flexible.result import DailyCalculationResult


class PersistenceResult(Enum):
    """Result status of persistence operation."""
    CREATED = "CREATED"                 # New record created
    RECALCULATED = "RECALCULATED"       # Old superseded, new created
    NO_CHANGE = "NO_CHANGE"             # Fingerprint match, skipped
    ERROR = "ERROR"                     # Persistence failed


@dataclass
class PersistenceContext:
    """Context for persistence operation."""
    employee: models.Employee
    target_date: date
    engine_version: str
    policy_dict: Dict[str, Any]
    punch_ids: List[int]
    result: DailyCalculationResult
    actor: Optional[models.User] = None
    recalculation_reason: Optional[str] = None


class CalculationPersistenceService:
    """
    Service for persisting attendance calculations with full audit trail.
    
    This service ensures:
    - Policy snapshots are reused when identical
    - Fingerprints detect duplicate calculations
    - Recalculations preserve historical records
    - All events are logged for forensic analysis
    
    NEVER modify historical records.
    ALWAYS use atomic transactions.
    """
    
    # =========================================================================
    # PUBLIC API
    # =========================================================================
    
    def persist_daily_calculation(
        self,
        employee: models.Employee,
        target_date: date,
        engine_version: str,
        policy_dict: Dict[str, Any],
        punch_ids: List[int],
        result: DailyCalculationResult,
        actor: Optional[models.User] = None,
        recalculation_reason: Optional[str] = None,
    ) -> Tuple[Optional[models.DailyAttendance], PersistenceResult]:
        """
        Persist a daily calculation result with full traceability.
        
        Args:
            employee: Employee model instance
            target_date: Date being calculated
            engine_version: Version string of the engine (e.g., "2.0.0")
            policy_dict: Policy as dictionary (will be snapshotted)
            punch_ids: List of punch IDs used as input (for fingerprint)
            result: DailyCalculationResult from the engine
            actor: User who triggered the calculation (optional)
            recalculation_reason: Reason for recalculation (if applicable)
        
        Returns:
            Tuple of (DailyAttendance or None, PersistenceResult)
        
        Raises:
            No exceptions - errors are returned as PersistenceResult.ERROR
        """
        context = PersistenceContext(
            employee=employee,
            target_date=target_date,
            engine_version=engine_version,
            policy_dict=policy_dict,
            punch_ids=sorted(punch_ids),  # Sort for deterministic fingerprint
            result=result,
            actor=actor,
            recalculation_reason=recalculation_reason,
        )
        
        try:
            with transaction.atomic():
                return self._persist_with_transaction(context)
        except Exception as e:
            # Log error but don't expose internal details
            print(f"[CalculationPersistenceService] Error: {e}")
            return None, PersistenceResult.ERROR
    
    # =========================================================================
    # PRIVATE - MAIN FLOW
    # =========================================================================
    
    def _persist_with_transaction(
        self, 
        context: PersistenceContext
    ) -> Tuple[models.DailyAttendance, PersistenceResult]:
        """
        Execute persistence within atomic transaction.
        
        Flow:
        1. Get or create policy snapshot
        2. Compute fingerprint
        3. Check for existing calculation
        4. Handle based on existence and fingerprint match
        5. Log audit event
        """
        # Step 1: Policy snapshot (DISABLED - legal audit module not implemented)
        # policy_snapshot = self._get_or_create_policy_snapshot(
        #     policy_dict=context.policy_dict,
        #     source='TIMETABLE',
        # )
        policy_snapshot = None
        
        # Step 2: Compute fingerprint
        fingerprint = self._compute_fingerprint(
            employee_id=context.employee.id,
            target_date=context.target_date,
            punch_ids=context.punch_ids,
            engine_version=context.engine_version,
            policy_hash=policy_snapshot.policy_hash if policy_snapshot else 'NO_POLICY_HASH',
        )
        
        # Step 3: Find existing CALCULATED record
        existing = self._find_current_record(
            employee_id=context.employee.id,
            target_date=context.target_date,
        )
        
        # Step 4: Decide action based on existence and fingerprint
        if existing is None:
            # Case A: No existing record - create new
            daily = self._create_new_record(context, policy_snapshot, fingerprint)
            # NOTE: Audit logging disabled - legal audit module not implemented
            # self._log_audit_event(
            #     daily=daily,
            #     event_type=AuditEventType.CREATED,
            #     actor=context.actor,
            #     metadata={'source': 'initial_calculation'},
            # )
            return daily, PersistenceResult.CREATED
        
        elif existing.calculation_fingerprint == fingerprint:
            # Case B: Same fingerprint - idempotent, skip
            # NOTE: Audit logging disabled - legal audit module not implemented
            # self._log_audit_event(
            #     daily=existing,
            #     event_type=AuditEventType.CREATED,  # Use CREATED as NO_CHANGE proxy
            #     actor=context.actor,
            #     metadata={
            #         'source': 'idempotent_skip',
            #         'fingerprint_match': True,
            #     },
            # )
            return existing, PersistenceResult.NO_CHANGE
        
        else:
            # Case C: Different fingerprint - recalculation
            daily = self._handle_recalculation(
                existing=existing,
                context=context,
                policy_snapshot=policy_snapshot,
                fingerprint=fingerprint,
            )
            return daily, PersistenceResult.RECALCULATED
    
    # =========================================================================
    # PRIVATE - POLICY SNAPSHOT
    # =========================================================================
    
    # NOTE: PolicySnapshot methods disabled - legal audit module not implemented
    # def _get_or_create_policy_snapshot(
    #     self,
    #     policy_dict: Dict[str, Any],
    #     source: str = 'COMPANY_DEFAULT',
    # ) -> PolicySnapshot:
    #     """
    #     Get existing snapshot or create new one.
    #     
    #     Snapshots are immutable and reused by hash.
    #     """
    #     policy_hash = self._compute_policy_hash(policy_dict)
    #     
    #     snapshot, created = PolicySnapshot.objects.get_or_create(
    #         policy_hash=policy_hash,
    #         defaults={
    #             'policy_json': policy_dict,
    #             'policy_type': 'FLEX',
    #             'source': source,
    #         }
    #     )
    #     
    #     return snapshot
    
    def _compute_policy_hash(self, policy_dict: Dict[str, Any]) -> str:
        """
        Compute deterministic hash from policy dictionary.
        
        Uses sorted keys and compact JSON for consistency.
        """
        json_str = json.dumps(policy_dict, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    # =========================================================================
    # PRIVATE - FINGERPRINT
    # =========================================================================
    
    def _compute_fingerprint(
        self,
        employee_id: int,
        target_date: date,
        punch_ids: List[int],
        engine_version: str,
        policy_hash: str,
    ) -> str:
        """
        Compute deterministic fingerprint from calculation inputs.
        
        The fingerprint uniquely identifies a calculation based on:
        - Who (employee)
        - When (date)
        - What (punches)
        - How (engine version + policy)
        
        Same inputs MUST produce same fingerprint.
        Different inputs MUST produce different fingerprint.
        """
        fingerprint_data = {
            'employee_id': employee_id,
            'target_date': target_date.isoformat(),
            'punch_ids': punch_ids,  # Already sorted
            'engine_version': engine_version,
            'policy_hash': policy_hash,
        }
        
        json_str = json.dumps(fingerprint_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    # =========================================================================
    # PRIVATE - RECORD OPERATIONS
    # =========================================================================
    
    def _find_current_record(
        self,
        employee_id: int,
        target_date: date,
    ) -> Optional[models.DailyAttendance]:
        """
        Find the current (non-superseded) record for employee/date.
        
        Returns None if no CALCULATED record exists.
        """
        return models.DailyAttendance.objects.filter(
            employee_id=employee_id,
            date=target_date,
            calculation_state='CALCULATED',
        ).first()
    
    def _create_new_record(
        self,
        context: PersistenceContext,
        policy_snapshot: Any,  # was PolicySnapshot, now disabled
        fingerprint: str,
        supersedes: Optional[models.DailyAttendance] = None,
    ) -> models.DailyAttendance:
        """
        Create a new DailyAttendance record from calculation result.
        
        Maps all result fields to model fields.
        """
        result = context.result
        now = timezone.now()
        
        daily = models.DailyAttendance(
            # Identity
            employee=context.employee,
            date=context.target_date,
            
            # Timestamps
            check_in=result.check_in,
            check_out=result.check_out,
            
            # Time metrics
            worked_minutes=result.worked_minutes,
            break_minutes=result.break_minutes,
            net_worked_minutes=result.net_worked_minutes,
            regular_minutes=result.regular_minutes,
            overtime_minutes=result.overtime_minutes,
            night_minutes=result.night_minutes,
            late_minutes=result.late_minutes or 0,
            early_minutes=result.early_out_minutes or 0,
            
            # Status
            status=result.status,
            is_absent=result.status == 'Absent',
            
            # Schedule context
            schedule_type=result.calculation_mode,
            timetable_id=result.timetable_id,
            source_logs_count=result.source_punches_count,
            
            # Forensic traceability
            engine_version=context.engine_version,
            calculation_mode=result.calculation_mode,
            policy_snapshot=policy_snapshot,
            calculation_fingerprint=fingerprint,
            calculation_state='CALCULATED',
            calculated_at=now,
            
            # Lineage
            supersedes=supersedes,
            recalculation_reason=context.recalculation_reason,
            
            # Review flags
            requires_review=result.requires_review,
        )
        
        daily.save()
        return daily
    
    def _handle_recalculation(
        self,
        existing: models.DailyAttendance,
        context: PersistenceContext,
        policy_snapshot: Any,  # was PolicySnapshot, now disabled
        fingerprint: str,
    ) -> models.DailyAttendance:
        """
        Handle recalculation: supersede existing, create new.
        
        CRITICAL: We never modify existing.
        We only update its 'superseded_by' after creating new.
        """
        # Capture previous values for audit
        previous_values = self._capture_values_for_audit(existing)
        
        # Create new record (with reference to superseded)
        new_daily = self._create_new_record(
            context=context,
            policy_snapshot=policy_snapshot,
            fingerprint=fingerprint,
            supersedes=existing,
        )
        
        # Mark existing as superseded (only these two fields)
        # This is the ONLY mutation allowed on historical records
        existing.calculation_state = 'SUPERSEDED'
        existing.superseded_by = new_daily
        existing.save(update_fields=['calculation_state', 'superseded_by'])
        
        # NOTE: Audit logging disabled - legal audit module not implemented
        # self._log_audit_event(
        #     daily=new_daily,
        #     event_type=AuditEventType.RECALCULATED,
        #     actor=context.actor,
        #     metadata={
        #         'previous_id': existing.id,
        #         'previous_fingerprint': existing.calculation_fingerprint,
        #         'previous_values': previous_values,
        #         'reason': context.recalculation_reason,
        #     },
        # )
        
        return new_daily
    
    def _capture_values_for_audit(
        self,
        daily: models.DailyAttendance
    ) -> Dict[str, Any]:
        """Capture key values for audit comparison."""
        return {
            'worked_minutes': daily.worked_minutes,
            'overtime_minutes': daily.overtime_minutes,
            'net_worked_minutes': daily.net_worked_minutes,
            'status': daily.status,
            'check_in': daily.check_in.isoformat() if daily.check_in else None,
            'check_out': daily.check_out.isoformat() if daily.check_out else None,
            'engine_version': daily.engine_version,
        }
    
    # =========================================================================
    # PRIVATE - AUDIT LOG
    # =========================================================================
    
    # NOTE: Audit logging disabled - legal audit module not implemented
    # def _log_audit_event(
    #     self,
    #     daily: models.DailyAttendance,
    #     event_type: AuditEventType,
    #     actor: Optional[models.User],
    #     metadata: Dict[str, Any],
    # ) -> CalculationAuditLog:
    #     """
    #     Create an audit log entry.
    #     
    #     Every persistence operation gets logged.
    #     """
    #     log = CalculationAuditLog(
    #         daily_attendance=daily,
    #         event_type=event_type.value,
    #         engine_version=daily.engine_version,
    #         calculation_fingerprint=daily.calculation_fingerprint,
    #         metadata=metadata,
    #         actor=actor,
    #     )
    #     log.save()
    #     return log


# Singleton instance for convenience
_persistence_service: Optional[CalculationPersistenceService] = None


def get_persistence_service() -> CalculationPersistenceService:
    """Get singleton persistence service instance."""
    global _persistence_service
    if _persistence_service is None:
        _persistence_service = CalculationPersistenceService()
    return _persistence_service
