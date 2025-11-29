from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import pyotp


class Permission(models.Model):
    """
    Permission model for fine-grained access control.
    Examples: 'view_grades', 'edit_courses', 'manage_users'
    """
    name = models.CharField(max_length=100, unique=True)
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'

    def __str__(self):
        return self.name


class Role(models.Model):
    """
    Role model for grouping permissions.
    Examples: Student, Teacher, Administrator, Academic Coordinator
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    permissions = models.ManyToManyField(
        Permission,
        related_name='roles',
        blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.name

    def add_permission(self, permission):
        """Add a permission to this role"""
        self.permissions.add(permission)

    def remove_permission(self, permission):
        """Remove a permission from this role"""
        self.permissions.remove(permission)

    def has_permission(self, permission_codename):
        """Check if role has a specific permission"""
        return self.permissions.filter(codename=permission_codename).exists()


class UserManager(BaseUserManager):
    """Custom user manager for User model"""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for academic management system with 2FA support.
    A user can have multiple profiles (e.g., be both a student and a professor).
    """
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    # Academic specific fields (kept for backward compatibility, but consider using Profile instead)
    student_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)

    # Two-Factor Authentication fields
    totp_secret = models.CharField(max_length=32, blank=True, null=True)
    is_2fa_enabled = models.BooleanField(default=False)
    backup_codes = models.JSONField(default=list, blank=True)

    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Return the user's short name"""
        return self.first_name

    # 2FA Methods
    def generate_totp_secret(self):
        """Generate a new TOTP secret for 2FA"""
        self.totp_secret = pyotp.random_base32()
        return self.totp_secret

    def get_totp_uri(self):
        """Get the TOTP URI for QR code generation"""
        if not self.totp_secret:
            self.generate_totp_secret()

        return pyotp.totp.TOTP(self.totp_secret).provisioning_uri(
            name=self.email,
            issuer_name='Sistema Academico'
        )

    def verify_totp(self, token):
        """Verify a TOTP token"""
        if not self.totp_secret:
            return False

        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(token, valid_window=1)

    def generate_backup_codes(self, count=10):
        """Generate backup codes for 2FA recovery"""
        import secrets
        codes = [secrets.token_hex(4).upper() for _ in range(count)]
        self.backup_codes = codes
        return codes

    def verify_backup_code(self, code):
        """Verify and consume a backup code"""
        if code.upper() in self.backup_codes:
            self.backup_codes.remove(code.upper())
            self.save(update_fields=['backup_codes'])
            return True
        return False

    def enable_2fa(self):
        """Enable 2FA for this user"""
        if not self.totp_secret:
            self.generate_totp_secret()
        if not self.backup_codes:
            self.generate_backup_codes()
        self.is_2fa_enabled = True
        self.save()

    def disable_2fa(self):
        """Disable 2FA for this user"""
        self.is_2fa_enabled = False
        self.totp_secret = None
        self.backup_codes = []
        self.save()

    # Permission Methods
    def has_role_permission(self, permission_codename, profile=None):
        """
        Check if user has a specific permission through any of their profiles.
        If profile is specified, check only that profile's role.
        """
        if self.is_superuser:
            return True

        # If specific profile provided, check only that profile
        if profile:
            if hasattr(profile, 'role') and profile.role:
                return profile.role.has_permission(permission_codename)
            return False

        # Check all user's profiles
        profiles = self.profiles.all()
        for prof in profiles:
            if prof.role and prof.role.has_permission(permission_codename):
                return True
        return False

    def get_all_permissions_codenames(self, profile=None):
        """
        Get all permission codenames for this user.
        If profile specified, get only that profile's permissions.
        """
        if profile:
            if hasattr(profile, 'role') and profile.role:
                return list(profile.role.permissions.values_list('codename', flat=True))
            return []

        # Get permissions from all profiles
        all_permissions = set()
        profiles = self.profiles.all()
        for prof in profiles:
            if prof.role:
                all_permissions.update(prof.role.permissions.values_list('codename', flat=True))
        return list(all_permissions)

    def get_active_profile(self):
        """
        Get the user's active profile (first available).
        In a real app, you might store this in session or have a flag on Profile.
        """
        return self.profiles.first()

    def get_student_profiles(self):
        """Get all student profiles"""
        return self.profiles.filter(
            role__name__in=Profile.STUDENT_ROLE_TYPES,
            is_active=True
        )

    def get_professor_profiles(self):
        """Get all professor profiles"""
        return self.profiles.filter(
            role__name__in=Profile.PROFESSOR_ROLE_TYPES,
            is_active=True
        )


class Profile(models.Model):
    """
    Profile model to extend User with academic role-specific data.
    A user can have multiple profiles (e.g., both student and professor, or multiple student profiles).
    The role determines the type (student, professor, etc.) and permissions.
    Based on ESTUDIANTE and PROFESOR tables from SQL schema.
    """
    # Student role types for role matching
    STUDENT_ROLE_TYPES = ['Student', 'Undergraduate Student', 'Graduate Student', 'PhD Student', 'PhD Candidate']

    # Professor role types for role matching
    PROFESSOR_ROLE_TYPES = ['Professor', 'Associate Professor', 'Full Professor', 'Teaching Assistant', 'Adjunct Professor', 'Visiting Professor']

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='profiles'
    )

    # Role determines both the type (student/professor) and permissions
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,  # Don't allow deleting roles that are in use
        null=True,  # Allow null for migration purposes
        blank=False,  # But require in forms
        related_name='profiles',
        help_text='Role determines the profile type and permissions'
    )

    # Common fields
    dni = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=200, blank=True, null=True)

    # Professor specific fields
    specialty = models.CharField(max_length=100, blank=True, null=True)
    academic_title = models.CharField(max_length=100, blank=True, null=True)

    # Career tracking for students (optional)
    career = models.ForeignKey(
        'Career',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_profiles',
        help_text='For student profiles, the career they are enrolled in'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['-created_at']

    def __str__(self):
        role_name = self.role.name if self.role else "No Role"
        career_info = f" ({self.career.name})" if self.is_student and self.career else ""
        return f"{self.user.get_full_name()} - {role_name}{career_info}"

    @property
    def is_student(self):
        """Check if this profile is a student type based on role"""
        if not self.role:
            return False
        return self.role.name in self.STUDENT_ROLE_TYPES

    @property
    def is_professor(self):
        """Check if this profile is a professor type based on role"""
        if not self.role:
            return False
        return self.role.name in self.PROFESSOR_ROLE_TYPES

    @property
    def profile_type(self):
        """
        Returns the general profile type for backward compatibility.
        Determines if this is fundamentally a student or professor role.
        """
        if self.is_student:
            return 'student'
        elif self.is_professor:
            return 'professor'
        else:
            return 'other'

    def get_profile_type_display(self):
        """Display the role name"""
        return self.role.name if self.role else "No Role"

    def has_permission(self, permission_codename):
        """Check if this profile's role has a specific permission"""
        if self.role:
            return self.role.has_permission(permission_codename)
        return False

    def get_permissions(self):
        """Get all permissions for this profile"""
        if self.role:
            return self.role.permissions.all()
        return []


class Faculty(models.Model):
    """
    Faculty model (Facultad).
    Represents academic faculties within the university.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    dean = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Faculty'
        verbose_name_plural = 'Faculties'
        ordering = ['name']

    def __str__(self):
        return self.name


class Career(models.Model):
    """
    Career model (Carrera).
    Represents academic programs/majors offered by faculties.
    """
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.RESTRICT,
        related_name='careers'
    )
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    duration_semesters = models.IntegerField()
    degree_awarded = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Career'
        verbose_name_plural = 'Careers'
        ordering = ['name']

    def __str__(self):
        return self.name


class Course(models.Model):
    """
    Course model (Curso).
    Represents courses offered within a career.
    """
    career = models.ForeignKey(
        Career,
        on_delete=models.RESTRICT,
        related_name='courses'
    )
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    credits = models.IntegerField()
    semester_level = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['code']
        constraints = [
            models.CheckConstraint(check=models.Q(credits__gt=0), name='credits_positive'),
            models.CheckConstraint(check=models.Q(semester_level__gt=0), name='semester_level_positive'),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Section(models.Model):
    """
    Section model (Seccion).
    Represents specific class sections of courses taught by professors.
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.RESTRICT,
        related_name='sections'
    )
    professor = models.ForeignKey(
        Profile,
        on_delete=models.RESTRICT,
        related_name='teaching_sections',
        limit_choices_to={'role__name__in': Profile.PROFESSOR_ROLE_TYPES}
    )
    code = models.CharField(max_length=20)
    max_capacity = models.IntegerField()
    classroom = models.CharField(max_length=50, blank=True, null=True)
    schedule = models.CharField(max_length=50, blank=True, null=True)
    days = models.CharField(max_length=50, blank=True, null=True)
    academic_period = models.CharField(max_length=20)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'
        ordering = ['academic_period', 'course__code', 'code']
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'code', 'academic_period'],
                name='unique_section_per_period'
            ),
            models.CheckConstraint(check=models.Q(max_capacity__gt=0), name='max_capacity_positive'),
        ]

    def __str__(self):
        return f"{self.course.code} - Section {self.code} ({self.academic_period})"

    @property
    def enrolled_count(self):
        """Return count of enrolled students"""
        return self.enrollments.filter(status__in=['PENDING', 'PAID', 'COMPLETED']).count()

    @property
    def available_seats(self):
        """Return number of available seats"""
        return self.max_capacity - self.enrolled_count


class Enrollment(models.Model):
    """
    Enrollment model (Matricula).
    Represents student enrollments in course sections with payment and grade tracking.
    """
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    )

    student = models.ForeignKey(
        Profile,
        on_delete=models.RESTRICT,
        related_name='enrollments',
        limit_choices_to={'role__name__in': Profile.STUDENT_ROLE_TYPES}
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.RESTRICT,
        related_name='enrollments'
    )
    enrollment_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, blank=True, null=True)

    # Grade field (based on CALIFICACION table)
    grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Grade from 0 to 20'
    )
    grade_notes = models.TextField(blank=True, null=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_enrollments',
        limit_choices_to={'profile_type': 'professor'}
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        ordering = ['-enrollment_date']
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'section'],
                name='unique_student_section_enrollment'
            ),
            models.CheckConstraint(check=models.Q(cost__gte=0), name='cost_non_negative'),
            models.CheckConstraint(
                check=models.Q(grade__isnull=True) | (models.Q(grade__gte=0) & models.Q(grade__lte=20)),
                name='grade_range_valid'
            ),
        ]

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.section}"

    @property
    def is_passed(self):
        """Check if student passed the course (grade >= 11)"""
        if self.grade is None:
            return None
        return self.grade >= 11

    @property
    def grade_status(self):
        """Return grade status as string"""
        if self.grade is None:
            return 'PENDING'
        elif self.grade >= 11:
            return 'PASSED'
        else:
            return 'FAILED'

    def can_be_viewed_by(self, user):
        """
        Check if a user can view this enrollment.
        Checks across all of the user's profiles.
        """
        if not user or not user.is_authenticated:
            return False

        # Superusers can view everything
        if user.is_superuser:
            return True

        # Check each profile the user has
        for profile in user.profiles.filter(is_active=True):
            # Users with view_all_enrollments permission can view all
            if profile.has_permission('view_all_enrollments'):
                return True

            # Students can view their own enrollments
            if profile.is_student and profile.has_permission('view_own_enrollment'):
                if self.student == profile:
                    return True

            # Professors can view enrollments in their sections
            if profile.is_professor and profile.has_permission('view_section_enrollments'):
                if self.section.professor == profile:
                    return True

        return False

    def can_be_graded_by(self, user, profile=None):
        """
        Check if a user can grade this enrollment.
        If profile is specified, check only that profile.
        Otherwise, check if ANY of the user's professor profiles can grade.
        """
        if not user or not user.is_authenticated:
            return False

        # Superusers can grade everything
        if user.is_superuser:
            return True

        # If specific profile provided, check only that profile
        if profile:
            if not profile.is_professor:
                return False
            if not profile.has_permission('grade_enrollment'):
                return False
            return self.section.professor == profile

        # Check all professor profiles
        for prof in user.profiles.filter(profile_type='professor', is_active=True):
            if prof.has_permission('grade_enrollment'):
                if self.section.professor == prof:
                    return True

        return False

    def set_grade(self, grade_value, user, notes='', profile=None):
        """
        Set grade for this enrollment.
        If profile not specified, finds the appropriate professor profile automatically.
        """
        if grade_value < 0 or grade_value > 20:
            raise ValueError('Grade must be between 0 and 20')

        # If no profile specified, find the professor profile for this section
        if not profile:
            professor_profiles = user.profiles.filter(
                profile_type='professor',
                is_active=True
            )
            for prof in professor_profiles:
                if self.section.professor == prof and prof.has_permission('grade_enrollment'):
                    profile = prof
                    break

        if not profile:
            raise ValueError('No valid professor profile found to grade this enrollment')

        # Final permission check
        if not self.can_be_graded_by(user, profile):
            raise ValueError('You do not have permission to grade this enrollment')

        self.grade = grade_value
        self.grade_notes = notes
        self.graded_at = timezone.now()
        self.graded_by = profile
        self.save()
