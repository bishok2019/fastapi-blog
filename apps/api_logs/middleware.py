from typing import Callable

from fastapi import Request, Response
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from apps.api_logs.models import APILog
from apps.database import get_db


class APILoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Print request
        print("=" * 25 + "Request Log Start" + "=" * 25)
        print("Request", request)
        print(f"Request Method: {request.method}")
        print(f"Request URL: {request.url}")
        print(f"Request Headers: {request.headers}")
        print(f"Request Client: {request.client}")
        print("request status code:", request.scope.get("status_code"))
        print("Request path params:", request.path_params)
        print("Request query params:", request.query_params)
        print("Request cookies:", request.cookies)
        print("Request state:", request.state)
        print("Request app:", request.app)
        print("Request type:", type(request))
        print("Request body:", await request.body())

        print("=" * 25 + "Response Log Start" + "=" * 25)

        # Process and return response
        response = await call_next(request)
        print(f"Response: {response}")
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response media type: {response.media_type}")
        print(f"Response background: {response.background}")
        print(f"Response type: {type(response)}")
        print("Response body:", response.body_iterator)
        return response
