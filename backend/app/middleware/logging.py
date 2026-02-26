"""
Structured Logging Middleware for Vibe PDF Platform

Provides comprehensive request/response logging with correlation IDs,
performance metrics, and structured JSON output for production observability.
"""

import json
import logging
import time
import uuid
from contextvars import ContextVar
from typing import Any, Callable, Optional

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Context variable for storing request-specific data
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


class StructuredLogger:
    """
    Structured logger with JSON output for production environments.
    """
    
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configure handlers for structured logging."""
        # Console handler with JSON formatter
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JsonFormatter())
        self.logger.addHandler(console_handler)
    
    def _build_log(
        self,
        level: str,
        message: str,
        extra: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Build structured log message."""
        log_data = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "level": level,
            "message": message,
            "request_id": request_id_var.get(),
            "user_id": user_id_var.get(),
        }
        
        if extra:
            log_data.update(extra)
        
        return log_data
    
    def debug(self, message: str, **kwargs: Any):
        """Log debug message."""
        self.logger.debug(json.dumps(self._build_log("DEBUG", message, kwargs)))
    
    def info(self, message: str, **kwargs: Any):
        """Log info message."""
        self.logger.info(json.dumps(self._build_log("INFO", message, kwargs)))
    
    def warning(self, message: str, **kwargs: Any):
        """Log warning message."""
        self.logger.warning(json.dumps(self._build_log("WARNING", message, kwargs)))
    
    def error(self, message: str, **kwargs: Any):
        """Log error message."""
        self.logger.error(json.dumps(self._build_log("ERROR", message, kwargs)))
    
    def critical(self, message: str, **kwargs: Any):
        """Log critical message."""
        self.logger.critical(json.dumps(self._build_log("CRITICAL", message, kwargs)))
    
    def exception(self, message: str, **kwargs: Any):
        """Log exception with traceback."""
        self.logger.exception(json.dumps(self._build_log("ERROR", message, kwargs)))


class JsonFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        try:
            log_data = json.loads(record.getMessage())
            return json.dumps(log_data)
        except json.JSONDecodeError:
            return json.dumps({
                "timestamp": self.formatTime(record),
                "level": record.levelname,
                "message": record.getMessage(),
                "logger": record.name,
            })


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for comprehensive request/response logging.
    
    Features:
    - Request ID correlation
    - Performance metrics
    - Request/Response body logging (optional)
    - Error tracking
    """
    
    def __init__(
        self,
        app: ASGIApp,
        logger: Optional[StructuredLogger] = None,
        log_request_body: bool = False,
        log_response_body: bool = False,
        exclude_paths: Optional[list[str]] = None,
    ):
        super().__init__(app)
        self.logger = logger or StructuredLogger("vibe-pdf")
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/favicon.ico"]
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[..., Any]
    ) -> Response:
        """Process request and log details."""
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request_id_var.set(request_id)
        
        # Start timing
        start_time = time.perf_counter()
        
        # Build request log
        request_info = {
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }
        
        # Log request
        self.logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                **request_info,
                "type": "request_start",
            }
        )
        
        # Process request
        response: Optional[Response] = None
        error: Optional[Exception] = None
        
        try:
            response = await call_next(request)
        except Exception as e:
            error = e
            raise
        finally:
            # Calculate duration
            duration = time.perf_counter() - start_time
            duration_ms = round(duration * 1000, 2)
            
            # Build response log
            response_info = {
                "status_code": response.status_code if response else 500,
                "duration_ms": duration_ms,
                "request_id": request_id,
            }
            
            if error:
                self.logger.error(
                    f"Request failed: {request.method} {request.url.path}",
                    extra={
                        **request_info,
                        **response_info,
                        "error_type": type(error).__name__,
                        "error_message": str(error),
                        "type": "request_error",
                    }
                )
            else:
                log_level = "info" if response.status_code < 400 else "warning"
                getattr(self.logger, log_level)(
                    f"Request completed: {request.method} {request.url.path}",
                    extra={
                        **request_info,
                        **response_info,
                        "type": "request_complete",
                    }
                )
        
        # Add request ID to response headers
        if response:
            response.headers["X-Request-ID"] = request_id
        
        return response


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name)


# Application lifecycle logging
async def log_startup(app: FastAPI):
    """Log application startup."""
    logger = get_logger("vibe-pdf.startup")
    logger.info("Application starting up")


async def log_shutdown(app: FastAPI):
    """Log application shutdown."""
    logger = get_logger("vibe-pdf.startup")
    logger.info("Application shutting down")


# Health check logging utility
async def log_health_check(
    name: str,
    status: str,
    duration_ms: float,
    details: Optional[dict[str, Any]] = None
):
    """Log health check result."""
    logger = get_logger("vibe-pdf.health")
    logger.info(
        f"Health check: {name} - {status}",
        extra={
            "check_name": name,
            "status": status,
            "duration_ms": duration_ms,
            "details": details or {},
            "type": "health_check",
        }
    )


# Error tracking utility
async def log_error(
    error: Exception,
    context: Optional[dict[str, Any]] = None
):
    """Log error with context."""
    logger = get_logger("vibe-pdf.errors")
    logger.error(
        f"Error occurred: {type(error).__name__}",
        extra={
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "type": "error",
        }
    )
