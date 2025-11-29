from django.core.management.base import BaseCommand
from sistema_academico.models import Permission, Role


class Command(BaseCommand):
    help = 'Set up initial RBAC permissions and roles for the academic system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Setting up RBAC permissions and roles...'))

        # Create Permissions
        permissions_data = [
            {
                'name': 'View Own Enrollment',
                'codename': 'view_own_enrollment',
                'description': 'Can view their own enrollments'
            },
            {
                'name': 'View Section Enrollments',
                'codename': 'view_section_enrollments',
                'description': 'Can view enrollments in their teaching sections'
            },
            {
                'name': 'View All Enrollments',
                'codename': 'view_all_enrollments',
                'description': 'Can view all enrollments in the system'
            },
            {
                'name': 'Grade Enrollment',
                'codename': 'grade_enrollment',
                'description': 'Can grade student enrollments in their sections'
            },
            {
                'name': 'Manage Enrollments',
                'codename': 'manage_enrollments',
                'description': 'Can create, update, and delete enrollments'
            },
            {
                'name': 'Manage Courses',
                'codename': 'manage_courses',
                'description': 'Can create, update, and delete courses'
            },
            {
                'name': 'Manage Sections',
                'codename': 'manage_sections',
                'description': 'Can create, update, and delete sections'
            },
            {
                'name': 'Manage Users',
                'codename': 'manage_users',
                'description': 'Can create, update, and delete users'
            },
        ]

        permissions = {}
        for perm_data in permissions_data:
            perm, created = Permission.objects.get_or_create(
                codename=perm_data['codename'],
                defaults={
                    'name': perm_data['name'],
                    'description': perm_data['description']
                }
            )
            permissions[perm_data['codename']] = perm
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created permission: {perm.name}'))
            else:
                self.stdout.write(f'  - Permission already exists: {perm.name}')

        # Create Roles
        self.stdout.write(self.style.WARNING('\nSetting up roles...'))

        # Student Roles (various types)
        roles_data = [
            # Student Roles
            {
                'name': 'Student',
                'description': 'General student with access to view own enrollments and grades',
                'permissions': ['view_own_enrollment']
            },
            {
                'name': 'Undergraduate Student',
                'description': 'Undergraduate student with basic permissions',
                'permissions': ['view_own_enrollment']
            },
            {
                'name': 'Graduate Student',
                'description': 'Graduate student with additional research permissions',
                'permissions': ['view_own_enrollment']
            },
            {
                'name': 'PhD Student',
                'description': 'PhD student with research and teaching permissions',
                'permissions': ['view_own_enrollment']
            },
            {
                'name': 'PhD Candidate',
                'description': 'PhD candidate with advanced research permissions',
                'permissions': ['view_own_enrollment']
            },

            # Professor Roles
            {
                'name': 'Professor',
                'description': 'Professor with access to view and grade student enrollments in their sections',
                'permissions': ['view_section_enrollments', 'grade_enrollment']
            },
            {
                'name': 'Associate Professor',
                'description': 'Associate Professor with teaching and grading permissions',
                'permissions': ['view_section_enrollments', 'grade_enrollment']
            },
            {
                'name': 'Full Professor',
                'description': 'Full Professor with teaching and grading permissions',
                'permissions': ['view_section_enrollments', 'grade_enrollment']
            },
            {
                'name': 'Teaching Assistant',
                'description': 'Teaching Assistant who can grade but with limited permissions',
                'permissions': ['view_section_enrollments', 'grade_enrollment']
            },
            {
                'name': 'Adjunct Professor',
                'description': 'Adjunct Professor with teaching permissions',
                'permissions': ['view_section_enrollments', 'grade_enrollment']
            },
            {
                'name': 'Visiting Professor',
                'description': 'Visiting Professor with temporary teaching permissions',
                'permissions': ['view_section_enrollments', 'grade_enrollment']
            },

            # Administrative Roles
            {
                'name': 'Academic Coordinator',
                'description': 'Academic coordinator with access to manage courses, sections, and enrollments',
                'permissions': ['view_all_enrollments', 'manage_enrollments', 'manage_courses', 'manage_sections']
            },
            {
                'name': 'Administrator',
                'description': 'Administrator with full access to the system',
                'permissions': list(permissions.keys())  # All permissions
            },
        ]

        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            if created:
                # Add permissions
                for perm_codename in role_data['permissions']:
                    if perm_codename in permissions:
                        role.permissions.add(permissions[perm_codename])
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created role: {role.name}'))
            else:
                self.stdout.write(f'  - Role already exists: {role.name}')

        self.stdout.write(self.style.SUCCESS('\n✓ RBAC setup complete!'))
        self.stdout.write(self.style.WARNING('\nAvailable Student Roles:'))
        self.stdout.write('  - Student (general)')
        self.stdout.write('  - Undergraduate Student')
        self.stdout.write('  - Graduate Student')
        self.stdout.write('  - PhD Student')
        self.stdout.write('  - PhD Candidate')
        self.stdout.write(self.style.WARNING('\nAvailable Professor Roles:'))
        self.stdout.write('  - Professor')
        self.stdout.write('  - Associate Professor')
        self.stdout.write('  - Full Professor')
        self.stdout.write('  - Teaching Assistant')
        self.stdout.write('  - Adjunct Professor')
        self.stdout.write('  - Visiting Professor')
        self.stdout.write(self.style.WARNING('\nAvailable Administrative Roles:'))
        self.stdout.write('  - Academic Coordinator')
        self.stdout.write('  - Administrator')
