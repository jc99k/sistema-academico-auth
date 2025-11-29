# RBAC Setup Guide for Sistema Academico

This guide explains how to set up and use the Role-Based Access Control (RBAC) system for enrollment management.

## Overview

The system implements RBAC using the existing `Permission` and `Role` models to control access to enrollment data:

- **Students** can view their own enrollments
- **Professors** can view and grade enrollments in their sections only
- **Academic Coordinators** can manage all enrollments, courses, and sections
- **Administrators** have full system access

## Setup Steps

### 1. Run Migrations

First, apply the database migrations to create the new models:

```bash
python manage.py migrate
```

### 2. Set Up RBAC Permissions and Roles

Run the management command to create the initial permissions and roles:

```bash
python manage.py setup_rbac
```

This command creates:

**Permissions:**
- `view_own_enrollment` - View own enrollments
- `view_section_enrollments` - View enrollments in teaching sections
- `view_all_enrollments` - View all enrollments
- `grade_enrollment` - Grade student enrollments
- `manage_enrollments` - Create/update/delete enrollments
- `manage_courses` - Create/update/delete courses
- `manage_sections` - Create/update/delete sections
- `manage_users` - Create/update/delete users

**Roles:**
- **Student** - Can view own enrollments
- **Professor** - Can view and grade enrollments in their sections
- **Academic Coordinator** - Can manage courses, sections, and enrollments
- **Administrator** - Full system access

### 3. Create Test Data

Use Django admin to create test data:

#### A. Create Faculty and Career

1. Go to `/admin/`
2. Create a Faculty (e.g., "Engineering")
3. Create a Career under that Faculty (e.g., "Computer Science", 10 semesters)

#### B. Create Courses

Create some courses (e.g., "CS101 - Introduction to Programming", 4 credits, semester 1)

#### C. Create Users with Profiles

1. **Create a Student User:**
   - Email: `student@test.com`
   - First Name: `John`
   - Last Name: `Doe`
   - Role: `Student`
   - Create a Profile for this user:
     - Profile Type: `Student`
     - DNI: `12345678`

2. **Create a Professor User:**
   - Email: `professor@test.com`
   - First Name: `Jane`
   - Last Name: `Smith`
   - Role: `Professor`
   - Create a Profile for this user:
     - Profile Type: `Professor`
     - DNI: `87654321`
     - Specialty: `Computer Science`

#### D. Create a Section

Create a Section:
- Course: Select your course
- Professor: Select the professor profile
- Code: `A01`
- Max Capacity: `30`
- Academic Period: `2024-1`
- Schedule: `Monday, Wednesday 10:00-12:00`

#### E. Create an Enrollment

Create an Enrollment:
- Student: Select the student profile
- Section: Select the section you created
- Status: `PAID`
- Cost: `500.00`

## Testing the RBAC System

### As a Student

1. Login as `student@test.com`
2. Go to "Enrollments" in the navbar
3. You should see ONLY your own enrollments
4. Click "View" to see enrollment details
5. You should NOT see the "Assign Grade" button

### As a Professor

1. Login as `professor@test.com`
2. Go to "Enrollments" in the navbar
3. You should see ALL enrollments in YOUR sections
4. Click "View" on a student enrollment
5. Click "Assign Grade" button
6. Enter a grade (0-20) and optional notes
7. Submit the grade
8. The student can now see their grade

### Permission Testing

The RBAC system enforces the following rules:

#### Student Permissions
- ✅ Can view their own enrollments
- ✅ Can see their grades
- ❌ Cannot view other students' enrollments
- ❌ Cannot grade enrollments
- ❌ Cannot view enrollments in sections they're not enrolled in

#### Professor Permissions
- ✅ Can view all enrollments in their sections
- ✅ Can grade enrollments in their sections
- ❌ Cannot grade enrollments in other professors' sections
- ❌ Cannot view enrollments in sections they don't teach

## Models Structure

### Profile Model
Extends User with student or professor specific data:
- `user` - OneToOne to User
- `profile_type` - 'student' or 'professor'
- `dni` - Unique identification number
- `phone`, `birth_date`, `address` - Common fields
- `specialty`, `academic_title` - Professor-specific fields

### Faculty Model
Represents academic faculties:
- `name`, `description`, `location`, `dean`

### Career Model
Academic programs offered by faculties:
- `faculty`, `name`, `description`, `duration_semesters`, `degree_awarded`

### Course Model
Courses within careers:
- `career`, `code`, `name`, `description`, `credits`, `semester_level`

### Section Model
Specific class sections taught by professors:
- `course`, `professor` (Profile), `code`, `max_capacity`
- `classroom`, `schedule`, `days`, `academic_period`
- Properties: `enrolled_count`, `available_seats`

### Enrollment Model
Student enrollments with grading:
- `student` (Profile), `section`, `enrollment_date`, `status`, `cost`
- **Grade fields:** `grade`, `grade_notes`, `graded_at`, `graded_by`
- **RBAC Methods:**
  - `can_be_viewed_by(user)` - Checks view permission
  - `can_be_graded_by(user)` - Checks grading permission
  - `set_grade(grade_value, user, notes)` - Sets grade with permission check

## API Endpoints

- `/enrollments/` - List enrollments (filtered by role)
- `/enrollments/<id>/` - View enrollment details
- `/enrollments/<id>/grade/` - Grade an enrollment (professors only)

## Security Features

1. **Permission-based access control** using the Permission model
2. **Role-based filtering** of enrollment lists
3. **Object-level permissions** for viewing and grading
4. **Professor verification** - Only the section's professor can grade
5. **Grade validation** - Grades must be between 0 and 20
6. **Audit trail** - Tracks who graded and when

## Troubleshooting

### "You do not have permission to view enrollments"
- Ensure the user has a Profile
- Ensure the user's Role has appropriate permissions
- Run `python manage.py setup_rbac` if roles/permissions are missing

### "Only the section professor can grade this enrollment"
- Verify the logged-in user is the professor assigned to the section
- Check that the user has the `grade_enrollment` permission

### No enrollments showing up
- Verify you created an Enrollment in the admin
- Check that the enrollment's student/section matches your profile
- Ensure the enrollment status is not 'CANCELLED'

## Next Steps

- Create more test users with different roles
- Test permission boundaries by attempting unauthorized actions
- Add more courses, sections, and enrollments
- Implement enrollment creation from the UI
- Add filtering and search functionality
