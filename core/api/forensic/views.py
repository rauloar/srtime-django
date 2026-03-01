"""
Forensic API Views
REST endpoints for attendance calculation and shadow review.

DESIGN PRINCIPLES:
1. NO BUSINESS LOGIC - All logic delegated to services
2. CLEAN SEPARATION - Views only handle HTTP concerns
3. PERMISSION ENFORCEMENT - Every endpoint has explicit permissions
4. ERROR HANDLING - All errors converted to clean responses
5. AUDIT TRAIL - Services handle auditing, views don't duplicate

ENDPOINTS:
- POST /calculate/         - Calculate attendance
- GET /{employee}/{date}/  - View attendance
- GET /shadow/differences/ - List shadow differences
- GET /shadow/analysis/{id}/ - View analysis detail
- POST /shadow/review/{id}/start/ - Start review
- POST /shadow/review/{id}/decision/ - Submit decision
- POST /shadow/review/{id}/close/ - Close case
"""
import logging
from datetime import datetime

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from django.shortcuts import get_object_or_404

from .permissions import IsAttendanceAdmin, IsShadowReviewer
from .serializers import (
    CalculateAttendanceInputSerializer,
    CalculateAttendanceOutputSerializer,
    AttendanceDetailSerializer,
    ShadowDifferenceListSerializer,
    ShadowDifferenceFilterSerializer,
    ShadowAnalysisDetailSerializer,
    StartReviewOutputSerializer,
    SubmitDecisionInputSerializer,
    SubmitDecisionOutputSerializer,
    CloseReviewOutputSerializer,
)
from .exceptions import (
    EmployeeNotFoundError,
    AttendanceNotFoundError,
    AnalysisNotFoundError,
    InvalidTransitionError,
    UnauthorizedActionError,
    ProtectedDayError,
)

# Service imports - all business logic is in services
from core.services.attendance_application import (
    get_attendance_service,
    ProtectedDayError as ServiceProtectedDayError,
    ScheduleNotFoundError,
    AttendanceServiceError,
)
from core.services.shadow.review_workflow_service import (
    get_review_workflow_service,
    InvalidShadowTransition,
    UnauthorizedReviewer,
    ReviewNotFound,
    AnalysisNotFound as ServiceAnalysisNotFound,
    DecisionRequired,
)
from core.models_shadow import (
    ShadowCalculation,
    ShadowDifferenceAnalysis,
    ShadowReviewDecision,
    ReviewDecision,
    ConfidenceLevel,
)
from core import models


logger = logging.getLogger(__name__)


# =============================================================================
# ATTENDANCE ENDPOINTS
# =============================================================================

class CalculateAttendanceView(APIView):
    """
    POST /api/forensic/attendance/calculate/
    
    Calculate or recalculate attendance for a specific day.
    Delegates all logic to AttendanceApplicationService.
    
    Permissions: IsAttendanceAdmin
    """
    permission_classes = [IsAttendanceAdmin]
    
    def post(self, request):
        # Validate input
        serializer = CalculateAttendanceInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        user_id = data.get('user_id')
        legacy_employee_id = data.get('employee_id')
        warning_headers = {}
        
        try:
            if user_id:
                employee = models.Employee.objects.get(user_id=user_id)
            elif legacy_employee_id:
                employee = models.Employee.objects.get(id=int(legacy_employee_id))
                warning_headers['X-API-Deprecated'] = 'employee_id will be removed. Use user_id instead.'
            else:
                raise EmployeeNotFoundError("No employee identifier provided")
        except models.Employee.DoesNotExist:
            raise EmployeeNotFoundError(f"Employee {user_id or legacy_employee_id} not found")

        # Get service
        service = get_attendance_service()
        
        try:
            # Delegate to service
            result = service.process_daily_attendance(
                employee_id=employee.id,
                target_date=data['date'],
                actor=request.user,
                force=data.get('force', False),
                recalculation_reason=data.get('reason'),
            )
            
            # Format response
            daily = result.daily_attendance
            output = CalculateAttendanceOutputSerializer({
                'status': result.status.value if hasattr(result.status, 'value') else str(result.status),
                'requires_review': getattr(daily, 'requires_review', False),
                'engine_version': result.engine_version,
                'regular_minutes': getattr(daily, 'regular_minutes', daily.worked_minutes),
                'overtime_minutes': getattr(daily, 'overtime_minutes', 0),
                'night_minutes': getattr(daily, 'night_minutes', 0),
                'fingerprint': getattr(daily, 'calculation_fingerprint', ''),
            })
            
            return Response(output.data, status=status.HTTP_200_OK, headers=warning_headers if warning_headers else None)
            
        except models.Employee.DoesNotExist:
            raise EmployeeNotFoundError(
                f"Employee {data['employee_id']} not found"
            )
        except ServiceProtectedDayError as e:
            raise ProtectedDayError(
                str(e),
                details={'user_id': user_id or legacy_employee_id, 'date': str(data['date'])}
            )
        except ScheduleNotFoundError as e:
            raise EmployeeNotFoundError(
                f"No schedule found for employee {user_id or legacy_employee_id} on {data['date']}"
            )
        except AttendanceServiceError as e:
            logger.error(f"Attendance calculation failed: {e}")
            raise


class AttendanceDetailView(APIView):
    """
    GET /api/forensic/attendance/{employee_id}/{date}/
    
    View official attendance record for a specific day.
    Read-only endpoint.
    
    Permissions: IsAttendanceAdmin
    """
    permission_classes = [IsAttendanceAdmin]
    
    def get(self, request, user_id: str, date: str):
        # Get employee
        warning_headers = {}
        try:
            employee = models.Employee.objects.get(user_id=user_id)
        except models.Employee.DoesNotExist:
            if str(user_id).isdigit():
                employee = get_object_or_404(models.Employee, pk=int(user_id))
                warning_headers['X-API-Deprecated'] = 'employee_id will be removed. Use user_id instead.'
            else:
                raise EmployeeNotFoundError(f"Employee {user_id} not found")
        
        # Parse date
        try:
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'INVALID_DATE', 'message': 'Date must be YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get most recent attendance record
        daily = models.DailyAttendance.objects.filter(
            employee=employee,
            date=target_date,
        ).order_by('-created_at').first()
        
        if not daily:
            raise AttendanceNotFoundError(
                f"No attendance record for employee {user_id} on {date}"
            )
        
        # Build response
        policy_hash = ''
        if hasattr(daily, 'policy_snapshot') and daily.policy_snapshot:
            policy_hash = daily.policy_snapshot.policy_hash[:16] if hasattr(daily.policy_snapshot, 'policy_hash') else ''
        
        output = AttendanceDetailSerializer({
            'user_id': employee.user_id,
            'employee_id': daily.employee_id,
            'date': daily.date,
            'status': daily.status,
            'worked_minutes': daily.worked_minutes,
            'regular_minutes': getattr(daily, 'regular_minutes', daily.worked_minutes),
            'overtime_minutes': getattr(daily, 'overtime_minutes', 0),
            'night_minutes': getattr(daily, 'night_minutes', 0),
            'engine_version': getattr(daily, 'engine_version', '1.0.0'),
            'fingerprint': getattr(daily, 'calculation_fingerprint', ''),
            'policy_snapshot_hash': policy_hash,
            'supersedes_id': getattr(daily, 'supersedes_id', None),
            'calculation_state': getattr(daily, 'calculation_state', 'ACTIVE'),
            'calculated_at': getattr(daily, 'updated_at', daily.created_at),
            'created_at': daily.created_at,
        })
        
        return Response(output.data, headers=warning_headers if warning_headers else None)


# =============================================================================
# SHADOW DIFFERENCE ENDPOINTS
# =============================================================================

class ShadowDifferenceListView(APIView):
    """
    GET /api/forensic/shadow/differences/
    
    List shadow calculation differences with filters.
    
    Permissions: IsShadowReviewer
    """
    permission_classes = [IsShadowReviewer]
    
    def get(self, request):
        # Parse filters
        filter_serializer = ShadowDifferenceFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data
        
        # Build queryset
        queryset = ShadowDifferenceAnalysis.objects.select_related(
            'shadow_calculation',
            'shadow_calculation__employee',
        ).prefetch_related(
            'review_decision',
        ).order_by('-created_at')
        
        # Apply filters
        if filters.get('severity'):
            queryset = queryset.filter(
                shadow_calculation__difference_type=filters['severity']
            )
        
        if filters.get('requires_review') is not None:
            queryset = queryset.filter(requires_human_review=filters['requires_review'])
        
        if filters.get('date_from'):
            queryset = queryset.filter(shadow_calculation__date__gte=filters['date_from'])
        
        if filters.get('date_to'):
            queryset = queryset.filter(shadow_calculation__date__lte=filters['date_to'])
        
        if filters.get('review_status'):
            queryset = queryset.filter(review_decision__status=filters['review_status'])
        
        # Pagination (simple limit)
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        queryset = queryset[offset:offset + limit]
        
        # Serialize
        results = []
        for analysis in queryset:
            shadow = analysis.shadow_calculation
            review = getattr(analysis, 'review_decision', None)
            
            results.append({
                'analysis_id': analysis.id,
                'user_id': shadow.employee.user_id if shadow.employee else None,
                'employee_id': shadow.employee_id,
                'employee_name': str(shadow.employee) if shadow.employee else '',
                'date': shadow.date,
                'difference_minutes': shadow.difference_minutes,
                'difference_type': shadow.difference_type,
                'primary_reason': analysis.primary_reason,
                'confidence_level': analysis.confidence_level,
                'requires_human_review': analysis.requires_human_review,
                'review_status': review.status if review else 'NOT_STARTED',
                'reviewer_name': str(review.reviewer) if review and review.reviewer else None,
            })
        
        serializer = ShadowDifferenceListSerializer(results, many=True)
        return Response({
            'count': len(results),
            'results': serializer.data,
        })


class ShadowAnalysisDetailView(APIView):
    """
    GET /api/forensic/shadow/analysis/{id}/
    
    View detailed shadow analysis with V1/V2 comparison.
    
    Permissions: IsShadowReviewer
    """
    permission_classes = [IsShadowReviewer]
    
    def get(self, request, analysis_id: int):
        # Get analysis with related data
        analysis = ShadowDifferenceAnalysis.objects.select_related(
            'shadow_calculation',
            'shadow_calculation__employee',
        ).filter(id=analysis_id).first()
        
        if not analysis:
            raise AnalysisNotFoundError(f"Analysis {analysis_id} not found")
        
        shadow = analysis.shadow_calculation
        
        # Get review if exists
        try:
            review = analysis.review_decision
        except ShadowReviewDecision.DoesNotExist:
            review = None
        
        # Build response
        data = {
            'id': analysis.id,
            'user_id': shadow.employee.user_id if shadow.employee else None,
            'employee_id': shadow.employee_id,
            'employee_name': str(shadow.employee) if shadow.employee else '',
            'date': shadow.date,
            
            # V1 data
            'v1_worked_minutes': shadow.v1_worked_minutes,
            'v1_overtime_minutes': shadow.v1_overtime_minutes,
            'v1_status': shadow.v1_status,
            
            # V2 data
            'v2_worked_minutes': shadow.v2_worked_minutes,
            'v2_net_minutes': shadow.v2_net_minutes,
            'v2_overtime_minutes': shadow.v2_overtime_minutes,
            'v2_night_minutes': shadow.v2_night_minutes,
            'v2_status': shadow.v2_status,
            
            # Comparison
            'difference_minutes': shadow.difference_minutes,
            'difference_type': shadow.difference_type,
            
            # Analysis
            'primary_reason': analysis.primary_reason,
            'secondary_reason': analysis.secondary_reason,
            'confidence_level': analysis.confidence_level,
            'explanation': analysis.explanation,
            'rule_trace': analysis.rule_trace,
            'affected_fields': analysis.affected_fields,
            
            # Review
            'review_status': review.status if review else 'NOT_STARTED',
            'reviewer_id': review.reviewer_id if review else None,
            'reviewer_name': str(review.reviewer) if review and review.reviewer else None,
            'decision': review.decision if review else None,
            'decision_notes': review.decision_notes if review else None,
            'decided_at': review.decided_at if review else None,
        }
        
        serializer = ShadowAnalysisDetailSerializer(data)
        return Response(serializer.data)


# =============================================================================
# REVIEW WORKFLOW ENDPOINTS
# =============================================================================

class StartReviewView(APIView):
    """
    POST /api/forensic/shadow/review/{analysis_id}/start/
    
    Start human review of a shadow analysis.
    Transitions: PENDING → IN_PROGRESS
    
    Permissions: IsShadowReviewer
    """
    permission_classes = [IsShadowReviewer]
    
    def post(self, request, analysis_id: int):
        service = get_review_workflow_service()
        
        try:
            review = service.start_review(
                analysis_id=analysis_id,
                reviewer=request.user,
            )
            
            output = StartReviewOutputSerializer({
                'analysis_id': analysis_id,
                'status': review.status,
                'reviewer_id': review.reviewer_id,
                'started_at': review.started_at,
            })
            
            return Response(output.data, status=status.HTTP_200_OK)
            
        except ServiceAnalysisNotFound:
            raise AnalysisNotFoundError(f"Analysis {analysis_id} not found")
        except InvalidShadowTransition as e:
            raise InvalidTransitionError(
                f"Cannot start review: {e}",
                details={'from': e.from_status, 'to': e.to_status}
            )


class SubmitDecisionView(APIView):
    """
    POST /api/forensic/shadow/review/{analysis_id}/decision/
    
    Submit a decision on a shadow analysis.
    Transitions: IN_PROGRESS → ACCEPTED/ADJUSTED/ESCALATED
    
    Permissions: IsShadowReviewer (must be assigned reviewer)
    """
    permission_classes = [IsShadowReviewer]
    
    def post(self, request, analysis_id: int):
        # Validate input
        serializer = SubmitDecisionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        service = get_review_workflow_service()
        
        try:
            # Map string decision to enum
            decision_map = {
                'V2_CORRECT': ReviewDecision.V2_CORRECT,
                'V1_CORRECT': ReviewDecision.V1_CORRECT,
                'POLICY_CHANGE': ReviewDecision.POLICY_CHANGE_NEEDED,
                'INCONCLUSIVE': ReviewDecision.INCONCLUSIVE,
                'N/A': ReviewDecision.NOT_APPLICABLE,
            }
            decision = decision_map.get(data['decision'], data['decision'])
            
            # Map confidence override if provided
            confidence_override = None
            if data.get('confidence_override'):
                confidence_map = {
                    'HIGH': ConfidenceLevel.HIGH,
                    'MEDIUM': ConfidenceLevel.MEDIUM,
                    'LOW': ConfidenceLevel.LOW,
                }
                confidence_override = confidence_map.get(data['confidence_override'])
            
            review = service.submit_decision(
                analysis_id=analysis_id,
                reviewer=request.user,
                decision=decision,
                notes=data['notes'],
                confidence_override=confidence_override,
            )
            
            output = SubmitDecisionOutputSerializer({
                'analysis_id': analysis_id,
                'status': review.status,
                'decision': review.decision,
                'decided_at': review.decided_at,
            })
            
            return Response(output.data, status=status.HTTP_200_OK)
            
        except ReviewNotFound:
            raise AnalysisNotFoundError(
                f"No review found for analysis {analysis_id}. Start review first."
            )
        except UnauthorizedReviewer:
            raise UnauthorizedActionError(
                "Only the assigned reviewer can submit a decision"
            )
        except InvalidShadowTransition as e:
            raise InvalidTransitionError(
                f"Cannot submit decision: {e}",
                details={'from': e.from_status, 'to': e.to_status}
            )
        except DecisionRequired:
            return Response(
                {'error': 'NOTES_REQUIRED', 'message': 'Decision notes are required'},
                status=status.HTTP_400_BAD_REQUEST
            )


class CloseReviewView(APIView):
    """
    POST /api/forensic/shadow/review/{analysis_id}/close/
    
    Close a decided review case.
    Transitions: ACCEPTED/ADJUSTED/ESCALATED → CLOSED
    
    Permissions: IsShadowReviewer
    """
    permission_classes = [IsShadowReviewer]
    
    def post(self, request, analysis_id: int):
        service = get_review_workflow_service()
        
        try:
            review = service.close_case(
                analysis_id=analysis_id,
                reviewer=request.user,
            )
            
            output = CloseReviewOutputSerializer({
                'analysis_id': analysis_id,
                'status': review.status,
                'closed_by': review.closed_by_id,
                'closed_at': review.closed_at,
            })
            
            return Response(output.data, status=status.HTTP_200_OK)
            
        except ReviewNotFound:
            raise AnalysisNotFoundError(
                f"No review found for analysis {analysis_id}"
            )
        except InvalidShadowTransition as e:
            raise InvalidTransitionError(
                f"Cannot close review: {e}",
                details={'from': e.from_status, 'to': e.to_status}
            )
