import logging

logger = logging.getLogger("conversations")


def log_error(error_message, context=None):
    extra = context or {}
    logger.error(
        error_message,
        extra=extra,
        exc_info=True
    )


def log_info(message, context=None):
    extra = context or {}
    logger.info(message, extra=extra)


def log_warning(message, context=None):
    extra = context or {}
    logger.warning(message, extra=extra)
