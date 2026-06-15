"""
Locust load test script for EstateOS API.

Run:
    locust -f tests/load/locustfile.py --host=http://localhost:8000

Set environment variables for authenticated load tests:
    ESTATEOS_TEST_EMAIL, ESTATEOS_TEST_PASSWORD, ESTATEOS_ESTATE_ID
"""
import os

from locust import HttpUser, between, task


class EstateOSUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.estate_id = os.getenv("ESTATEOS_ESTATE_ID", "")
        self.token = None
        email = os.getenv("ESTATEOS_TEST_EMAIL")
        password = os.getenv("ESTATEOS_TEST_PASSWORD")
        if email and password:
            response = self.client.post(
                "/api/v1/accounts/auth/token/",
                json={"email": email, "password": password},
                name="/api/v1/accounts/auth/token/",
            )
            if response.status_code == 200:
                self.token = response.json().get("access")

    def _headers(self):
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if self.estate_id:
            headers["X-Estate-Id"] = self.estate_id
        return headers

    @task(3)
    def health_check(self):
        self.client.get("/health/", name="/health/")

    @task(2)
    def current_user(self):
        if not self.token:
            return
        self.client.get(
            "/api/v1/accounts/me/",
            headers=self._headers(),
            name="/api/v1/accounts/me/",
        )

    @task(1)
    def token_refresh(self):
        email = os.getenv("ESTATEOS_TEST_EMAIL")
        password = os.getenv("ESTATEOS_TEST_PASSWORD")
        if not email or not password:
            return
        login = self.client.post(
            "/api/v1/accounts/auth/token/",
            json={"email": email, "password": password},
            name="/api/v1/accounts/auth/token/ [refresh-flow]",
        )
        if login.status_code != 200:
            return
        refresh = login.json().get("refresh")
        if refresh:
            self.client.post(
                "/api/v1/accounts/auth/token/refresh/",
                json={"refresh": refresh},
                name="/api/v1/accounts/auth/token/refresh/",
            )
