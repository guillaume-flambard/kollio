from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.util.re import parse_env_headers

from src.platform.config import Settings


def configure_telemetry(
    settings: Settings, *, service_name: str = "kollio-api"
) -> TracerProvider | None:
    if not settings.otel_exporter_otlp_traces_endpoint:
        return None
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    exporter = OTLPSpanExporter(
        endpoint=settings.otel_exporter_otlp_traces_endpoint,
        headers=dict(parse_env_headers(settings.otel_exporter_otlp_headers.get_secret_value())),
        timeout=5,
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return provider
