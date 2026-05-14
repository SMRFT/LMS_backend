from rest_framework import serializers
from .models import LibraryUser, Member, Book, NonBookItem, Periodical, BackVolume, Department, Subject, Circulation, GateLog, Transaction, MemberType

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class MemberTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberType
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class LibraryUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = LibraryUser
        fields = ('_id', 'username', 'email', 'first_name', 'last_name', 'name', 'is_staff_member')
    
    def get_name(self, obj):
        return obj.get_full_name() or obj.username

class MemberSerializer(serializers.ModelSerializer):
    department = serializers.SlugRelatedField(slug_field='name', queryset=Department.objects.all(), required=False, allow_null=True)
    member_type = serializers.SlugRelatedField(slug_field='name', queryset=MemberType.objects.all(), required=False, allow_null=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    member_type_name = serializers.CharField(source='member_type.name', read_only=True)
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Member
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    department = serializers.SlugRelatedField(slug_field='name', queryset=Department.objects.all(), required=False, allow_null=True)
    subject = serializers.SlugRelatedField(slug_field='name', queryset=Subject.objects.all(), required=False, allow_null=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    issued_count = serializers.SerializerMethodField()
    remaining_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = '__all__'

    def get_issued_count(self, obj):
        if 'issued_counts' in self.context:
            return self.context['issued_counts'].get(obj.accession_no, 0)
        return sum(Circulation.objects.filter(
            item_id=obj.accession_no, 
            item_type='BOOK', 
            type='ISSUE', 
            return_date__isnull=True
        ).values_list('quantity', flat=True))

    def get_remaining_count(self, obj):
        issued = self.get_issued_count(obj)
        return max(0, obj.count - issued)

class NonBookItemSerializer(serializers.ModelSerializer):
    department = serializers.SlugRelatedField(slug_field='name', queryset=Department.objects.all(), required=False, allow_null=True)
    subject = serializers.SlugRelatedField(slug_field='name', queryset=Subject.objects.all(), required=False, allow_null=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    issued_count = serializers.SerializerMethodField()
    remaining_count = serializers.SerializerMethodField()
    
    class Meta:
        model = NonBookItem
        fields = '__all__'

    def get_issued_count(self, obj):
        if 'issued_counts' in self.context:
            return self.context['issued_counts'].get(obj.non_book_id, 0)
        return sum(Circulation.objects.filter(
            item_id=obj.non_book_id, 
            item_type='NON_BOOK', 
            type='ISSUE', 
            return_date__isnull=True
        ).values_list('quantity', flat=True))

    def get_remaining_count(self, obj):
        issued = self.get_issued_count(obj)
        return max(0, obj.count - issued)

class PeriodicalSerializer(serializers.ModelSerializer):
    department = serializers.SlugRelatedField(slug_field='name', queryset=Department.objects.all(), required=False, allow_null=True)
    subject = serializers.SlugRelatedField(slug_field='name', queryset=Subject.objects.all(), required=False, allow_null=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
    class Meta:
        model = Periodical
        fields = '__all__'

class BackVolumeSerializer(serializers.ModelSerializer):
    department = serializers.SlugRelatedField(slug_field='name', queryset=Department.objects.all(), required=False, allow_null=True)
    subject = serializers.SlugRelatedField(slug_field='name', queryset=Subject.objects.all(), required=False, allow_null=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
    class Meta:
        model = BackVolume
        fields = '__all__'

class CirculationSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    member_reg_no = serializers.CharField(source='member.reg_no', read_only=True)
    item_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Circulation
        fields = '__all__'
        
    def get_item_title(self, obj):
        if obj.item_type == 'BOOK':
            item = Book.objects.filter(accession_no=obj.item_id).first()
        elif obj.item_type == 'NON_BOOK':
            item = NonBookItem.objects.filter(non_book_id=obj.item_id).first()
        elif obj.item_type == 'PERIODICAL':
            item = Periodical.objects.filter(periodical_id=obj.item_id).first()
        elif obj.item_type == 'BACK_VOLUME':
            item = BackVolume.objects.filter(backvolume_id=obj.item_id).first()
        else:
            item = None
        return item.title if item else "Unknown Item"

class GateLogSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    reg_no = serializers.CharField(source='member.reg_no', read_only=True)
    lapsed_time = serializers.SerializerMethodField()

    class Meta:
        model = GateLog
        fields = '__all__'
        
    def get_lapsed_time(self, obj):
        return str(obj.lapsed_time) if obj.lapsed_time else None

class TransactionSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = '__all__'
