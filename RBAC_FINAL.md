# Final RBAC Architecture - Role-Only Design

## Evolution of the Design

### ❌ Version 1: Redundant (Role on User + Profile)
- User → Role
- User → Profile (OneToOne)
- **Problem**: Can't be both student and professor

### ❌ Version 2: Still Redundant (Role on Profile + profile_type)
- User → Profiles (Multiple)
- Profile → Role
- Profile → profile_type (enum: student/professor)
- **Problem**: Role and profile_type duplicate the same information

### ✅ Version 3: Clean & Flexible (Role Only)
- User → Profiles (Multiple)
- Profile → Role (determines everything)
- **Benefits**: Single source of truth, maximum flexibility, no redundancy

## Key Architecture Decisions

### Why Remove profile_type?

**The redundancy:**
```python
# Old way (redundant)
profile.profile_type = 'student'  # Enum field
profile.role = Role.objects.get(name='Student')  # Database relation

# These always had to match!
# If profile_type='student', role must be a student role
# If profile_type='professor', role must be a professor role
```

**New way (single source of truth):**
```python
# Just use the role
profile.role = Role.objects.get(name='PhD Student')

# Type is derived from role
profile.is_student  # True (role name in STUDENT_ROLE_TYPES)
profile.is_professor  # False
```

### Role Types

The Profile model now defines two lists that classify roles:

**Student Roles:**
- Student
- Undergraduate Student
- Graduate Student
- PhD Student
- PhD Candidate

**Professor Roles:**
- Professor
- Associate Professor
- Full Professor
- Teaching Assistant
- Adjunct Professor
- Visiting Professor

You can easily add more role types by:
1. Adding them to the `setup_rbac` command
2. Adding them to the appropriate list in Profile model

## Model Structure

### Profile Model (sistema_academico/models.py:258-361)

```python
class Profile(models.Model):
    # Role classification constants
    STUDENT_ROLE_TYPES = ['Student', 'Undergraduate Student', ...]
    PROFESSOR_ROLE_TYPES = ['Professor', 'Associate Professor', ...]

    user = models.ForeignKey(User, related_name='profiles')
    role = models.ForeignKey(Role)  # Single source of truth!

    # Career (for students)
    career = models.ForeignKey('Career', ...)

    # Common fields
    dni, phone, birth_date, address

    # Professor fields
    specialty, academic_title

    # Computed properties
    @property
    def is_student(self):
        return self.role.name in self.STUDENT_ROLE_TYPES

    @property
    def is_professor(self):
        return self.role.name in self.PROFESSOR_ROLE_TYPES

    # Backward compatibility
    @property
    def profile_type(self):
        if self.is_student:
            return 'student'
        elif self.is_professor:
            return 'professor'
        else:
            return 'other'
```

### Benefits of This Approach

1. **No redundancy**: Role is the only field that defines the profile type
2. **Flexible**: Can create any role (Teaching Assistant, Lab Instructor, etc.)
3. **Maintainable**: Add new roles without changing the database schema
4. **Permissions**: Each role has its own permission set
5. **Granular**: Differentiate between "Undergraduate Student" and "PhD Student"

## Available Roles (from setup_rbac)

### Student Roles
All have `view_own_enrollment` permission:
- **Student** - General student
- **Undergraduate Student** - Bachelor's degree student
- **Graduate Student** - Master's degree student
- **PhD Student** - Doctoral student
- **PhD Candidate** - Advanced PhD student

### Professor Roles
All have `view_section_enrollments` and `grade_enrollment` permissions:
- **Professor** - General professor
- **Associate Professor** - Mid-level faculty
- **Full Professor** - Senior faculty
- **Teaching Assistant** - Student who teaches/grades
- **Adjunct Professor** - Part-time faculty
- **Visiting Professor** - Temporary faculty

### Administrative Roles
- **Academic Coordinator** - Manages courses/sections/enrollments
- **Administrator** - Full system access

## Real-World Scenarios

### 1. Teaching Assistant (Student + Professor)
```python
user = User.objects.create(email='ta@university.edu', ...)

# Student profile (taking courses)
Profile.objects.create(
    user=user,
    role=Role.objects.get(name='PhD Student'),
    dni='11111111',
    career=Career.objects.get(name='Computer Science PhD')
)

# Professor profile (teaching/grading)
Profile.objects.create(
    user=user,
    role=Role.objects.get(name='Teaching Assistant'),
    dni='11111112',  # Different DNI
    specialty='Algorithms'
)
```

### 2. Professor Pursuing PhD
```python
user = User.objects.create(email='prof@university.edu', ...)

# Professor profile
Profile.objects.create(
    user=user,
    role=Role.objects.get(name='Associate Professor'),
    dni='22222221',
    specialty='Distributed Systems'
)

# PhD Student profile
Profile.objects.create(
    user=user,
    role=Role.objects.get(name='PhD Student'),
    dni='22222222',
    career=Career.objects.get(name='Computer Science PhD')
)
```

### 3. Different Student Levels
```python
# Undergraduate evolving to Graduate
Profile.objects.create(
    user=user,
    role=Role.objects.get(name='Undergraduate Student'),  # Start here
    ...
)

# Later, change role to Graduate Student
profile.role = Role.objects.get(name='Graduate Student')
profile.save()

# Or create new profile for second degree
Profile.objects.create(
    user=user,
    role=Role.objects.get(name='Graduate Student'),
    career=different_career
)
```

## Setup Instructions

### 1. Run Migrations

```bash
python manage.py migrate
```

This applies migration `0004_remove_profile_type_use_role` which:
- Removes `profile_type` field from Profile
- Updates constraints on Section.professor and Enrollment.student
- Makes role nullable for migration purposes

### 2. Setup RBAC Roles

```bash
python manage.py setup_rbac
```

This creates all 14 roles with their appropriate permissions.

### 3. Create Profiles with Roles

In Django admin:
1. Create User
2. Create Profile:
   - Select User
   - Select Role (e.g., "PhD Student" or "Professor")
   - Fill in DNI and other details
   - For students: Select Career
   - For professors: Fill in Specialty

### 4. Test Permissions

- Login as user with "Student" role → Can only view own enrollments
- Login as user with "Professor" role → Can view and grade section enrollments
- Login as user with both profiles → Sees data from both

## Migration Path from Previous Versions

If you have existing data with `profile_type`:

1. **Before migration**: Your data has profile_type='student' and role='Student'
2. **Run migration**: profile_type field is removed
3. **After migration**: Only role exists, is_student property derives from role

The `is_student` and `is_professor` properties maintain backward compatibility.

## Adding New Role Types

Want to add "Lab Instructor" role?

1. **Add to setup_rbac.py:**
```python
{
    'name': 'Lab Instructor',
    'description': 'Lab instructor with limited teaching permissions',
    'permissions': ['view_section_enrollments', 'grade_enrollment']
},
```

2. **Add to Profile model:**
```python
PROFESSOR_ROLE_TYPES = [
    ...,
    'Lab Instructor'  # Add here
]
```

3. **Run:**
```bash
python manage.py setup_rbac  # Creates the new role
```

That's it! No database migrations needed.

## Advantages Over Previous Designs

| Aspect | Old (profile_type) | New (role only) |
|--------|-------------------|-----------------|
| **Redundancy** | profile_type AND role | role only |
| **Flexibility** | 2 types (student/professor) | Unlimited role types |
| **Permissions** | Generic by type | Specific by role |
| **Maintenance** | Edit model & migrate | Just add role to command |
| **Granularity** | Student vs Professor | PhD Student, TA, Full Prof, etc. |

## FAQ

**Q: What if I want a role that's neither student nor professor?**
A: Just create it! If the role name isn't in STUDENT_ROLE_TYPES or PROFESSOR_ROLE_TYPES, both `is_student` and `is_professor` return False. The `profile_type` property will return 'other'.

**Q: Can I have different permissions for "Student" vs "PhD Student"?**
A: Yes! Each role has its own permission set. Modify `setup_rbac.py` to give different permissions to different student roles.

**Q: How do I restrict sections to only certain professor types?**
A: Update the limit_choices_to in Section.professor:
```python
limit_choices_to={'role__name__in': ['Full Professor', 'Associate Professor']}
```

**Q: What happens to old code that uses profile.profile_type?**
A: It still works! The `profile_type` property is maintained for backward compatibility.

## Summary

The final architecture is clean, flexible, and eliminates all redundancy:
- **Single source of truth**: Role
- **No duplication**: profile_type removed
- **Maximum flexibility**: Any number of role types
- **Easy to extend**: Add roles without migrations
- **Backward compatible**: is_student, is_professor, and profile_type still work

This is the ideal RBAC architecture for academic systems!
