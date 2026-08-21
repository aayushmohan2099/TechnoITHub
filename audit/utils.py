from .models import AuditLog

def log_action(actor, action, entity_type, entity_id, metadata=None):
    """
    Audit log record karne ke liye helper function.
    """
    AuditLog.objects.create(
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        metadata=metadata
    )