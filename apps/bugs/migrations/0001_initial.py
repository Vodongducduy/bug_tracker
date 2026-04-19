from django.db import migrations

class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[],
            options={'db_table': 'project', 'managed': False},
        ),
        migrations.CreateModel(
            name='Bug',
            fields=[],
            options={'db_table': 'bug', 'managed': False},
        ),
        migrations.CreateModel(
            name='ProjectMember',
            fields=[],
            options={'db_table': 'project_member', 'managed': False},
        ),
        migrations.CreateModel(
            name='AttachmentFile',
            fields=[],
            options={'db_table': 'attachment_file', 'managed': False},
        ),
        migrations.CreateModel(
            name='BugActivityLog',
            fields=[],
            options={'db_table': 'bug_activity_log', 'managed': False},
        ),
    ]
