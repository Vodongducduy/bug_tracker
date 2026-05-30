from pathlib import Path

from django.core.management.base import BaseCommand

from apps.bugs.static_export import build_static_site


class Command(BaseCommand):
    help = "Export static HTML previews for GitHub Pages."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            default="_site",
            help="Directory where rendered static pages will be written.",
        )
        parser.add_argument(
            "--site-prefix",
            default="/bug_tracker",
            help="URL prefix used by GitHub Pages.",
        )

    def handle(self, *args, **options):
        build_static_site(
            output_dir=Path(options["output_dir"]),
            site_prefix=options["site_prefix"],
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Exported static preview site to {options['output_dir']}"
            )
        )
