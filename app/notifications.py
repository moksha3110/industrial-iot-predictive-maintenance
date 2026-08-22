import logging
from .config import get_settings
log = logging.getLogger(__name__)

def notify_owner(subject: str, message: str) -> bool:
    settings = get_settings()
    if not settings.sns_topic_arn or not settings.aws_region:
        log.warning("LOCAL OWNER NOTIFICATION | %s | %s", subject, message)
        return True
    try:
        import boto3
        boto3.client("sns", region_name=settings.aws_region).publish(TopicArn=settings.sns_topic_arn, Subject=subject[:100], Message=message)
        log.info("SNS notification published")
        return True
    except Exception:
        log.exception("SNS failed; alert remains persisted and visible")
        return False
