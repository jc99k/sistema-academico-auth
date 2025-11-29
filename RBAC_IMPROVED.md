# Improved RBAC Architecture - Multiple Profiles per User

## Key Improvements

The RBAC system has been refactored to address a critical architectural issue:

### ❌ Old Design (Redundant)
- **Role** attached to **User**
- **Profile** attached to **User** (OneToOne)
- Cannot be both student and professor
- Cannot enroll in second career

### ✅ New Design (Flexible)
- **Role** attached to **Profile**
- **User** can have multiple **Profiles** (ForeignKey)
- Can be student AND professor simultaneously
- Can have multiple student profiles for different careers
- Permissions checked across all active profiles

## Real-World Use Cases

This architecture now supports:

1. **Professor who is also a student**: A professor pursuing a PhD can have:
   - Profile 1: Professor (Computer Science) with "grade_enrollment" permission
   - Profile 2: Student (PhD Program) with "view_own_enrollment" permission

2. **Second career student**: Someone who completed one degree and starts another:
   - Profile 1: Student (Computer Science - graduated, inactive)
   - Profile 2: Student (Business Administration - active)

3. **Part-time professor and student**: Common in universities
   - Profile 1: Student (Master's Program)
   - Profile 2: Professor (Teaching Assistant)

## Architecture Changes

### Profile Model (sistema_academico/models.py:248-328)

```python
class Profile(models.Model):
    user = models.ForeignKey(User, related_name='profiles')  # Changed from OneToOne
    profile_type = models.CharField(choices=[('student', 'Student'), ('professor', 'Professor')])

    # Role moved from User to Profile
    role = models.ForeignKey(Role, ...)

    # New: Career tracking for students
    career = models.ForeignKey('Career', ...)

    # Methods
    def has_permission(self, permission_codename)
    def get_permissions()
```

### User Model Updates (sistema_academico/models.py:197-245)

```python
class User(AbstractBaseUser, PermissionsMixin):
    # Role field removed from here

    # New methods
    def has_role_permission(self, permission_codename, profile=None):
        """Check permission across all profiles or specific profile"""

    def get_all_permissions_codenames(self, profile=None):
        """Get permissions from all or specific profile"""

    def get_active_profile():
        """Get first available profile"""

    def get_profiles_by_type(self, profile_type):
        """Get all student or professor profiles"""
```

### Enrollment RBAC (sistema_academico/models.py:556-645)

```python
class Enrollment(models.Model):
    def can_be_viewed_by(self, user):
        """Check across ALL user's profiles"""
        for profile in user.profiles.filter(is_active=True):
            if profile.has_permission('view_own_enrollment') and self.student == profile:
                return True
            if profile.has_permission('view_section_enrollments') and self.section.professor == profile:
                return True
        return False

    def can_be_graded_by(self, user, profile=None):
        """Check specific or any professor profile"""

    def set_grade(self, grade_value, user, notes='', profile=None):
        """Automatically finds correct professor profile"""
```

## Migration Path

### 1. Run Migration

```bash
python manage.py migrate
```

This migration:
- Removes `role` from User model
- Adds `role` to Profile model
- Changes Profile.user from OneToOne to ForeignKey
- Adds `career` field to Profile

### 2. Data Migration (If Needed)

If you have existing data, you'll need to:
1. Convert OneToOne Profile relationships to ForeignKey
2. Move role assignments from User to Profile
3. Update any code that assumes `user.profile` (singular)

### 3. Update Code References

**Before:**
```python
user.role  # ❌ No longer exists
user.profile  # ❌ No longer works (OneToOne)
```

**After:**
```python
user.profiles.all()  # ✅ Get all profiles
user.get_active_profile()  # ✅ Get first profile
user.has_role_permission('view_own_enrollment')  # ✅ Checks all profiles
```

## Updated Setup Steps

### 1. Run Migrations

```bash
python manage.py migrate
python manage.py setup_rbac
```

### 2. Create Test Users with Multiple Profiles

**Example 1: Professor who is also a PhD student**

1. Create User: `dr.smith@university.edu`
2. Create Profile 1:
   - Type: Professor
   - Role: Professor
   - DNI: 11111111
   - Specialty: Computer Science
3. Create Profile 2:
   - Type: Student
   - Role: Student
   - DNI: 11111112  # Different DNI
   - Career: PhD in Computer Science

**Example 2: Student in two careers**

1. Create User: `john.doe@student.edu`
2. Create Profile 1:
   - Type: Student
   - Role: Student
   - DNI: 22222221
   - Career: Computer Science
   - Active: True
3. Create Profile 2:
   - Type: Student
   - Role: Student
   - DNI: 22222222
   - Career: Business Administration
   - Active: True

## Permission Resolution

When checking permissions, the system:

1. **Checks superuser first**: Superusers bypass all checks
2. **Iterates through active profiles**: Any profile with the permission grants access
3. **Aggregates enrollments**: Shows data from all profiles combined

### Example Permission Check Flow

```python
User: jane.smith@university.edu
Profiles:
  - Professor (has 'grade_enrollment', 'view_section_enrollments')
  - Student (has 'view_own_enrollment')

Action: View enrollments
Result: Shows:
  - Her own enrollments (via Student profile)
  - All enrollments in her sections (via Professor profile)

Action: Grade enrollment in her section
Result: ✅ Allowed (via Professor profile)

Action: Grade enrollment in another professor's section
Result: ❌ Denied (no matching professor profile)
```

## Benefits of This Architecture

1. **Real-world flexibility**: Matches how universities actually work
2. **Data isolation**: Each profile has distinct permissions
3. **Career tracking**: Students can be tracked across multiple programs
4. **Scalability**: Easy to add more profile types (e.g., "administrator", "coordinator")
5. **Audit trail**: Know exactly which profile performed which action
6. **Clean permissions**: Permissions tied to roles, not users

## Admin Interface Changes

- **User list**: Shows all profiles for each user
- **Profile list**: Now shows role and career
- **Create user workflow**: Create user first, then add profiles as needed

## Testing the New System

### Test Case 1: Dual Role User

1. Login as dr.smith@university.edu (professor + student)
2. Go to Enrollments
3. Should see:
   - Own enrollments as a student
   - All enrollments in sections taught as professor
4. On a student's enrollment in your section:
   - Click "View" ✅ (can view via professor profile)
   - Click "Assign Grade" ✅ (can grade via professor profile)
5. On your own enrollment as a student:
   - Click "View" ✅ (can view via student profile)
   - Should NOT see "Assign Grade" button

### Test Case 2: Multiple Student Profiles

1. Login as john.doe@student.edu (CS + Business student)
2. Go to Enrollments
3. Should see enrollments from BOTH careers
4. Each enrollment should show the correct career info

## Troubleshooting

### "User has no attribute 'profile'"
- Update code from `user.profile` to `user.profiles.all()` or `user.get_active_profile()`

### "Profile matching query does not exist"
- User may not have any profiles created yet
- Create at least one profile for the user

### Permissions not working
- Ensure the profile has a role assigned
- Ensure the role has the required permissions
- Check that the profile is `is_active=True`

## Future Enhancements

- **Profile switching UI**: Let users switch between profiles in the navbar
- **Session-based active profile**: Store current profile in session
- **Profile-specific dashboards**: Different UI based on active profile
- **Profile permissions inheritance**: Hierarchical permission structures
- **Time-based profiles**: Automatically activate/deactivate based on dates
