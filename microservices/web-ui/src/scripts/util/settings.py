import os


class Settings:
    def __init__(self):
        self.app_port = int(os.environ["APP_PORT"])
        self.app_host = os.environ["APP_HOST"]

        self.db_api_url = os.environ["DB_API_URL"]
        self.picture_api_url = os.environ["PICTURE_API_URL"]

        # IMPORTANT:
        # Keep this value stable and shared across all web-ui pods.
        # If pods use different secrets, session cookies become invalid when
        # traffic is routed to a different pod.
        self.secret_key = os.environ["WEB_UI_SECRET_KEY"]

        # Shared Redis session store (required for multi-pod session continuity).
        self.redis_url = os.environ.get(
            "REDIS_URL",
            "redis://redis-service.redis.svc.cluster.local:6379/0"
        )

        # Cookie settings (browser stores only session id; data stays in Redis).
        self.session_cookie_name = os.environ.get("SESSION_COOKIE_NAME", "hobbora_sid")
        self.session_cookie_secure = os.environ.get("SESSION_COOKIE_SECURE", "true").lower() == "true"
        self.session_cookie_samesite = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")
        self.session_lifetime_minutes = int(os.environ.get("SESSION_LIFETIME_MINUTES", "30"))

        self.config = {"name": "Hobbora"}

    # def _get_all_paths_in_folder(self, directory):
    #     file_urls = []
    #     for filename in os.listdir(directory):
    #         # Get the full path
    #         file_path = os.path.join(directory, filename)
    #         if os.path.isfile(file_path):
    #             # Convert file path to a URL-like path (if needed)
    #             file_urls.append(file_path.replace('\\', "/").replace('microservices/web-ui/src/static/', ""))
    #     return file_urls