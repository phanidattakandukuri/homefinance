import time
from collections import defaultdict, deque
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Small-process guardrail; use an API gateway/Redis limiter for multi-worker production."""
    def __init__(self, app, limit=120, window=60):
        super().__init__(app); self.limit=limit; self.window=window; self.hits=defaultdict(deque)
    async def dispatch(self, request: Request, call_next):
        now=time.monotonic(); key=request.client.host if request.client else "unknown"; q=self.hits[key]
        while q and now-q[0]>self.window: q.popleft()
        if len(q)>=self.limit: return JSONResponse({"error":{"message":"Rate limit exceeded"}},status_code=429)
        q.append(now); return await call_next(request)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response=await call_next(request); response.headers["X-Content-Type-Options"]="nosniff"; response.headers["X-Frame-Options"]="DENY"; response.headers["Referrer-Policy"]="no-referrer"; response.headers["Cache-Control"]="no-store"; return response
