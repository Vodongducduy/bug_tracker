from django.shortcuts import render
from django.db import connection
from apps.accounts.decorators import custom_login_required

@custom_login_required
def reports_view(request):
    # Lấy dữ liệu từ vw_project_summary
    project_summary = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM vw_project_summary")
        columns = [col[0] for col in cursor.description]
        project_summary = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Lấy dữ liệu từ vw_bug_stats_by_status
    bug_stats = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM vw_bug_stats_by_status")
        columns = [col[0] for col in cursor.description]
        bug_stats = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return render(request, 'bugs/reports.html', {
        'project_summary': project_summary,
        'bug_stats': bug_stats
    })
