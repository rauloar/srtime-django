"""Backward-compatible forensic model aliases used by legacy imports/tests."""

from django.db import models
from django.utils import timezone


class _ForensicBase(models.Model):
    class Meta:
        abstract = True
        app_label = "core"


class ForensicIntegrityHash(_ForensicBase):
    entity_type = models.CharField(max_length=100, default="unknown")
    entity_id = models.CharField(max_length=100, default="0")
    case_id = models.CharField(max_length=100, null=True, blank=True)
    chain_hash = models.TextField(default="")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta(_ForensicBase.Meta):
        db_table = "forensic_integrity_hash"
        managed = False


class ForensicTimestampToken(_ForensicBase):
    entity_type = models.CharField(max_length=100, default="unknown")
    entity_id = models.CharField(max_length=100, default="0")
    event_type = models.CharField(max_length=100, default="unknown")
    tsa_provider = models.CharField(max_length=100, default="unknown")
    tsa_timestamp = models.DateTimeField(default=timezone.now)
    is_certified = models.BooleanField(default=False)

    class Meta(_ForensicBase.Meta):
        db_table = "forensic_timestamp_token"
        managed = False


class ForensicDocumentSignature(_ForensicBase):
    case_id = models.CharField(max_length=100, default="")
    document_type = models.CharField(max_length=100, default="")
    certificate_serial = models.CharField(max_length=200, default="")
    signature_timestamp = models.DateTimeField(default=timezone.now)
    export_count = models.IntegerField(default=0)

    class Meta(_ForensicBase.Meta):
        db_table = "forensic_document_signature"
        managed = False


class ForensicIdempotencyKey(_ForensicBase):
    idempotency_key = models.CharField(max_length=255, default="")
    endpoint = models.CharField(max_length=255, default="")
    response_status = models.IntegerField(default=200)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(default=timezone.now)

    @property
    def is_expired(self):
        return self.expires_at <= timezone.now()

    class Meta(_ForensicBase.Meta):
        db_table = "forensic_idempotency_key"
        managed = False


class ForensicImmutabilityViolation(_ForensicBase):
    table_name = models.CharField(max_length=200)
    record_id = models.IntegerField(default=0)
    attempted_operation = models.CharField(max_length=20)
    attempted_by = models.CharField(max_length=100)
    attempted_at = models.DateTimeField(default=timezone.now)
    old_values = models.JSONField(default=dict)
    blocked = models.BooleanField(default=True)

    class Meta(_ForensicBase.Meta):
        db_table = "forensic_immutability_violation"
        managed = False


class ForensicAuditLog(_ForensicBase):
    sequence_number = models.BigIntegerField(default=0)
    event_type = models.CharField(max_length=100, default="")
    entity_type = models.CharField(max_length=100, default="")
    entity_id = models.CharField(max_length=100, default="")
    actor_id = models.CharField(max_length=100, null=True, blank=True)
    timestamp_server = models.DateTimeField(default=timezone.now)
    chain_hash = models.TextField(default="")

    class Meta(_ForensicBase.Meta):
        db_table = "forensic_audit_log"
        managed = False
