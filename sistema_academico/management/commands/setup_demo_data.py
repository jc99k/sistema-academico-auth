from django.core.management.base import BaseCommand
from sistema_academico.models import Role, Permission, User


class Command(BaseCommand):
    help = 'Setup demo roles, permissions, and users for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Setting up demo data...'))

        # Create Permissions
        self.stdout.write('Creating permissions...')
        permissions_data = [
            {'name': 'View Grades', 'codename': 'view_grades', 'description': 'Can view student grades'},
            {'name': 'Edit Grades', 'codename': 'edit_grades', 'description': 'Can edit student grades'},
            {'name': 'View Courses', 'codename': 'view_courses', 'description': 'Can view courses'},
            {'name': 'Edit Courses', 'codename': 'edit_courses', 'description': 'Can edit courses'},
            {'name': 'Manage Users', 'codename': 'manage_users', 'description': 'Can manage user accounts'},
            {'name': 'View Attendance', 'codename': 'view_attendance', 'description': 'Can view attendance records'},
            {'name': 'Mark Attendance', 'codename': 'mark_attendance', 'description': 'Can mark attendance'},
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
        self.stdout.write('\nCreating roles...')

        # Student Role
        student_role, created = Role.objects.get_or_create(
            name='Student',
            defaults={
                'description': 'Student with limited access to view their own data',
                'is_active': True
            }
        )
        if created:
            student_role.permissions.add(
                permissions['view_grades'],
                permissions['view_courses'],
                permissions['view_attendance']
            )
            self.stdout.write(self.style.SUCCESS('  ✓ Created role: Student'))
        else:
            self.stdout.write('  - Role already exists: Student')

        # Teacher Role
        teacher_role, created = Role.objects.get_or_create(
            name='Teacher',
            defaults={
                'description': 'Teaching staff with grade and attendance management',
                'is_active': True
            }
        )
        if created:
            teacher_role.permissions.add(
                permissions['view_grades'],
                permissions['edit_grades'],
                permissions['view_courses'],
                permissions['view_attendance'],
                permissions['mark_attendance']
            )
            self.stdout.write(self.style.SUCCESS('  ✓ Created role: Teacher'))
        else:
            self.stdout.write('  - Role already exists: Teacher')

        # Administrator Role
        admin_role, created = Role.objects.get_or_create(
            name='Administrator',
            defaults={
                'description': 'Full system administrator with all permissions',
                'is_active': True
            }
        )
        if created:
            admin_role.permissions.set(permissions.values())
            self.stdout.write(self.style.SUCCESS('  ✓ Created role: Administrator'))
        else:
            self.stdout.write('  - Role already exists: Administrator')

        # Academic Coordinator Role
        coordinator_role, created = Role.objects.get_or_create(
            name='Academic Coordinator',
            defaults={
                'description': 'Coordinates courses and manages academic schedules',
                'is_active': True
            }
        )
        if created:
            coordinator_role.permissions.add(
                permissions['view_grades'],
                permissions['view_courses'],
                permissions['edit_courses'],
                permissions['view_attendance']
            )
            self.stdout.write(self.style.SUCCESS('  ✓ Created role: Academic Coordinator'))
        else:
            self.stdout.write('  - Role already exists: Academic Coordinator')

        # Create Demo Users
        self.stdout.write('\nCreating demo users...')

        demo_users = [
            {
                'email': 'student@demo.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'password': 'demo123',
                'role': student_role,
                'student_id': 'STU001'
            },
            {
                'email': 'teacher@demo.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'password': 'demo123',
                'role': teacher_role,
                'employee_id': 'EMP001'
            },
            {
                'email': 'admin@demo.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'password': 'demo123',
                'role': admin_role,
                'employee_id': 'ADM001',
                'is_staff': True
            },
        ]

        for user_data in demo_users:
            email = user_data.pop('email')
            password = user_data.pop('password')

            if User.objects.filter(email=email).exists():
                self.stdout.write(f'  - User already exists: {email}')
            else:
                user = User.objects.create_user(email=email, password=password, **user_data)
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created user: {email} (password: demo123)'))

        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('Demo data setup complete!'))
        self.stdout.write('='*60)
        self.stdout.write('\nDemo users created:')
        self.stdout.write('  • student@demo.com   (password: demo123) - Student role')
        self.stdout.write('  • teacher@demo.com   (password: demo123) - Teacher role')
        self.stdout.write('  • admin@demo.com     (password: demo123) - Administrator role')
        self.stdout.write('\nYou can now login with any of these accounts!')
