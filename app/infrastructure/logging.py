import logging
import json
import sys
import contextvars
from datetime import datetime
from typing import Any, Dict

correlation_id = contextvars.ContextVar("correlation_id", default="none")

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "correlation_id": correlation_id.get(),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    # Silence third-party loggers if needed
    logging.getLogger("uvicorn.access").handlers = [handler]
