from django.core.management.base import BaseCommand

from core.demo_seed import run_demo_seed


class Command(BaseCommand):
    help = "Seed demo / QA data for all EstateOS dashboards (idempotent; use --flush to reset)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Remove existing demo data (@demo.estateos users and demo estates) before seeding.",
        )

    def handle(self, *args, **options):
        summary = run_demo_seed(flush=options["flush"], verbosity=options["verbosity"])
        self.stdout.write(self.style.SUCCESS("Demo seed completed."))
        if summary.created:
            self.stdout.write("Created:")
            for key, count in sorted(summary.created.items()):
                self.stdout.write(f"  {key}: {count}")
        if summary.skipped:
            self.stdout.write("Already present (skipped create):")
            for key, count in sorted(summary.skipped.items()):
                self.stdout.write(f"  {key}: {count}")
