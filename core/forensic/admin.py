"""
Forensic Admin Protection
Django Admin configuration for forensic models.

All forensic models are:
- Read-only in admin
- No delete permission
- Access attempts logged
"""
import logging
from typing import Any, Optional

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.http import HttpRequest

from core.models_forensic import (
    ForensicIntegrityHash,
    ForensicTimestampToken,
    ForensicDocumentSignature,
    ForensicIdempotencyKey,
    ForensicImmutabilityViolation,
    ForensicAuditLog,
)


logger = logging.getLogger('forensic.admin')


# =============================================================================
# BASE READ-ONLY ADMIN
# =============================================================================

class ForensicReadOnlyAdmin(ModelAdmin):
    """
    Base admin class for forensic models.
    
    Provides:
    - Read-only access (no add, change, delete)
    - Audit logging of all access
    - Warning banner about immutability
    """
    
    # No permissions for modification
    def has_add_permission(self, request: HttpRequest) -> bool:
        logger.info(
            f"ADMIN_ACCESS: {request.user.username} attempted add on {self.model._meta.model_name}"
        )
        return False
    
    def has_change_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        logger.info(
            f"ADMIN_ACCESS: {request.user.username} attempted change on "
            f"{self.model._meta.model_name} (id={obj.pk if obj else 'list'})"
        )
        return False
    
    def has_delete_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        logger.warning(
            f"ADMIN_DELETE_ATTEMPT: {request.user.username} attempted delete on "
            f"{self.model._meta.model_name} (id={obj.pk if obj else 'list'})"
        )
        return False
    
    def get_readonly_fields(self, request: HttpRequest, obj: Any = None) -> list:
        """Make all fields readonly."""
        return [field.name for field in self.model._meta.fields]
    
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """Add warning banner to change form."""
        extra_context = extra_context or {}
        extra_context['show_save'] = False
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_add_another'] = False
        extra_context['title'] = f'View {self.model._meta.verbose_name} (Read-Only)'
        return super().changeform_view(request, object_id, form_url, extra_context)


# =============================================================================
# FORENSIC MODEL ADMINS
# =============================================================================

@admin.register(ForensicIntegrityHash)
class ForensicIntegrityHashAdmin(ForensicReadOnlyAdmin):
    """Admin for integrity hash chain nodes."""
    
    list_display = [
        'id', 'entity_type', 'entity_id', 'case_id',
        'chain_hash_short', 'created_at'
    ]
    list_filter = ['entity_type', 'created_at']
    search_fields = ['entity_id', 'case_id', 'chain_hash']
    ordering = ['-created_at']
    
    def chain_hash_short(self, obj):
        return f"{obj.chain_hash[:12]}..."
    chain_hash_short.short_description = 'Chain Hash'


@admin.register(ForensicTimestampToken)
class ForensicTimestampTokenAdmin(ForensicReadOnlyAdmin):
    """Admin for TSA timestamp tokens."""
    
    list_display = [
        'id', 'entity_type', 'entity_id', 'event_type',
        'tsa_provider', 'tsa_timestamp', 'is_certified'
    ]
    list_filter = ['entity_type', 'event_type', 'tsa_provider', 'is_certified']
    search_fields = ['entity_id', 'hash_timestamped']
    ordering = ['-tsa_timestamp']


@admin.register(ForensicDocumentSignature)
class ForensicDocumentSignatureAdmin(ForensicReadOnlyAdmin):
    """Admin for signed document records."""
    
    list_display = [
        'id', 'case_id', 'document_type', 'certificate_serial',
        'signature_timestamp', 'export_count'
    ]
    list_filter = ['document_type', 'signature_timestamp']
    search_fields = ['case_id', 'certificate_serial', 'signed_document_hash']
    ordering = ['-signature_timestamp']


@admin.register(ForensicIdempotencyKey)
class ForensicIdempotencyKeyAdmin(ForensicReadOnlyAdmin):
    """Admin for idempotency keys."""
    
    list_display = [
        'id', 'idempotency_key_short', 'endpoint', 'response_status',
        'created_at', 'expires_at', 'is_expired_display'
    ]
    list_filter = ['response_status', 'created_at']
    search_fields = ['idempotency_key', 'endpoint']
    ordering = ['-created_at']
    
    def idempotency_key_short(self, obj):
        return f"{obj.idempotency_key[:12]}..."
    idempotency_key_short.short_description = 'Idempotency Key'
    
    def is_expired_display(self, obj):
        return obj.is_expired
    is_expired_display.boolean = True
    is_expired_display.short_description = 'Expired'


@admin.register(ForensicImmutabilityViolation)
class ForensicImmutabilityViolationAdmin(ForensicReadOnlyAdmin):
    """Admin for immutability violation logs."""
    
    list_display = [
        'id', 'table_name', 'record_id', 'attempted_operation',
        'attempted_by_short', 'attempted_at', 'blocked'
    ]
    list_filter = ['table_name', 'attempted_operation', 'blocked', 'attempted_at']
    search_fields = ['table_name', 'record_id', 'attempted_by']
    ordering = ['-attempted_at']
    
    def attempted_by_short(self, obj):
        if len(obj.attempted_by) > 50:
            return f"{obj.attempted_by[:50]}..."
        return obj.attempted_by
    attempted_by_short.short_description = 'Attempted By'


@admin.register(ForensicAuditLog)
class ForensicAuditLogAdmin(ForensicReadOnlyAdmin):
    """Admin for audit log entries."""
    
    list_display = [
        'id', 'sequence_number', 'event_type', 'entity_type',
        'entity_id', 'actor_id', 'timestamp_server'
    ]
    list_filter = ['event_type', 'entity_type', 'timestamp_server']
    search_fields = ['sequence_number', 'entity_id', 'actor_id', 'chain_hash']
    ordering = ['-sequence_number']
    
    def get_queryset(self, request):
        """Log list view access."""
        logger.info(
            f"ADMIN_LIST_ACCESS: {request.user.username} accessed ForensicAuditLog list"
        )
        return super().get_queryset(request)
