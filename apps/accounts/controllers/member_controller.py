from django.shortcuts import render
from django.db import connection
from apps.accounts.decorators import custom_login_required

@custom_login_required
def member_list_view(request):
    grouped_members = {}
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM vw_project_members ORDER BY project_name, username")
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        for row in rows:
            p_name = row['project_name']
            if p_name not in grouped_members:
                grouped_members[p_name] = []
            grouped_members[p_name].append(row)

    return render(request, 'accounts/member_list.html', {
        'grouped_members': grouped_members
    })
