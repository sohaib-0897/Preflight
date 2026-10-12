"""Metadata-only OpenTelemetry spans. No prompts, credentials or provider reasoning."""

import json
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


class JsonSpanExporter(SpanExporter):
    def __init__(self, path):
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        self.handler = RotatingFileHandler(destination, maxBytes=2 * 1024 * 1024, backupCount=2)
        self.handler.setFormatter(logging.Formatter("%(message)s"))

    def export(self, spans):
        for span in spans:
            record = {
                "event": "otel_span",
                "name": span.name,
                "trace_id": format(span.context.trace_id, "032x"),
                "span_id": format(span.context.span_id, "016x"),
                "parent_span_id": format(span.parent.span_id, "016x") if span.parent else None,
                "start_ns": span.start_time,
                "end_ns": span.end_time,
                "status": span.status.status_code.name,
                "attributes": {
                    k: v
                    for k, v in span.attributes.items()
                    if k
                    in {
                        "http.request.method",
                        "http.route",
                        "http.response.status_code",
                        "preflight.request_id",
                        "preflight.run_id",
                        "preflight.scenario_id",
                        "preflight.trial",
                        "preflight.execution_returned",
                    }
                },
            }
            self.handler.handle(
                logging.LogRecord(
                    "preflight.trace", logging.INFO, "", 0, json.dumps(record), (), None
                )
            )
        return SpanExportResult.SUCCESS

    def shutdown(self):
        self.handler.close()


provider = TracerProvider(
    resource=Resource.create({"service.name": "preflight", "service.version": "0.1.0"})
)
if os.environ.get("PREFLIGHT_TRACE_FILE"):
    provider.add_span_processor(
        SimpleSpanProcessor(JsonSpanExporter(os.environ["PREFLIGHT_TRACE_FILE"]))
    )
tracer = provider.get_tracer("preflight", "0.1.0")
propagator = TraceContextTextMapPropagator()


def context_headers():
    headers = {}
    propagator.inject(headers)
    return headers


def identifiers(span=None):
    context = (span or trace.get_current_span()).get_span_context()
    return {
        "trace_id": format(context.trace_id, "032x"),
        "span_id": format(context.span_id, "016x"),
    }
