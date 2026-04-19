from django.db import models

class Permission(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'permission'
        managed = False

    def __str__(self):
        return self.title

class Role(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    permissions = models.ManyToManyField(Permission, through='RolePermission')

    class Meta:
        db_table = 'role'
        managed = False

    def __str__(self):
        return self.title

class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'role_permission'
        managed = False

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='primary_users', db_column='role_id')
    
    class Meta:
        db_table = 'user'
        managed = False

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class RoleUser(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='roles_created', db_column='created_by')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='roles_updated', db_column='updated_by')

    class Meta:
        db_table = 'role_user'
        managed = False
