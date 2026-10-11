# accounts/middleware.py


class ClientIPMiddleware:
    """
    Attach the direct client IP address to request.client_ip.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.client_ip = request.META.get(
            "REMOTE_ADDR",
            "Unknown",
        )

        return self.get_response(request)
