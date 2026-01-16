from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# Initialize engines once
# nlp_engine_name="en_core_web_sm" helps start up faster if model matches
analyzer = AnalyzerEngine() 
anonymizer = AnonymizerEngine()

def mask_pii_processor(logger, method_name, event_dict):
    """
    Structlog processor to mask PII in the 'event' field.
    """
    event_text = event_dict.get("event")
    if isinstance(event_text, str):
        try:
            results = analyzer.analyze(text=event_text, language="en")
            if results:
                anonymized_result = anonymizer.anonymize(
                    text=event_text, analyzer_results=results
                )
                event_dict["event"] = anonymized_result.text
        except Exception:
            # Fallback if analysis fails, logs shouldn't crash app
            # Maybe log an error to stderr or just pass through
            pass
            
    return event_dict
