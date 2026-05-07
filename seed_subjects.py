import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_backend.settings')
django.setup()

from core.models import Subject

subjects = [
    "Anatomy", "Anatomyphysiology", "sociology", "psychiatric Nursing", 
    "Medical Surgical Nursing", "surgery", "cardiology", "Medicine", 
    "Nutrition", "Microbiology", "Biochemistry", "Pediatric", 
    "dictionary", "psychology community Health Nursing", "computer", 
    "pharmacology pathology", "OBG", "ophthalmology", "Ent", 
    "othopedics", "Urology", "Bio-statistics", "Gastroenterology", 
    "Midwifery", "Rehabilitation", "Neurology", "Homatology", 
    "dermatogy Tamil", "physiotherapy", "obstetrics", "Education", 
    "General Books"
]

for sub_name in subjects:
    Subject.objects.get_or_create(name=sub_name)
    print(f"Ensured subject: {sub_name}")
