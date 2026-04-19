from django.db import models
from django.conf import settings
from apps.accounts.models import Role

class Project(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Đang hoạt động'),
        ('CLOSED', 'Đã đóng'),
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='ACTIVE')
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='created_projects', db_column='created_by')
    updated_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='updated_projects', db_column='updated_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project'
        managed = False

    def __str__(self):
        return self.name

class ProjectMember(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='project_memberships')
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    assign_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='members_assigned', db_column='created_by')
    updated_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='members_updated', db_column='updated_by')

    class Meta:
        unique_together = ('project', 'user')
        db_table = 'project_member'
        managed = False

class Bug(models.Model):
    TYPE_CHOICES = (
        ('Functional', 'Functional Bug'),
        ('System', 'System Bug'),
        ('UI', 'UI Bug'),
        ('Performance', 'Performance Bug'),
    )
    STATUS_CHOICES = (
        ('NEW', 'Mới'),
        ('ASSIGNED', 'Đã gán'),
        ('IN_PROGRESS', 'Đang xử lý'),
        ('FIXED', 'Đã sửa'),
        ('CLOSED', 'Đã đóng'),
        ('RE_OPENED', 'Mở lại'),
    )
    PRIORITY_CHOICES = (
        ('S', 'Critical (S)'),
        ('A', 'High (A)'),
        ('B', 'Medium (B)'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='bugs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='NEW')
    priority = models.CharField(max_length=5, choices=PRIORITY_CHOICES)
    root_cause = models.TextField(blank=True, null=True)
    assign_to = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_bugs', db_column='assign_to')
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='reported_bugs', db_column='created_by')
    updated_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='updated_bugs', db_column='updated_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bug'
        managed = False

    def __str__(self):
        return f"#{self.id} - {self.title}"

class AttachmentFile(models.Model):
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE, related_name='attachments')
    file_name = models.CharField(max_length=255)
    file_url = models.URLField(max_length=500)
    file_type = models.CharField(max_length=100, blank=True, null=True)
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, db_column='uploaded_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attachment_file'
        managed = False

class BugActivityLog(models.Model):
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=255)
    performed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, db_column='performed_by')
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'bug_activity_log'
        managed = False

