"""Temporary API smoke tests against demo seed data."""
from __future__ import annotations

import json
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")

import django

django.setup()

from django.conf import settings
from django.core.management import call_command
from rest_framework.test import APIClient

from core.demo_seed.constants import DEMO_PASSWORD, OAK_HEIGHTS_SLUG, PALM_GROVE_SLUG
from estates.models import Estate

if "testserver" not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, "testserver"]

TOKEN_URL = "/api/v1/accounts/auth/token/"
PLATFORM_OVERVIEW = "/api/v1/platform/overview/"
INVOICES = "/api/v1/billing/invoices/"
PROFILES = "/api/v1/residents/profiles/"
PALM_GROVE_INVOICE_NUMBERS = {"INV-DEMO-2026-0001", "INV-DEMO-2026-0002"}


def resp_data(response):
    if hasattr(response, "data"):
        return response.data
    try:
        return json.loads(response.content.decode())
    except Exception:
        return response.content.decode(errors="replace")


def snippet(body, max_len=120):
    if body is None:
        return ""
    if isinstance(body, (dict, list)):
        text = json.dumps(body, default=str)
    else:
        text = str(body)
    text = text.replace("\n", " ")
    return text[:max_len] + ("…" if len(text) > max_len else "")


class Row:
    def __init__(self, endpoint, user, expected, actual, note="", body=None, passed=None):
        self.endpoint = endpoint
        self.user = user
        self.expected = expected
        self.actual = actual
        self.note = note
        self.body = body or ""
        self.passed = passed if passed is not None else (str(actual) == str(expected))


def login(client: APIClient, email: str):
    return client.post(TOKEN_URL, {"email": email, "password": DEMO_PASSWORD}, format="json")


def auth_get(client: APIClient, url: str, token: str, estate_id: str | None = None):
    headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
    if estate_id:
        headers["HTTP_X_ESTATE_ID"] = estate_id
    return client.get(url, **headers)


def invoice_numbers(response):
    data = resp_data(response)
    items = data.get("results", data) if isinstance(data, dict) else data
    if not isinstance(items, list):
        return set()
    return {item.get("invoice_number") for item in items if isinstance(item, dict)}


def main() -> int:
    call_command("migrate", verbosity=0, interactive=False)
    call_command("seed_demo", verbosity=0)

    palm = Estate.objects.get(slug=PALM_GROVE_SLUG)
    oak = Estate.objects.get(slug=OAK_HEIGHTS_SLUG)
    rows: list[Row] = []
    client = APIClient()

    # 1 superadmin
    email = "superadmin@demo.estateos"
    r = login(client, email)
    rows.append(Row(TOKEN_URL, email, 200, r.status_code, "login", snippet(resp_data(r))))
    if r.status_code == 200:
        token = resp_data(r)["access"]
        r2 = auth_get(client, PLATFORM_OVERVIEW, token)
        rows.append(
            Row(
                PLATFORM_OVERVIEW,
                email,
                200,
                r2.status_code,
                body=snippet(resp_data(r2)),
            )
        )
    else:
        rows.append(Row(PLATFORM_OVERVIEW, email, 200, "skipped", "no token"))

    # 2 palm admin tenant
    email = "admin@palmgrovedemo.estateos"
    r = login(client, email)
    rows.append(Row(TOKEN_URL, email, 200, r.status_code, "login", snippet(resp_data(r))))
    if r.status_code == 200:
        token = resp_data(r)["access"]
        for path in (INVOICES, PROFILES):
            r2 = auth_get(client, path, token, str(palm.id))
            rows.append(
                Row(
                    path,
                    email,
                    200,
                    r2.status_code,
                    f"X-Estate-Id={palm.id}",
                    snippet(resp_data(r2)),
                )
            )

    # 3 resident blocked from platform
    email = "resident1@palmgrovedemo.estateos"
    r = login(client, email)
    rows.append(Row(TOKEN_URL, email, 200, r.status_code, "login", snippet(resp_data(r))))
    if r.status_code == 200:
        token = resp_data(r)["access"]
        r2 = auth_get(client, PLATFORM_OVERVIEW, token)
        rows.append(
            Row(
                PLATFORM_OVERVIEW,
                email,
                403,
                r2.status_code,
                "resident denied",
                snippet(resp_data(r2)),
            )
        )

    # 4 cross-tenant oak resident
    email = "resident1@oakheightsdemo.estateos"
    r = login(client, email)
    rows.append(Row(TOKEN_URL, email, 200, r.status_code, "login", snippet(resp_data(r))))
    if r.status_code == 200:
        token = resp_data(r)["access"]
        r2 = auth_get(client, INVOICES, token, str(oak.id))
        nums = invoice_numbers(r2)
        leak = nums & PALM_GROVE_INVOICE_NUMBERS
        passed = r2.status_code == 200 and not leak
        rows.append(
            Row(
                INVOICES,
                email,
                "200, no palm invoices",
                f"{r2.status_code}, nums={sorted(n for n in nums if n)}",
                f"X-Estate-Id={oak.id}",
                snippet(resp_data(r2)),
                passed=passed,
            )
        )
        r3 = auth_get(client, INVOICES, token, str(palm.id))
        rows.append(
            Row(
                INVOICES,
                email,
                403,
                r3.status_code,
                f"X-Estate-Id={palm.id} cross-tenant",
                snippet(resp_data(r3)),
            )
        )

    # 5 pending resident2
    email = "resident2@palmgrovedemo.estateos"
    r = login(client, email)
    pending = resp_data(r).get("pending_membership") if r.status_code == 200 else None
    rows.append(
        Row(
            TOKEN_URL,
            email,
            "200, pending_membership=True",
            f"{r.status_code}, pending_membership={pending!r}",
            "auth response",
            snippet(resp_data(r)),
            passed=(r.status_code == 200 and pending is True),
        )
    )

    headers = ("endpoint", "user", "expected", "actual", "error/body snippet")
    print(" | ".join(headers))
    print("-+-".join("-" * 24 for _ in headers))
    failures = []
    for row in rows:
        detail = row.note
        if row.body:
            detail = f"{detail} | {row.body}" if detail else row.body
        print(f"{row.endpoint} | {row.user} | {row.expected} | {row.actual} | {detail}")
        if not row.passed:
            failures.append(row)

    print()
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures:
            print(f"  {f.endpoint} ({f.user}): expected {f.expected}, got {f.actual}")
            if f.note or f.body:
                print(f"    {f.note} {f.body}".strip())
        return 1
    print("All smoke checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
