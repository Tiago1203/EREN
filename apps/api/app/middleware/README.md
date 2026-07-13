# app/middleware

**Custom ASGI/HTTP middleware.**

- `request_context.py` — `RequestContextMiddleware` assigns an `X-Request-ID`
  correlation id to every request and echoes it on the response.

Register middleware in `app.main.create_app`. Extend with timing, auth context,
etc. as needed.
