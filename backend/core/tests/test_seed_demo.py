import pytest
from django.core.management import call_command

from accounts.models import User
from billing.models import Invoice
from core.demo_seed import run_demo_seed
from core.demo_seed.constants import (
    DEMO_PASSWORD,
    DEMO_SUPERUSER,
    OAK_HEIGHTS_SLUG,
    PALM_GROVE_SLUG,
)
from estates.models import Estate
from platform_admin.models import PlatformAuditLog
from residents.models import ResidentProfile


@pytest.mark.django_db
class TestSeedDemo:
    def test_seed_demo_is_idempotent(self):
        first = run_demo_seed(flush=True, verbosity=0)
        second = run_demo_seed(flush=False, verbosity=0)

        assert Estate.objects.filter(slug=PALM_GROVE_SLUG).exists()
        assert Estate.objects.filter(slug=OAK_HEIGHTS_SLUG).exists()
        assert User.objects.filter(email=DEMO_SUPERUSER["email"]).exists()
        assert User.objects.get(email=DEMO_SUPERUSER["email"]).check_password(DEMO_PASSWORD)

        palm = Estate.objects.get(slug=PALM_GROVE_SLUG)
        assert Invoice.objects.filter(estate=palm).count() >= 2
        assert ResidentProfile.objects.filter(estate=palm, status=ResidentProfile.Status.PENDING).exists()
        assert PlatformAuditLog.objects.filter(estate=palm).exists()

        assert sum(first.created.values()) >= sum(second.created.values())

    def test_management_command_runs(self):
        call_command("seed_demo", verbosity=0)
