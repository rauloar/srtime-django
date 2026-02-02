"""
Forensic API Serializers
Data serialization for attendance and shadow review endpoints.

DESIGN:
- Input serializers validate request data
- Output serializers format response data
- No business logic in serializers
- All domain validation delegated to services
"""
from rest_framework import serializers
from datetime import date


# =============================================================================
# ATTENDANCE SERIALIZERS
# =============================================================================

class CalculateAttendanceInputSerializer(serializers.Serializer):
    """Input for attendance calculation request."""
    
    employee_id = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text='ID del empleado'
    )
    date = serializers.DateField(
        required=True,
        help_text='Fecha a calcular (YYYY-MM-DD)'
    )
    force = serializers.BooleanField(
        required=False,
        default=False,
        help_text='Forzar recálculo ignorando protecciones'
    )
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text='Motivo del recálculo (requerido si force=true)'
    )
    
    def validate(self, attrs):
        """Validate that reason is provided when forcing."""
        if attrs.get('force') and not attrs.get('reason'):
            raise serializers.ValidationError({
                'reason': 'Reason is required when force=true'
            })
        return attrs
    
    def validate_date(self, value):
        """Validate date is not in the future."""
        if value > date.today():
            raise serializers.ValidationError(
                'Cannot calculate attendance for future dates'
            )
        return value


class CalculateAttendanceOutputSerializer(serializers.Serializer):
    """Output for attendance calculation response."""
    
    status = serializers.CharField(
        help_text='Result status: CREATED, RECALCULATED, NO_CHANGE'
    )
    requires_review = serializers.BooleanField(
        help_text='Whether the day requires human review'
    )
    engine_version = serializers.CharField(
        help_text='Engine version used for calculation'
    )
    regular_minutes = serializers.IntegerField(
        help_text='Regular worked minutes'
    )
    overtime_minutes = serializers.IntegerField(
        help_text='Overtime minutes'
    )
    night_minutes = serializers.IntegerField(
        help_text='Night shift minutes'
    )
    fingerprint = serializers.CharField(
        required=False,
        help_text='Calculation fingerprint for verification'
    )


class AttendanceDetailSerializer(serializers.Serializer):
    """Output for attendance detail view."""
    
    employee_id = serializers.IntegerField()
    date = serializers.DateField()
    status = serializers.CharField()
    
    # Time breakdown
    worked_minutes = serializers.IntegerField()
    regular_minutes = serializers.IntegerField()
    overtime_minutes = serializers.IntegerField()
    night_minutes = serializers.IntegerField()
    
    # Forensic data
    engine_version = serializers.CharField()
    fingerprint = serializers.CharField()
    policy_snapshot_hash = serializers.CharField(required=False)
    
    # Lineage
    supersedes_id = serializers.IntegerField(required=False, allow_null=True)
    calculation_state = serializers.CharField()
    
    # Timestamps
    calculated_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()


# =============================================================================
# SHADOW DIFFERENCE SERIALIZERS
# =============================================================================

class ShadowDifferenceListSerializer(serializers.Serializer):
    """Output for shadow difference list."""
    
    id = serializers.IntegerField(source='analysis_id')
    employee_id = serializers.IntegerField()
    employee_name = serializers.CharField(required=False)
    date = serializers.DateField()
    
    # Difference metrics
    difference_minutes = serializers.IntegerField()
    difference_type = serializers.CharField()
    
    # Analysis
    primary_reason = serializers.CharField()
    confidence_level = serializers.CharField()
    requires_human_review = serializers.BooleanField()
    
    # Review status
    review_status = serializers.CharField(required=False)
    reviewer_name = serializers.CharField(required=False)


class ShadowAnalysisDetailSerializer(serializers.Serializer):
    """Output for shadow analysis detail view."""
    
    id = serializers.IntegerField()
    
    # Identity
    employee_id = serializers.IntegerField()
    employee_name = serializers.CharField(required=False)
    date = serializers.DateField()
    
    # V1 Data
    v1_worked_minutes = serializers.IntegerField()
    v1_overtime_minutes = serializers.IntegerField()
    v1_status = serializers.CharField()
    
    # V2 Data
    v2_worked_minutes = serializers.IntegerField()
    v2_net_minutes = serializers.IntegerField()
    v2_overtime_minutes = serializers.IntegerField()
    v2_night_minutes = serializers.IntegerField()
    v2_status = serializers.CharField()
    
    # Comparison
    difference_minutes = serializers.IntegerField()
    difference_type = serializers.CharField()
    
    # Analysis
    primary_reason = serializers.CharField()
    secondary_reason = serializers.CharField(required=False, allow_null=True)
    confidence_level = serializers.CharField()
    explanation = serializers.CharField()
    rule_trace = serializers.JSONField(required=False)
    affected_fields = serializers.JSONField(required=False)
    
    # Review
    review_status = serializers.CharField(required=False)
    reviewer_id = serializers.IntegerField(required=False, allow_null=True)
    reviewer_name = serializers.CharField(required=False)
    decision = serializers.CharField(required=False, allow_null=True)
    decision_notes = serializers.CharField(required=False, allow_null=True)
    decided_at = serializers.DateTimeField(required=False, allow_null=True)


# =============================================================================
# REVIEW WORKFLOW SERIALIZERS
# =============================================================================

class StartReviewOutputSerializer(serializers.Serializer):
    """Output for starting a review."""
    
    analysis_id = serializers.IntegerField()
    status = serializers.CharField()
    reviewer_id = serializers.IntegerField()
    started_at = serializers.DateTimeField()


class SubmitDecisionInputSerializer(serializers.Serializer):
    """Input for submitting a review decision."""
    
    DECISION_CHOICES = [
        ('V2_CORRECT', 'V2 is correct'),
        ('V1_CORRECT', 'V1 is correct'),
        ('POLICY_CHANGE', 'Policy change needed'),
        ('INCONCLUSIVE', 'Inconclusive'),
        ('N/A', 'Not applicable'),
    ]
    
    CONFIDENCE_CHOICES = [
        ('HIGH', 'High confidence'),
        ('MEDIUM', 'Medium confidence'),
        ('LOW', 'Low confidence'),
    ]
    
    decision = serializers.ChoiceField(
        choices=DECISION_CHOICES,
        required=True,
        help_text='The review decision'
    )
    notes = serializers.CharField(
        required=True,
        min_length=10,
        max_length=2000,
        help_text='Justification for the decision (min 10 chars)'
    )
    confidence_override = serializers.ChoiceField(
        choices=CONFIDENCE_CHOICES,
        required=False,
        allow_null=True,
        help_text='Optional override of confidence level'
    )


class SubmitDecisionOutputSerializer(serializers.Serializer):
    """Output for decision submission."""
    
    analysis_id = serializers.IntegerField()
    status = serializers.CharField()
    decision = serializers.CharField()
    decided_at = serializers.DateTimeField()


class CloseReviewOutputSerializer(serializers.Serializer):
    """Output for closing a review."""
    
    analysis_id = serializers.IntegerField()
    status = serializers.CharField()
    closed_by = serializers.IntegerField()
    closed_at = serializers.DateTimeField()


# =============================================================================
# FILTER SERIALIZERS
# =============================================================================

class ShadowDifferenceFilterSerializer(serializers.Serializer):
    """Query parameters for shadow difference list."""
    
    severity = serializers.ChoiceField(
        choices=[('MINOR', 'Minor'), ('MAJOR', 'Major'), ('CRITICAL', 'Critical')],
        required=False,
        help_text='Filter by severity'
    )
    requires_review = serializers.BooleanField(
        required=False,
        help_text='Filter by review required'
    )
    date_from = serializers.DateField(
        required=False,
        help_text='Start date filter'
    )
    date_to = serializers.DateField(
        required=False,
        help_text='End date filter'
    )
    department_id = serializers.IntegerField(
        required=False,
        help_text='Filter by department'
    )
    review_status = serializers.ChoiceField(
        choices=[
            ('PENDING', 'Pending'),
            ('IN_PROGRESS', 'In Progress'),
            ('ACCEPTED', 'Accepted'),
            ('ADJUSTED', 'Adjusted'),
            ('ESCALATED', 'Escalated'),
            ('CLOSED', 'Closed'),
        ],
        required=False,
        help_text='Filter by review status'
    )
