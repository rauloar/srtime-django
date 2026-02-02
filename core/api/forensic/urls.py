"""
Forensic API URL Configuration
Routes for attendance calculation and shadow review endpoints.

All endpoints are prefixed with /api/forensic/ when included in main urlconf.
"""
from django.urls import path

from .views import (
    CalculateAttendanceView,
    AttendanceDetailView,
    ShadowDifferenceListView,
    ShadowAnalysisDetailView,
    StartReviewView,
    SubmitDecisionView,
    CloseReviewView,
)


app_name = 'forensic'

urlpatterns = [
    # === ATTENDANCE ENDPOINTS ===
    path(
        'attendance/calculate/',
        CalculateAttendanceView.as_view(),
        name='calculate-attendance'
    ),
    path(
        'attendance/<int:employee_id>/<str:date>/',
        AttendanceDetailView.as_view(),
        name='attendance-detail'
    ),
    
    # === SHADOW DIFFERENCE ENDPOINTS ===
    path(
        'shadow/differences/',
        ShadowDifferenceListView.as_view(),
        name='shadow-differences'
    ),
    path(
        'shadow/analysis/<int:analysis_id>/',
        ShadowAnalysisDetailView.as_view(),
        name='shadow-analysis-detail'
    ),
    
    # === REVIEW WORKFLOW ENDPOINTS ===
    path(
        'shadow/review/<int:analysis_id>/start/',
        StartReviewView.as_view(),
        name='review-start'
    ),
    path(
        'shadow/review/<int:analysis_id>/decision/',
        SubmitDecisionView.as_view(),
        name='review-decision'
    ),
    path(
        'shadow/review/<int:analysis_id>/close/',
        CloseReviewView.as_view(),
        name='review-close'
    ),
]


# =============================================================================
# MAIN URLCONF INTEGRATION
# =============================================================================
# Add to your main urls.py:
#
# from django.urls import path, include
#
# urlpatterns = [
#     ...
#     path('api/forensic/', include('core.api.forensic.urls')),
# ]
# =============================================================================
