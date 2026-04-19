from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[],
            options={
                'db_table': 'user',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[],
            options={'db_table': 'permission', 'managed': False},
        ),
        migrations.CreateModel(
            name='Role',
            fields=[],
            options={'db_table': 'role', 'managed': False},
        ),
        migrations.CreateModel(
            name='RolePermission',
            fields=[],
            options={'db_table': 'role_permission', 'managed': False},
        ),
    ]
