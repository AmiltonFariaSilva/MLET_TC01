import time
import logging
from uuid import uuid4
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("monitoring")

class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        trace_id = request.headers.get("X-Request-ID") or str(uuid4())
        # Add trace id into state so handlers can reuse
        request.state.trace_id = trace_id

        response = None
        error = None
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            error = str(exc)
            raise
        finally:
            process_time = (time.perf_counter() - start_time) * 1000
            remote_addr = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
            log = {
                "event": "http_request",
                "method": request.method,
                "path": request.url.path,
                "status_code": getattr(response, "status_code", 500),
                "duration_ms": round(process_time, 2),
                "client_ip": remote_addr,
                "user_agent": user_agent,
                "trace_id": trace_id,
                "error": error,
            }
            logger.info(log)