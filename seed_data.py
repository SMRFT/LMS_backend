import os
import django
import sys
from django.utils import timezone

# Add the project path to sys.path
sys.path.append('/Users/parthibanmurugan/Desktop/Live Projects/Libarary management/library_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_backend.settings')
django.setup()

from core.models import (Department, Subject, UserType, LibraryUser, 
                        Book, NonBookItem, Periodical, BackVolume, GateLog)

def seed_data():
    print("Seeding updated library data...")
    
    # Departments
    depts_objs = {}
    depts = ['Anatomy', 'Physiology', 'Sociology', 'Nursing', 'Surgery', 'Medicine']
    for name in depts:
        obj, _ = Department.objects.get_or_create(name=name)
        depts_objs[name] = obj
    
    # User Types
    types = ['Student', 'Faculty', 'Staff', 'Librarian']
    for name in types:
        UserType.objects.get_or_create(name=name)
        
    # Subjects
    sub_objs = {}
    subjects = ['Medical Surgical Nursing', 'Pediatric', 'Biochemistry', 'Microbiology']
    for name in subjects:
        obj, _ = Subject.objects.get_or_create(name=name)
        sub_objs[name] = obj

    # Admin User
    admin, created = LibraryUser.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'reg_no': 'ADM001',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print("Superuser created: admin / admin123")

    # Books
    Book.objects.get_or_create(
        accession_no='BK001',
        defaults={
            'title': 'Essentials of Nursing Practice',
            'author': 'Jane Doe',
            'department': depts_objs['Nursing'],
            'subject': sub_objs['Medical Surgical Nursing'],
            'publisher': 'Health Press',
            'edition': '5th'
        }
    )

    # Non-Books
    NonBookItem.objects.get_or_create(
        non_book_id='NB001',
        defaults={
            'title': 'Anatomy Diagram Poster',
            'item_type': 'Poster',
            'department': depts_objs['Anatomy']
        }
    )

    # Periodicals
    Periodical.objects.get_or_create(
        periodical_id='P001',
        defaults={
            'title': 'The Lancet',
            'frequency': 'Weekly',
            'department': depts_objs['Medicine']
        }
    )

    # Gate Logs
    GateLog.objects.create(user=admin)

    print("Seeding completed successfully!")

if __name__ == '__main__':
    seed_data()
