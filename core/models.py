from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from djongo import models as djongo_models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Department(TimeStampedModel):
    _id = models.CharField(max_length=100, primary_key=True, default='')
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class MemberType(TimeStampedModel):
    _id = models.CharField(max_length=100, primary_key=True, default='')
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class Subject(TimeStampedModel):
    _id = models.CharField(max_length=100, primary_key=True, default='')
    name = models.CharField(max_length=200, unique=True)
    def __str__(self):
        return self.name

class LibraryUser(AbstractUser):
    _id = models.CharField(max_length=100, primary_key=True, default='')
    is_staff_member = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Member(TimeStampedModel):
    _id = models.CharField(max_length=100, primary_key=True, default='')
    reg_no = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    member_type = models.ForeignKey(MemberType, on_delete=models.SET_NULL, null=True, blank=True)
    academic_year = models.CharField(max_length=20, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.reg_no} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

class BaseLibraryItem(TimeStampedModel):
    title = models.CharField(max_length=500)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    language = models.CharField(max_length=100, default='English')
    is_available = models.BooleanField(default=True)
    count = models.IntegerField(default=1)

    class Meta:
        abstract = True

class Book(BaseLibraryItem):
    _id = models.CharField(max_length=100, primary_key=True, default='')
    accession_no = models.CharField(max_length=50, unique=True)
    author = models.CharField(max_length=500)
    publisher = models.CharField(max_length=500, null=True, blank=True)
    edition = models.CharField(max_length=100, null=True, blank=True)
    volume = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return f"Book: {self.accession_no} - {self.title}"

class NonBookItem(BaseLibraryItem):
    _id = models.CharField(max_length=100, primary_key=True, default='')
    non_book_id = models.CharField(max_length=50, unique=True)
    item_type = models.CharField(max_length=100) # e.g., CD, DVD, Map
    
    def __str__(self):
        return f"Non-Book: {self.non_book_id} - {self.title}"

class Periodical(BaseLibraryItem):
    _id = models.CharField(max_length=100, primary_key=True, default='')
    periodical_id = models.CharField(max_length=50, unique=True)
    frequency = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"Periodical: {self.periodical_id} - {self.title}"

class BackVolume(BaseLibraryItem):
    _id = models.CharField(max_length=100, primary_key=True, default='')
    backvolume_id = models.CharField(max_length=50, unique=True)
    year = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"BackVolume: {self.backvolume_id} - {self.title}"

class GateLog(TimeStampedModel):
    _id = models.CharField(max_length=100, primary_key=True, default='')
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    in_time = models.DateTimeField(auto_now_add=True)
    out_time = models.DateTimeField(null=True, blank=True)
    
    @property
    def lapsed_time(self):
        if self.out_time:
            return self.out_time - self.in_time
        return None

class Circulation(TimeStampedModel):
    _id = models.CharField(max_length=100, primary_key=True, default='')
    ITEM_TYPES = [
        ('BOOK', 'Book'),
        ('NON_BOOK', 'Non Book'),
        ('PERIODICAL', 'Periodical'),
        ('BACK_VOLUME', 'Back Volume'),
    ]
    CIRCULATION_TYPES = [
        ('ISSUE', 'Issue'),
        ('RETURN', 'Return'),
        ('RENEWAL', 'Renewal'),
    ]
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES, default='BOOK')
    item_id = models.CharField(max_length=50) # The ID of the specific item (accession_no, etc.)
    type = models.CharField(max_length=10, choices=CIRCULATION_TYPES)
    date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)
    quantity = models.IntegerField(default=1)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class Transaction(TimeStampedModel):
    _id = models.CharField(max_length=100, primary_key=True, default='')
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    circulation = models.ForeignKey(Circulation, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transaction_type = models.CharField(max_length=20, choices=[('FINE_PAYMENT', 'Fine Payment'), ('OTHER', 'Other')])
    date = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=200, default='Main Library')
