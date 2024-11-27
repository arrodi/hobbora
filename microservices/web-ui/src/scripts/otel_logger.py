import logging
from opentelemetry import logs
from opentelemetry.exporter.otlp.proto.http.log_exporter import OTLPLogExporter
from opentelemetry.sdk.logs import LoggerProvider, BatchLogProcessor

def setup_otlp_logging(otel_collector_url: str):
    # Set up OpenTelemetry OTLP log exporter
    otlp_exporter = OTLPLogExporter(endpoint=otel_collector_url)

    # Set up logger provider and processor
    log_provider = LoggerProvider()
    log_provider.add_log_processor(BatchLogProcessor(otlp_exporter))

    # Set the OpenTelemetry logger provider
    logs.set_logger_provider(log_provider)

    # Set up the basic Python logger
    logger = logging.getLogger()
    return logger