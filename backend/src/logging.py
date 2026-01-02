import logging
import sys
import structlog
from typing import Any, MutableMapping
from contextvars import ContextVar
import os

# Context Variable for Request ID (Correlation ID)
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="unknown")

# Sensitive keys to mask blindly
SENSITIVE_KEYS = {"password", "token", "access_token", "secret", "ssn", "credit_card", "api_key"}

# Lazy load Presidio to avoid startup/import errors if model missing
_analyzer_engine = None

def get_analyzer_engine():
    global _analyzer_engine
    if _analyzer_engine is None:
        try:
            from presidio_analyzer import AnalyzerEngine
            _analyzer_engine = AnalyzerEngine()
        except Exception as e:
            # Fallback or log warning if model missing
            print(f"Warning: Presidio Analyzer failed to load: {e}")
            _analyzer_engine = False # Sentinel for failed
    return _analyzer_engine if _analyzer_engine is not False else None

def mask_sensitive_keys(logger: logging.Logger, method_name: str, event_dict: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    """
    Masks values for specific sensitive keys in the event dictionary.
    """
    for key in event_dict.copy():
        if key.lower() in SENSITIVE_KEYS:
            event_dict[key] = "***"
    return event_dict

def mask_exception_phi(logger: logging.Logger, method_name: str, event_dict: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    """
    Uses Presidio to mask PHI in exception tracebacks if present.
    """
    exc_info = event_dict.get("exception")
    if exc_info and isinstance(exc_info, str):
        engine = get_analyzer_engine()
        if engine:
            try:
                results = engine.analyze(text=exc_info, language="en", entities=["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "US_SSN"])
                # Note: Presidio Analyzer only analyzes. Anonymizer is separate.
                # For simplicity here, we might just flag it or use basic replacement.
                # Doing full Anonymization synchronously on tracebacks might be slow.
                # Requirement: "Implement Presidio integration for uncaught exceptions (Synchronous)"
                
                from presidio_anonymizer import AnonymizerEngine
                anonymizer = AnonymizerEngine()
                anonymized_result = anonymizer.anonymize(text=exc_info, analyzer_results=results)
                event_dict["exception"] = anonymized_result.text
            except Exception as e:
                # Fallback if analysis fails
                print(f"DEBUG: Presidio Error: {e}")
                pass
    return event_dict

def configure_logging():
    """
    Configures structlog and standard logging for JSON output.
    """
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info, # Adds 'exception' key
        mask_sensitive_keys,               # Mask keys first
        mask_exception_phi,                # Mask PHI in exception text
        structlog.processors.JSONRenderer(),
    ]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard logging to use structlog
    handler = logging.StreamHandler(sys.stdout)
    # We need to make sure stdlib logs go through structlog processors or at least are JSON
    # structlog.stdlib.ProcessorFormatter works for this.
    
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=[
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.ExtraAdder(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.format_exc_info,
            mask_sensitive_keys,
            mask_exception_phi,
        ]
    )
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.INFO)

    # Uvicorn access overrides
    # (Optional: Uvicorn uses its own logging config, often needs specific override)

