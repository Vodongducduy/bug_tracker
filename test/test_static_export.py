import os
import unittest
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
os.environ.setdefault("STATIC_EXPORT", "1")

import django

django.setup()

from apps.bugs.static_export import build_static_site


class StaticExportTests(unittest.TestCase):
    def test_build_static_site_exports_all_preview_pages(self):
        output_dir = Path("D:/ProjecDh/qltt/.tmp-test-output/static-export")

        build_static_site(output_dir, site_prefix="/bug_tracker")

        expected_pages = [
            "index.html",
            "403.html",
            "all-pages/index.html",
            "login/index.html",
            "register/index.html",
            "accounts/index.html",
            "accounts/create/index.html",
            "accounts/members/index.html",
            "reports/index.html",
            "bugs/project/create/index.html",
            "bugs/project/1/index.html",
            "bugs/project/1/create/index.html",
            "bugs/project/1/members/index.html",
            "bugs/101/index.html",
        ]

        for relative_path in expected_pages:
            self.assertTrue(
                (output_dir / relative_path).exists(),
                f"Missing exported page: {relative_path}",
            )

        dashboard_html = (output_dir / "index.html").read_text(encoding="utf-8")
        self.assertIn("Overview", dashboard_html)
        self.assertIn("/bug_tracker/static/css/styles.css", dashboard_html)
        self.assertIn("/bug_tracker/reports/", dashboard_html)
        self.assertNotIn("{%", dashboard_html)
        self.assertNotIn("{{", dashboard_html)

        hub_html = (output_dir / "all-pages/index.html").read_text(encoding="utf-8")
        self.assertIn("Bugiz Pages Preview", hub_html)
        self.assertIn("/bug_tracker/bugs/project/1/", hub_html)

        bug_detail_html = (output_dir / "bugs/101/index.html").read_text(encoding="utf-8")
        self.assertIn("Login button does not respond on Safari", bug_detail_html)


if __name__ == "__main__":
    unittest.main()
