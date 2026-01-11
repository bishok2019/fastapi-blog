import json
import traceback
from typing import Callable

from fastapi import Request, Response
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from apps.api_logs.models import APILog, ErrorLog
from apps.database import SessionLocal, get_db

# class APILoggingMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next: Callable) -> Response:
#         # Print request
#         print("=" * 25 + "Request Log Start" + "=" * 25)
#         print("Request", request)
#         print(f"Request Method: {request.method}")
#         print(f"Request URL: {request.url}")
#         # print(f"Request Headers: {request.headers}")
#         print(f"Request Headers: {dict(request.headers)}")
#         print(f"Request Client: {request.client}")
#         print("request status code:", request.scope.get("status_code"))
#         print("Request path params:", request.path_params)
#         print("Request query params:", request.query_params)
#         print("Request cookies:", request.cookies)
#         print("Request state:", request.state)
#         print("Request app:", request.app)
#         print("Request type:", type(request))
#         print("Request json body:", await request.json())
#         print("Request body:", await request.body())
#         print("user agent:", request.headers.get("user-agent"))

#         print("=" * 25 + "Response Log Start" + "=" * 25)

#         # Process and return response
#         response = await call_next(request)
#         print(f"Response: {response}")
#         print(f"Response status code: {response.status_code}")
#         print(f"Response headers: {response.headers}")
#         print(f"Response media type: {response.media_type}")
#         print(f"Response background: {response.background}")
#         print(f"Response type: {type(response)}")

#         response_body = b""
#         async for chunk in response.body_iterator:
#             response_body += chunk
#         print("Response body:", response_body.decode())
#         # print("Response body:", response.body_iterator)
#         new_response = Response(
#             content=response_body,
#             status_code=response.status_code,
#             headers=dict(response.headers),
#             media_type=response.media_type,
#         )


#         return


# class APILoggingMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next: Callable) -> Response:
#         response_body = b""  # initialize early
#         response_status = 500
#         response_headers = {}
#         response_media_type = "application/json"

#         # Skip GET requests
#         if request.method.upper() == "GET":
#             return await call_next(request)

#         try:
#             # Read request body
#             try:
#                 body = await request.json()
#             except Exception:
#                 body = None

#             # Process response
#             response = await call_next(request)

#             # Read response body
#             response_body = b""
#             async for chunk in response.body_iterator:
#                 response_body += chunk

#             try:
#                 response_content = json.loads(response_body.decode())
#             except Exception:
#                 response_content = response_body.decode()

#             # Save response metadata
#             response_status = response.status_code
#             response_headers = dict(response.headers)
#             response_media_type = response.media_type

#             # Log API call
#             db: Session = next(get_db())
#             api_log = APILog(
#                 url=str(request.url),
#                 method=request.method,
#                 ip=request.client.host if request.client else None,
#                 user_agent=request.headers.get("user-agent"),
#                 body=body,
#                 header=dict(request.headers),
#                 response=response_content,
#                 status_code=str(response_status),
#             )
#             db.add(api_log)
#             db.commit()

#         except Exception as exc:
#             # Log errors
#             db: Session = next(get_db())
#             error_log = ErrorLog(
#                 url=str(request.url),
#                 method=request.method.lower(),
#                 body=body if "body" in locals() else None,
#                 header=dict(request.headers),
#                 response="".join(
#                     traceback.format_exception(type(exc), exc, exc.__traceback__)
#                 ),
#             )
#             db.add(error_log)
#             db.commit()

#         # Return response safely
#         return Response(
#             content=response_body,
#             status_code=response_status,
#             headers=response_headers,
#             media_type=response_media_type,
#         )


class APILoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response_body = b""
        response_status = 500
        response_headers = {}
        response_media_type = "application/json"
        body = None

        try:
            # Skip GET requests
            if request.method.upper() != "GET":
                # Read request body
                try:
                    body = await request.json()
                except Exception:
                    body = None

            # Get response
            response = await call_next(request)

            # Read response body safely
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk

            # Convert response to string for logging
            try:
                response_content = json.dumps(json.loads(response_body.decode()))
            except Exception:
                response_content = response_body.decode()

            # Save metadata
            response_status = response.status_code
            response_headers = dict(response.headers)
            response_media_type = response.media_type

            # Log API call
            if request.method.upper() != "GET":
                db: Session = next(get_db())
                api_log = APILog(
                    url=str(request.url),
                    method=request.method,
                    ip=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                    body=body,
                    header=dict(request.headers),
                    response=response_content,
                    status_code=str(response_status),
                )
                db.add(api_log)
                db.commit()

        except Exception as exc:
            # Log errors
            db: Session = next(get_db())
            error_log = ErrorLog(
                url=str(request.url),
                method=request.method.lower(),
                body=body if "body" in locals() else None,
                header=dict(request.headers),
                response="".join(
                    traceback.format_exception(type(exc), exc, exc.__traceback__)
                ),
            )
            db.add(error_log)
            db.commit()
            # Override response with error
            # response_body = json.dumps({"detail": str(exc)}).encode()
            # response_status = 500
            # response_headers = {"content-type": "application/json"}
            # response_media_type = "application/json"

        # Return the original response content safely
        return Response(
            content=response_body,
            status_code=response_status,
            headers=response_headers,
            media_type=response_media_type,
        )
