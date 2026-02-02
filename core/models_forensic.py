"""
Forensic Integrity Layer - Django Models
Data layer for cryptographic integrity, timestamps, and audit chain.

All models in this module are designed to be:
- Immutable after creation
- Forensically verifiable
- Chain-linked for tamper detection
"""
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


# =============================================================================
# ENTITY TYPE CHOICES
# =============================================================================

class ForensicEntityType(models.TextChoices):
    """Types of entities that participate in the integrity chain."""
    SHADOW_CALC = 'SHADOW_CALC', 'Shadow Calculation'
    ANALYSIS = 'ANALYSIS', 'Difference Analysis'
    DECISION = 'DECISION', 'Review Decision'
    CLOSURE = 'CLOSURE', 'Case Closure'
    EXPORT = 'EXPORT', 'Document Export'


class ForensicEventType(models.TextChoices):
    """Event types for timestamping."""
    CREATED = 'CREATED', 'Created'
    DECIDED = 'DECIDED', 'Decision Made'
    CLOSED = 'CLOSED', 'Case Closed'
    EXPORTED = 'EXPORTED', 'Document Exported'


class ForensicDocumentType(models.TextChoices):
    """Types of signed documents."""
    CASE_EXPORT = 'CASE_EXPORT', 'Case Export PDF'
    AUDIT_REPORT = 'AUDIT_REPORT', 'Audit Report'


class AttemptedOperation(models.TextChoices):
    """Types of blocked operations."""
    UPDATE = 'UPDATE', 'Update Attempt'
    DELETE = 'DELETE', 'Delete Attempt'


class AuditEventType(models.TextChoices):
    """Audit log event types."""
    SHADOW_CREATED = 'SHADOW_CREATED', 'Shadow Calculation Created'
    ANALYSIS_GENERATED = 'ANALYSIS_GENERATED', 'Analysis Generated'
    REVIEW_STARTED = 'REVIEW_STARTED', 'Review Started'
    DECISION_SUBMITTED = 'DECISION_SUBMITTED', 'Decision Submitted'
    REVIEW_CLOSED = 'REVIEW_CLOSED', 'Case Closed'
    CASE_EXPORTED = 'CASE_EXPORTED', 'Case Exported'
    ACCESS_DENIED = 'ACCESS_DENIED', 'Access Denied'
    INTEGRITY_VERIFIED = 'INTEGRITY_VERIFIED', 'Integrity Verified'
    INTEGRITY_VIOLATION = 'INTEGRITY_VIOLATION', 'Integrity Violation Detected'


# =============================================================================
# MODEL 1: FORENSIC INTEGRITY HASH
# =============================================================================

class ForensicIntegrityHash(models.Model):
    """
    Cryptographic hash chain node for forensic entities.
    
    Each record represents one node in the integrity chain.
    The chain_hash links to the previous node, creating a
    tamper-evident sequence that can be verified forensically.
    
    IMMUTABLE: This model does not allow updates after creation.
    """
    
    entity_type = models.CharField(
        max_length=20,
        choices=ForensicEntityType.choices,
        db_index=True,
        verbose_name='Entity Type'
    )
    
    entity_id = models.BigIntegerField(
        db_index=True,
        verbose_name='Entity ID'
    )
    
    case_id = models.BigIntegerField(
        db_index=True,
        null=True,
        blank=True,
        verbose_name='Case ID',
        help_text='Allows chain verification per case'
    )
    
    content_hash = models.CharField(
        max_length=64,
        verbose_name='Content Hash',
        help_text='SHA-256 of canonical JSON'
    )
    
    previous_hash = models.CharField(
        max_length=64,
        default='GENESIS',
        verbose_name='Previous Hash',
        help_text='Previous chain hash or GENESIS for first node'
    )
    
    chain_hash = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name='Chain Hash',
        help_text='SHA-256(content_hash + previous_hash)'
    )
    
    canonical_json = models.JSONField(
        verbose_name='Canonical JSON',
        help_text='Exact content that was hashed for reproducibility'
    )
    
    hash_algorithm = models.CharField(
        max_length=20,
        default='SHA256',
        verbose_name='Hash Algorithm'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Created At'
    )
    
    class Meta:
        db_table = 'forensic_integrity_hash'
        verbose_name = 'Forensic Integrity Hash'
        verbose_name_plural = 'Forensic Integrity Hashes'
        ordering = ['created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['entity_type', 'entity_id'],
                name='uq_forensic_integrity_entity'
            ),
        ]
        indexes = [
            models.Index(fields=['case_id', 'created_at']),
            models.Index(fields=['entity_type', 'entity_id']),
        ]
    
    def __str__(self):
        return f"{self.entity_type}:{self.entity_id} [{self.chain_hash[:8]}...]"
    
    def save(self, *args, **kwargs):
        """Prevent updates to existing records."""
        if self.pk is not None:
            raise ValidationError(
                "ForensicIntegrityHash records are immutable and cannot be updated."
            )
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Prevent deletion of records."""
        raise ValidationError(
            "ForensicIntegrityHash records are immutable and cannot be deleted."
        )


# =============================================================================
# MODEL 2: FORENSIC TIMESTAMP TOKEN
# =============================================================================

class ForensicTimestampToken(models.Model):
    """
    Stores RFC 3161 Time Stamping Authority (TSA) responses.
    
    Each critical forensic event is timestamped by an external TSA
    to provide legally defensible proof of when the event occurred.
    
    IMMUTABLE: This model does not allow updates after creation.
    """
    
    entity_type = models.CharField(
        max_length=20,
        choices=ForensicEntityType.choices,
        db_index=True,
        verbose_name='Entity Type'
    )
    
    entity_id = models.BigIntegerField(
        db_index=True,
        verbose_name='Entity ID'
    )
    
    event_type = models.CharField(
        max_length=20,
        choices=ForensicEventType.choices,
        verbose_name='Event Type'
    )
    
    hash_timestamped = models.CharField(
        max_length=64,
        verbose_name='Hash Timestamped',
        help_text='SHA-256 hash that was sent to TSA'
    )
    
    tsa_token = models.BinaryField(
        verbose_name='TSA Token',
        help_text='RFC 3161 timestamp response (DER encoded)'
    )
    
    tsa_provider = models.CharField(
        max_length=100,
        verbose_name='TSA Provider',
        help_text='Name of the TSA service (e.g., DigiCert, FreeTSA)'
    )
    
    tsa_timestamp = models.DateTimeField(
        verbose_name='TSA Timestamp',
        help_text='Certified timestamp from TSA'
    )
    
    server_timestamp = models.DateTimeField(
        verbose_name='Server Timestamp',
        help_text='Local server time for reference'
    )
    
    clock_drift_ms = models.IntegerField(
        default=0,
        verbose_name='Clock Drift (ms)',
        help_text='Difference between server and TSA time in milliseconds'
    )
    
    verification_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name='Verification URL',
        help_text='URL to verify the timestamp token'
    )
    
    is_certified = models.BooleanField(
        default=True,
        verbose_name='Is Certified',
        help_text='False if TSA was unavailable and local time was used'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    
    class Meta:
        db_table = 'forensic_timestamp_token'
        verbose_name = 'Forensic Timestamp Token'
        verbose_name_plural = 'Forensic Timestamp Tokens'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['tsa_timestamp']),
        ]
    
    def __str__(self):
        return f"TSA:{self.entity_type}:{self.entity_id} @ {self.tsa_timestamp}"
    
    def save(self, *args, **kwargs):
        """Prevent updates to existing records."""
        if self.pk is not None:
            raise ValidationError(
                "ForensicTimestampToken records are immutable and cannot be updated."
            )
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Prevent deletion of records."""
        raise ValidationError(
            "ForensicTimestampToken records are immutable and cannot be deleted."
        )


# =============================================================================
# MODEL 3: FORENSIC DOCUMENT SIGNATURE
# =============================================================================

class ForensicDocumentSignature(models.Model):
    """
    Tracks digitally signed, immutable PDF documents.
    
    Each exported case produces ONE signed PDF that is stored permanently.
    Subsequent exports return the same file to ensure consistency.
    
    IMMUTABLE: Core fields cannot be updated after creation.
    Only export_count can be incremented.
    """
    
    case_id = models.BigIntegerField(
        db_index=True,
        verbose_name='Case ID'
    )
    
    document_type = models.CharField(
        max_length=20,
        choices=ForensicDocumentType.choices,
        verbose_name='Document Type'
    )
    
    document_hash = models.CharField(
        max_length=64,
        verbose_name='Document Hash',
        help_text='SHA-256 of PDF content before signing'
    )
    
    signed_document_hash = models.CharField(
        max_length=64,
        unique=True,
        verbose_name='Signed Document Hash',
        help_text='SHA-256 of signed PDF'
    )
    
    signature_timestamp = models.DateTimeField(
        verbose_name='Signature Timestamp'
    )
    
    certificate_serial = models.CharField(
        max_length=100,
        verbose_name='Certificate Serial',
        help_text='Serial number of signing certificate'
    )
    
    certificate_issuer = models.CharField(
        max_length=500,
        verbose_name='Certificate Issuer',
        help_text='CA that issued the signing certificate'
    )
    
    certificate_expiry = models.DateField(
        verbose_name='Certificate Expiry',
        help_text='Expiration date of signing certificate'
    )
    
    signature_algorithm = models.CharField(
        max_length=50,
        default='SHA256withRSA',
        verbose_name='Signature Algorithm'
    )
    
    signed_pdf_path = models.CharField(
        max_length=500,
        verbose_name='Signed PDF Path',
        help_text='Filesystem path to signed PDF'
    )
    
    first_export_at = models.DateTimeField(
        verbose_name='First Export At'
    )
    
    export_count = models.PositiveIntegerField(
        default=1,
        verbose_name='Export Count',
        help_text='Number of times this document has been downloaded'
    )
    
    integrity_hash_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='Integrity Hash ID',
        help_text='FK to ForensicIntegrityHash for chain linkage'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    
    class Meta:
        db_table = 'forensic_document_signature'
        verbose_name = 'Forensic Document Signature'
        verbose_name_plural = 'Forensic Document Signatures'
        ordering = ['created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['case_id', 'document_type'],
                name='uq_forensic_document_case_type'
            ),
        ]
        indexes = [
            models.Index(fields=['case_id']),
            models.Index(fields=['signed_document_hash']),
        ]
    
    def __str__(self):
        return f"{self.document_type}:case_{self.case_id} [{self.signed_document_hash[:8]}...]"
    
    def increment_export_count(self):
        """Safe method to increment export count without full update."""
        ForensicDocumentSignature.objects.filter(pk=self.pk).update(
            export_count=models.F('export_count') + 1
        )
        self.refresh_from_db()


# =============================================================================
# MODEL 4: FORENSIC IDEMPOTENCY KEY
# =============================================================================

class ForensicIdempotencyKey(models.Model):
    """
    Prevents replay of legal operations.
    
    Each write operation requires a unique idempotency key.
    If the same key is used again, the cached response is returned
    without re-executing the operation.
    """
    
    idempotency_key = models.CharField(
        max_length=64,
        db_index=True,
        verbose_name='Idempotency Key',
        help_text='Client-provided UUID'
    )
    
    endpoint = models.CharField(
        max_length=200,
        verbose_name='Endpoint',
        help_text='API path of the operation'
    )
    
    request_hash = models.CharField(
        max_length=64,
        verbose_name='Request Hash',
        help_text='SHA-256 of request body'
    )
    
    response_status = models.IntegerField(
        verbose_name='Response Status',
        help_text='HTTP status code of cached response'
    )
    
    response_body = models.JSONField(
        verbose_name='Response Body',
        help_text='Cached response for replay'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Created At'
    )
    
    expires_at = models.DateTimeField(
        db_index=True,
        verbose_name='Expires At',
        help_text='TTL for idempotency key (typically 24h)'
    )
    
    class Meta:
        db_table = 'forensic_idempotency_key'
        verbose_name = 'Forensic Idempotency Key'
        verbose_name_plural = 'Forensic Idempotency Keys'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['idempotency_key', 'endpoint'],
                name='uq_forensic_idempotency_key_endpoint'
            ),
        ]
        indexes = [
            models.Index(fields=['idempotency_key', 'endpoint']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.idempotency_key[:8]}... @ {self.endpoint}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at


# =============================================================================
# MODEL 5: FORENSIC IMMUTABILITY VIOLATION
# =============================================================================

class ForensicImmutabilityViolation(models.Model):
    """
    Logs blocked tampering attempts.
    
    When a protected record receives an UPDATE or DELETE attempt,
    the attempt is blocked and logged here for forensic investigation.
    
    This model is append-only.
    """
    
    table_name = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name='Table Name'
    )
    
    record_id = models.BigIntegerField(
        verbose_name='Record ID'
    )
    
    attempted_operation = models.CharField(
        max_length=10,
        choices=AttemptedOperation.choices,
        verbose_name='Attempted Operation'
    )
    
    attempted_by = models.CharField(
        max_length=100,
        verbose_name='Attempted By',
        help_text='Database user that attempted the operation'
    )
    
    attempted_at = models.DateTimeField(
        db_index=True,
        verbose_name='Attempted At'
    )
    
    old_values = models.JSONField(
        verbose_name='Old Values',
        help_text='State of record before attempted change'
    )
    
    blocked = models.BooleanField(
        default=True,
        verbose_name='Blocked',
        help_text='Whether the operation was successfully blocked'
    )
    
    class Meta:
        db_table = 'forensic_immutability_violation'
        verbose_name = 'Forensic Immutability Violation'
        verbose_name_plural = 'Forensic Immutability Violations'
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['table_name', 'attempted_at']),
            models.Index(fields=['record_id']),
        ]
    
    def __str__(self):
        return f"VIOLATION: {self.attempted_operation} on {self.table_name}:{self.record_id}"
    
    def save(self, *args, **kwargs):
        """Prevent updates to existing records."""
        if self.pk is not None:
            raise ValidationError(
                "ForensicImmutabilityViolation records are immutable."
            )
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Prevent deletion of records."""
        raise ValidationError(
            "ForensicImmutabilityViolation records cannot be deleted."
        )


# =============================================================================
# MODEL 6: FORENSIC AUDIT LOG
# =============================================================================

class ForensicAuditLog(models.Model):
    """
    Tamper-evident audit chain.
    
    Every audit event includes a hash chain that links to the previous event.
    This creates a blockchain-lite structure where any insertion, deletion,
    or modification can be detected by verifying the chain.
    
    IMMUTABLE: This model is strictly append-only.
    """
    
    sequence_number = models.BigIntegerField(
        unique=True,
        db_index=True,
        verbose_name='Sequence Number',
        help_text='Global sequence for chain verification'
    )
    
    event_type = models.CharField(
        max_length=50,
        choices=AuditEventType.choices,
        db_index=True,
        verbose_name='Event Type'
    )
    
    entity_type = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name='Entity Type'
    )
    
    entity_id = models.BigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name='Entity ID'
    )
    
    actor_id = models.BigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name='Actor ID',
        help_text='User who performed the action'
    )
    
    actor_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Actor IP'
    )
    
    actor_user_agent = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Actor User Agent'
    )
    
    event_data = models.JSONField(
        default=dict,
        verbose_name='Event Data',
        help_text='Additional event metadata'
    )
    
    event_hash = models.CharField(
        max_length=64,
        verbose_name='Event Hash',
        help_text='SHA-256 of event content'
    )
    
    previous_hash = models.CharField(
        max_length=64,
        default='GENESIS',
        verbose_name='Previous Hash'
    )
    
    chain_hash = models.CharField(
        max_length=64,
        db_index=True,
        verbose_name='Chain Hash',
        help_text='SHA-256(event_hash + previous_hash)'
    )
    
    timestamp_server = models.DateTimeField(
        db_index=True,
        verbose_name='Server Timestamp'
    )
    
    timestamp_tsa = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='TSA Timestamp',
        help_text='Certified timestamp for critical events'
    )
    
    tsa_token = models.ForeignKey(
        ForensicTimestampToken,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name='TSA Token'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    
    class Meta:
        db_table = 'forensic_audit_log'
        verbose_name = 'Forensic Audit Log'
        verbose_name_plural = 'Forensic Audit Logs'
        ordering = ['sequence_number']
        indexes = [
            models.Index(fields=['sequence_number']),
            models.Index(fields=['event_type', 'timestamp_server']),
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['actor_id', 'timestamp_server']),
            models.Index(fields=['chain_hash']),
        ]
    
    def __str__(self):
        return f"[{self.sequence_number}] {self.event_type} - {self.entity_type}:{self.entity_id}"
    
    def save(self, *args, **kwargs):
        """Prevent updates to existing records."""
        if self.pk is not None:
            raise ValidationError(
                "ForensicAuditLog records are immutable and cannot be updated."
            )
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Prevent deletion of records."""
        raise ValidationError(
            "ForensicAuditLog records are immutable and cannot be deleted."
        )
