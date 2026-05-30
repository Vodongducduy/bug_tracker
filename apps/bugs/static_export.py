from __future__ import annotations

import shutil
from collections import OrderedDict
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

from django.conf import settings
from django.template.loader import render_to_string
from django.test.utils import override_settings
from django.test.client import RequestFactory
from django.urls import get_script_prefix, set_script_prefix

from apps.accounts.forms import LoginForm, RegisterForm


@dataclass(frozen=True)
class PageSpec:
    output_path: str
    template_name: str
    route_path: str
    active_url_name: str
    logged_in: bool
    context: dict


class PreviewUser(SimpleNamespace):
    def get_full_name(self):
        first_name = getattr(self, "first_name", "") or ""
        last_name = getattr(self, "last_name", "") or ""
        full_name = f"{first_name} {last_name}".strip()
        return full_name or getattr(self, "username", "")


class PreviewProject(SimpleNamespace):
    def get_status_display(self):
        labels = {
            "ACTIVE": "Active",
            "CLOSED": "Closed",
        }
        return labels.get(self.status, self.status)


class PreviewBug(SimpleNamespace):
    STATUS_CHOICES = (
        ("NEW", "New"),
        ("ASSIGNED", "Assigned"),
        ("IN_PROGRESS", "In Progress"),
        ("FIXED", "Fixed"),
        ("CLOSED", "Closed"),
        ("RE_OPENED", "Re-opened"),
    )

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def get_type_display(self):
        labels = {
            "Functional": "Functional Bug",
            "System": "System Bug",
            "UI": "UI Bug",
            "Performance": "Performance Bug",
        }
        return labels.get(self.type, self.type)

    def get_priority_display(self):
        labels = {
            "S": "Critical (S)",
            "A": "High (A)",
            "B": "Medium (B)",
        }
        return labels.get(self.priority, self.priority)


def _build_preview_data():
    admin = PreviewUser(
        id=1,
        username="duyadmin",
        first_name="Duy",
        last_name="Vo",
        email="duy@example.com",
        is_active=True,
        is_superuser=True,
        date_joined=datetime(2026, 5, 20, 8, 30),
    )
    qa = PreviewUser(
        id=2,
        username="linhqa",
        first_name="Linh",
        last_name="Tran",
        email="linh@example.com",
        is_active=True,
        is_superuser=False,
        date_joined=datetime(2026, 5, 22, 9, 15),
    )
    dev = PreviewUser(
        id=3,
        username="minhdev",
        first_name="Minh",
        last_name="Nguyen",
        email="minh@example.com",
        is_active=True,
        is_superuser=False,
        date_joined=datetime(2026, 5, 24, 10, 0),
    )
    suspended = PreviewUser(
        id=4,
        username="anhops",
        first_name="Anh",
        last_name="Pham",
        email="anh@example.com",
        is_active=False,
        is_superuser=False,
        date_joined=datetime(2026, 5, 26, 11, 45),
    )

    lead_role = SimpleNamespace(id=1, title="Project Lead")
    qa_role = SimpleNamespace(id=2, title="QA Engineer")
    dev_role = SimpleNamespace(id=3, title="Backend Developer")

    project = PreviewProject(
        id=1,
        name="Bugiz Web Portal",
        description="Main customer-facing web app where the team tracks login, checkout, and reporting issues.",
        status="ACTIVE",
    )
    secondary_project = PreviewProject(
        id=2,
        name="Internal Admin Console",
        description="Operations workspace for support and account management tasks.",
        status="CLOSED",
    )

    bug = PreviewBug(
        id=101,
        title="Login button does not respond on Safari",
        description=(
            "1. Open the sign-in form on Safari 17.\n"
            "2. Enter valid credentials.\n"
            "3. Press the Login button.\n"
            "4. Nothing happens and the loading state never appears."
        ),
        type="UI",
        status="IN_PROGRESS",
        priority="A",
        root_cause="The submit handler is blocked by a stale overlay layer on the auth card.",
        assign_to=dev,
        created_by=qa,
        updated_by=dev,
        updated_at=datetime(2026, 5, 31, 8, 45),
        project=project,
    )

    project_members = [
        SimpleNamespace(user=admin, role=lead_role, assign_at=datetime(2026, 5, 20, 8, 45)),
        SimpleNamespace(user=qa, role=qa_role, assign_at=datetime(2026, 5, 21, 10, 0)),
        SimpleNamespace(user=dev, role=dev_role, assign_at=datetime(2026, 5, 21, 10, 15)),
    ]

    activity_logs = [
        SimpleNamespace(
            performed_by=qa,
            action="CREATE_BUG",
            old_value="",
            new_value="Bug created",
            created_at=datetime(2026, 5, 30, 14, 20),
        ),
        SimpleNamespace(
            performed_by=admin,
            action="ASSIGN_BUG",
            old_value="Unassigned",
            new_value="Minh Nguyen",
            created_at=datetime(2026, 5, 30, 14, 40),
        ),
        SimpleNamespace(
            performed_by=dev,
            action="UPDATE_STATUS",
            old_value="Assigned",
            new_value="In Progress",
            created_at=datetime(2026, 5, 31, 8, 45),
        ),
    ]

    users = [admin, qa, dev, suspended]
    grouped_members = OrderedDict(
        [
            (
                project.name,
                [
                    SimpleNamespace(username=admin.username, email=admin.email, role_title=lead_role.title),
                    SimpleNamespace(username=qa.username, email=qa.email, role_title=qa_role.title),
                    SimpleNamespace(username=dev.username, email=dev.email, role_title=dev_role.title),
                ],
            ),
            (
                secondary_project.name,
                [
                    SimpleNamespace(username=suspended.username, email=suspended.email, role_title="Support"),
                ],
            ),
        ]
    )

    project_bugs = [
        bug,
        PreviewBug(
            id=102,
            title="Export report shows duplicated rows",
            description="CSV export duplicates filtered records when date range is empty.",
            type="Functional",
            status="NEW",
            priority="S",
            root_cause="",
            assign_to=qa,
            created_by=admin,
            updated_by=admin,
            updated_at=datetime(2026, 5, 31, 9, 5),
            project=project,
        ),
        PreviewBug(
            id=103,
            title="Billing webhook latency spike",
            description="Background job queue peaks above SLA after 6PM.",
            type="Performance",
            status="FIXED",
            priority="B",
            root_cause="Queue worker autoscaling threshold was too conservative.",
            assign_to=dev,
            created_by=qa,
            updated_by=dev,
            updated_at=datetime(2026, 5, 30, 18, 30),
            project=project,
        ),
    ]

    return {
        "admin": admin,
        "qa": qa,
        "dev": dev,
        "users": users,
        "roles": [lead_role, qa_role, dev_role],
        "project": project,
        "projects": [project, secondary_project],
        "project_members": project_members,
        "project_bugs": project_bugs,
        "bug": bug,
        "activity_logs": activity_logs,
        "grouped_members": grouped_members,
    }


def _build_page_specs():
    data = _build_preview_data()

    shared_logged_in = {
        "messages": [],
        "bug_summary": {
            "TOTAL": 18,
            "NEW": 4,
            "IN_PROGRESS": 6,
            "FIXED": 5,
            "CLOSED": 3,
        },
        "projects": data["projects"],
        "project_summary": [
            SimpleNamespace(name="Bugiz Web Portal", status="ACTIVE", total_bugs=12, new_bugs=4, resolved_bugs=6),
            SimpleNamespace(name="Internal Admin Console", status="CLOSED", total_bugs=6, new_bugs=0, resolved_bugs=6),
        ],
        "bug_stats": [
            SimpleNamespace(status="NEW", count=4),
            SimpleNamespace(status="IN_PROGRESS", count=6),
            SimpleNamespace(status="FIXED", count=5),
            SimpleNamespace(status="CLOSED", count=3),
        ],
    }

    login_form = LoginForm()
    register_form = RegisterForm()

    return [
        PageSpec(
            output_path="index.html",
            template_name="bugs/dashboard.html",
            route_path="/",
            active_url_name="dashboard",
            logged_in=True,
            context={**shared_logged_in},
        ),
        PageSpec(
            output_path="403.html",
            template_name="403.html",
            route_path="/",
            active_url_name="dashboard",
            logged_in=True,
            context={"messages": []},
        ),
        PageSpec(
            output_path="login/index.html",
            template_name="accounts/login.html",
            route_path="/login/",
            active_url_name="login",
            logged_in=False,
            context={"form": login_form},
        ),
        PageSpec(
            output_path="register/index.html",
            template_name="accounts/register.html",
            route_path="/register/",
            active_url_name="register",
            logged_in=False,
            context={"form": register_form},
        ),
        PageSpec(
            output_path="accounts/index.html",
            template_name="accounts/admin_list.html",
            route_path="/accounts/",
            active_url_name="account_list",
            logged_in=True,
            context={"messages": [], "users": data["users"]},
        ),
        PageSpec(
            output_path="accounts/create/index.html",
            template_name="accounts/admin_create.html",
            route_path="/accounts/create/",
            active_url_name="admin_create_account",
            logged_in=True,
            context={"messages": [], "form": RegisterForm()},
        ),
        PageSpec(
            output_path="accounts/members/index.html",
            template_name="accounts/member_list.html",
            route_path="/accounts/members/",
            active_url_name="member_list",
            logged_in=True,
            context={"messages": [], "grouped_members": data["grouped_members"]},
        ),
        PageSpec(
            output_path="reports/index.html",
            template_name="bugs/reports.html",
            route_path="/reports/",
            active_url_name="reports",
            logged_in=True,
            context={
                "messages": [],
                "project_summary": shared_logged_in["project_summary"],
                "bug_stats": shared_logged_in["bug_stats"],
            },
        ),
        PageSpec(
            output_path="bugs/project/create/index.html",
            template_name="bugs/create_project.html",
            route_path="/bugs/project/create/",
            active_url_name="create_project",
            logged_in=True,
            context={"messages": []},
        ),
        PageSpec(
            output_path="bugs/project/1/index.html",
            template_name="bugs/project_detail.html",
            route_path="/bugs/project/1/",
            active_url_name="dashboard",
            logged_in=True,
            context={
                "messages": [],
                "project": data["project"],
                "bugs": data["project_bugs"],
                "user_role": "Project Lead",
                "filters": {"q": "", "status": "", "priority": "", "type": ""},
            },
        ),
        PageSpec(
            output_path="bugs/project/1/create/index.html",
            template_name="bugs/create_bug.html",
            route_path="/bugs/project/1/create/",
            active_url_name="dashboard",
            logged_in=True,
            context={"messages": [], "project": data["project"]},
        ),
        PageSpec(
            output_path="bugs/project/1/members/index.html",
            template_name="bugs/manage_members.html",
            route_path="/bugs/project/1/members/",
            active_url_name="dashboard",
            logged_in=True,
            context={
                "messages": [],
                "project": data["project"],
                "members": data["project_members"],
                "available_users": [data["qa"], data["dev"]],
                "roles": data["roles"],
            },
        ),
        PageSpec(
            output_path="bugs/101/index.html",
            template_name="bugs/bug_detail.html",
            route_path="/bugs/101/",
            active_url_name="dashboard",
            logged_in=True,
            context={
                "messages": [],
                "bug": data["bug"],
                "activity_logs": data["activity_logs"],
                "project_members": data["project_members"],
            },
        ),
    ]


def _build_request(route_path: str, active_url_name: str, logged_in: bool):
    request = RequestFactory().get(route_path)
    request.logged_user = _build_preview_data()["admin"] if logged_in else None
    request.resolver_match = SimpleNamespace(url_name=active_url_name)
    return request


@contextmanager
def _site_render_settings(site_prefix: str):
    normalized_prefix = "/" + site_prefix.strip("/")
    previous_script_prefix = get_script_prefix()

    with override_settings(STATIC_URL=f"{normalized_prefix}/static/"):
        set_script_prefix(f"{normalized_prefix}/")
        try:
            yield normalized_prefix
        finally:
            set_script_prefix(previous_script_prefix)


def _write_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _copy_static_assets(output_dir: Path):
    destination = output_dir / "static"
    shutil.copytree(Path(settings.BASE_DIR) / "static", destination, dirs_exist_ok=True)


def _build_hub_page(output_dir: Path, site_prefix: str):
    links = [
        ("Dashboard", f"{site_prefix}/"),
        ("403", f"{site_prefix}/403.html"),
        ("Login", f"{site_prefix}/login/"),
        ("Register", f"{site_prefix}/register/"),
        ("Accounts", f"{site_prefix}/accounts/"),
        ("Create Account", f"{site_prefix}/accounts/create/"),
        ("Members", f"{site_prefix}/accounts/members/"),
        ("Reports", f"{site_prefix}/reports/"),
        ("Create Project", f"{site_prefix}/bugs/project/create/"),
        ("Project Detail", f"{site_prefix}/bugs/project/1/"),
        ("Create Bug", f"{site_prefix}/bugs/project/1/create/"),
        ("Manage Members", f"{site_prefix}/bugs/project/1/members/"),
        ("Bug Detail", f"{site_prefix}/bugs/101/"),
    ]
    items = "\n".join(
        f'<li><a href="{href}">{label}</a></li>' for label, href in links
    )
    hub_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bugiz Pages Preview</title>
  <style>
    body {{
      font-family: Inter, Arial, sans-serif;
      background: #f3f5ef;
      color: #223018;
      margin: 0;
      padding: 40px 24px;
    }}
    .wrap {{
      max-width: 820px;
      margin: 0 auto;
      background: #fff;
      border: 1px solid #d7dfcf;
      border-radius: 16px;
      padding: 28px;
      box-shadow: 0 18px 40px rgba(34, 48, 24, 0.08);
    }}
    h1 {{ margin-top: 0; }}
    ul {{ line-height: 1.9; }}
    a {{ color: #2d5518; text-decoration: none; font-weight: 600; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Bugiz Pages Preview</h1>
    <p>Static export of all previewable templates for GitHub Pages.</p>
    <ul>
      {items}
    </ul>
  </div>
</body>
</html>
"""
    _write_text(output_dir / "all-pages" / "index.html", hub_html)


def build_static_site(output_dir: Path | str, site_prefix: str = "/bug_tracker"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    _copy_static_assets(output_dir)

    with _site_render_settings(site_prefix) as normalized_prefix:
        for page in _build_page_specs():
            request = _build_request(page.route_path, page.active_url_name, page.logged_in)
            html = render_to_string(page.template_name, page.context, request=request)
            _write_text(output_dir / page.output_path, html)

        _build_hub_page(output_dir, normalized_prefix)
