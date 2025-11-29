from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Role, Permission, Profile, Faculty, Career,
    Course, Section, Enrollment
)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'codename', 'created_at']
    search_fields = ['name', 'codename']
    list_filter = ['created_at']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    search_fields = ['name']
    list_filter = ['is_active', 'created_at']
    filter_horizontal = ['permissions']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'get_profiles_display', 'is_2fa_enabled', 'is_active', 'is_staff']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'is_2fa_enabled']
    search_fields = ['email', 'first_name', 'last_name', 'student_id', 'employee_id']
    ordering = ['-date_joined']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'student_id', 'employee_id')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Two-Factor Authentication', {'fields': ('is_2fa_enabled', 'totp_secret', 'backup_codes')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

    readonly_fields = ['date_joined', 'last_login']

    def get_profiles_display(self, obj):
        """Display all profiles for this user"""
        profiles = obj.profiles.all()
        if not profiles:
            return '-'
        return ', '.join([f"{p.role.name if p.role else 'No role'}" for p in profiles])
    get_profiles_display.short_description = 'Profiles'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'career', 'dni', 'phone', 'is_student', 'is_professor', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at', 'career']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'dni', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'is_student', 'is_professor']

    fieldsets = (
        ('User & Role', {'fields': ('user', 'role', 'is_student', 'is_professor')}),
        ('Academic Information', {'fields': ('career',)}),
        ('Personal Information', {'fields': ('dni', 'phone', 'birth_date', 'address')}),
        ('Professor Information', {'fields': ('specialty', 'academic_title'), 'description': 'Only applicable for professor roles'}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['name', 'dean', 'location', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'dean', 'location']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ['name', 'faculty', 'duration_semesters', 'degree_awarded', 'is_active']
    list_filter = ['faculty', 'is_active', 'created_at']
    search_fields = ['name', 'faculty__name', 'degree_awarded']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'career', 'credits', 'semester_level', 'is_active']
    list_filter = ['career', 'semester_level', 'is_active', 'created_at']
    search_fields = ['code', 'name', 'career__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['code']


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['course', 'code', 'professor', 'academic_period', 'max_capacity', 'enrolled_count', 'is_active']
    list_filter = ['academic_period', 'is_active', 'created_at']
    search_fields = ['course__code', 'course__name', 'code', 'professor__user__first_name', 'professor__user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'enrolled_count', 'available_seats']

    fieldsets = (
        ('Course Information', {'fields': ('course', 'code', 'professor')}),
        ('Scheduling', {'fields': ('academic_period', 'start_date', 'end_date', 'schedule', 'days', 'classroom')}),
        ('Capacity', {'fields': ('max_capacity', 'enrolled_count', 'available_seats')}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'section', 'status', 'enrollment_date', 'grade', 'grade_status', 'cost']
    list_filter = ['status', 'enrollment_date', 'section__academic_period']
    search_fields = [
        'student__user__first_name',
        'student__user__last_name',
        'student__dni',
        'section__course__code',
        'section__course__name'
    ]
    readonly_fields = ['created_at', 'updated_at', 'graded_at', 'is_passed', 'grade_status']

    fieldsets = (
        ('Enrollment Information', {'fields': ('student', 'section', 'enrollment_date', 'status')}),
        ('Payment', {'fields': ('cost', 'payment_method')}),
        ('Grade Information', {'fields': ('grade', 'grade_notes', 'graded_by', 'graded_at', 'is_passed', 'grade_status')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def get_readonly_fields(self, request, obj=None):
        """Make graded_by readonly after it's set"""
        readonly = list(super().get_readonly_fields(request, obj))
        if obj and obj.graded_by:
            readonly.append('graded_by')
        return readonly
