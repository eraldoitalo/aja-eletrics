from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User


class NewUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role']


class ChangeUserForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class AccountAdmin(UserAdmin):
    form = ChangeUserForm
    add_form = NewUserForm
    list_display = ['email', 'first_name', 'role', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']
    fieldsets = [
        (None, {'fields': ['email', 'password']}),
        ('Perfil', {'fields': ['first_name', 'last_name', 'role', 'is_active']}),
        ('Administração técnica', {'fields': ['is_staff', 'is_superuser', 'groups', 'user_permissions']}),
    ]
    add_fieldsets = [(None, {'classes': ['wide'], 'fields': ['email', 'first_name', 'last_name', 'role', 'password1', 'password2']})]
    def has_module_permission(self, request):
        return request.user.is_superuser
    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser
    has_add_permission = has_view_permission
    has_change_permission = has_view_permission
    has_delete_permission = has_view_permission


admin.site.site_header = 'AJA · Administração de usuários'
admin.site.site_title = 'AJA Eletrics'
