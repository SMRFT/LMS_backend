from datetime import datetime
from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import (LibraryUser, Member, Book, NonBookItem, Periodical, BackVolume, 
                    Department, Subject, Circulation, GateLog, Transaction, MemberType)
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .serializers import (LibraryUserSerializer, MemberSerializer, BookSerializer, NonBookItemSerializer,
                          PeriodicalSerializer, BackVolumeSerializer, DepartmentSerializer, 
                          SubjectSerializer, CirculationSerializer, GateLogSerializer, 
                          TransactionSerializer, MemberTypeSerializer)
from .pagination import StandardResultsSetPagination

class LoginView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            return Response({
                'token': 'no-auth-token',
                'user': LibraryUserSerializer(user).data
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        data = request.data
        try:
            user = LibraryUser.objects.create_user(
                username=data.get('username'),
                email=data.get('email', ''),
                password=data.get('password'),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', '')
            )
            
            user.save()
            return Response({'message': 'Staff registered successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LibraryUserViewSet(viewsets.ModelViewSet):
    queryset = LibraryUser.objects.all()
    serializer_class = LibraryUserSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['username', 'first_name', 'last_name']
    filterset_fields = ['is_staff_member']

class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['reg_no', 'first_name', 'last_name']
    filterset_fields = ['department', 'member_type', 'academic_year']
from bson import ObjectId
from django.shortcuts import get_object_or_404

class OptimizedCirculationMixin:
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs[lookup_url_kwarg]
        
        # Try to convert to ObjectId for Djongo compatibility
        if self.lookup_field == 'pk' or self.lookup_field == '_id':
            try:
                if isinstance(lookup_value, str) and len(lookup_value) == 24:
                    obj = queryset.filter(_id=ObjectId(lookup_value)).first()
                    if obj:
                        self.check_object_permissions(self.request, obj)
                        return obj
            except Exception:
                pass
                
        return super().get_object()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        items = page if page is not None else queryset
        
        model_name = self.queryset.model.__name__
        item_type_map = {
            'Book': 'BOOK',
            'NonBookItem': 'NON_BOOK',
            'Periodical': 'PERIODICAL',
            'BackVolume': 'BACK_VOLUME'
        }
        item_type = item_type_map.get(model_name, 'BOOK')
        
        id_field_map = {
            'Book': 'accession_no',
            'NonBookItem': 'non_book_id',
            'Periodical': 'periodical_id',
            'BackVolume': 'volume_id'
        }
        id_field = id_field_map.get(model_name, 'accession_no')
        
        item_ids = [getattr(item, id_field) for item in items if hasattr(item, id_field)]
        
        circulations = Circulation.objects.filter(
            item_id__in=item_ids,
            item_type=item_type,
            type='ISSUE',
            return_date__isnull=True
        ).values('item_id', 'quantity')
        
        issued_counts = {}
        for circ in circulations:
            issued_counts[circ['item_id']] = issued_counts.get(circ['item_id'], 0) + circ['quantity']
            
        serializer = self.get_serializer(items, many=True, context={'issued_counts': issued_counts})
        
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

class BookViewSet(OptimizedCirculationMixin, viewsets.ModelViewSet):
    queryset = Book.objects.select_related('department', 'subject').all()
    serializer_class = BookSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'author', 'accession_no']
    filterset_fields = ['department', 'subject', 'language']

class NonBookItemViewSet(OptimizedCirculationMixin, viewsets.ModelViewSet):
    queryset = NonBookItem.objects.select_related('department', 'subject').all()
    serializer_class = NonBookItemSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'non_book_id']

class PeriodicalViewSet(OptimizedCirculationMixin, viewsets.ModelViewSet):
    queryset = Periodical.objects.select_related('department', 'subject').all()
    serializer_class = PeriodicalSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'periodical_id']

class BackVolumeViewSet(OptimizedCirculationMixin, viewsets.ModelViewSet):
    queryset = BackVolume.objects.all()
    serializer_class = BackVolumeSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'backvolume_id']

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class MemberTypeViewSet(viewsets.ModelViewSet):
    queryset = MemberType.objects.all()
    serializer_class = MemberTypeSerializer

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

class CirculationViewSet(viewsets.ModelViewSet):
    queryset = Circulation.objects.all().order_by('-date')
    serializer_class = CirculationSerializer
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['user', 'item_id', 'type', 'item_type']

    @action(detail=False, methods=['get'])
    def get_details(self, request):
        reg_no = request.query_params.get('reg_no')
        accession_no = request.query_params.get('accession_no')
        
        data = {}
        if reg_no:
            try:
                member = Member.objects.get(reg_no=reg_no)
                data['member'] = MemberSerializer(member).data
            except Member.DoesNotExist:
                data['member'] = None
        
        if accession_no:
            # Search across all item types
            book = Book.objects.filter(accession_no=accession_no).first()
            if book:
                data['item'] = BookSerializer(book).data
                data['item_type'] = 'BOOK'
            else:
                nb = NonBookItem.objects.filter(non_book_id=accession_no).first()
                if nb:
                    data['item'] = NonBookItemSerializer(nb).data
                    data['item_type'] = 'NON_BOOK'
                else:
                    data['item'] = None
        
        return Response(data)

    @action(detail=False, methods=['post'])
    def issue_item(self, request):
        member_id = request.data.get('user') # Frontend sends member ID as 'user'
        item_id = request.data.get('item_id') # Accession No
        item_type = request.data.get('item_type', 'BOOK')
        due_date = request.data.get('due_date')
        qty = int(request.data.get('quantity', 1))
        
        try:
            member = Member.objects.get(_id=member_id)
            if item_type == 'BOOK':
                item = Book.objects.get(accession_no=item_id)
            else:
                item = NonBookItem.objects.get(non_book_id=item_id)
            
            # Check current issued quantity for this specific item record
            current_issued = sum(Circulation.objects.filter(
                item_id=item_id, 
                item_type=item_type, 
                type='ISSUE', 
                return_date__isnull=True
            ).values_list('quantity', flat=True))
            
            if (item.count - current_issued) < qty:
                return Response({'error': f'Not enough stock. Available: {item.count - current_issued}'}, status=400)
            
            circulation = Circulation.objects.create(
                member=member,
                item_id=item_id,
                item_type=item_type,
                type='ISSUE',
                due_date=due_date,
                quantity=qty,
                date=timezone.now()
            )
            
            # Update item is_available flag for legacy compatibility
            if (item.count - current_issued - qty) <= 0:
                item.is_available = False
                item.save()
            
            return Response(CirculationSerializer(circulation).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=False, methods=['post'])
    def return_item(self, request):
        item_id = request.data.get('item_id')
        item_type = request.data.get('item_type', 'BOOK')
        return_date_str = request.data.get('return_date')
        
        # Handle timezone awareness for incoming date string
        if return_date_str:
            try:
                # Convert string to aware datetime
                from django.utils.dateparse import parse_datetime
                from django.utils.timezone import make_aware, is_naive
                dt = parse_datetime(return_date_str)
                if not dt: # Might be just a date string 'YYYY-MM-DD'
                    from django.utils.dateparse import parse_date
                    d = parse_date(return_date_str)
                    if d:
                        dt = datetime.combine(d, datetime.min.time())
                
                if dt and is_naive(dt):
                    return_date = make_aware(dt)
                else:
                    return_date = dt or timezone.now()
            except:
                return_date = timezone.now()
        else:
            return_date = timezone.now()
        
        try:
            if item_type == 'BOOK':
                item = Book.objects.get(accession_no=item_id)
            elif item_type == 'NON_BOOK':
                item = NonBookItem.objects.get(non_book_id=item_id)
            else:
                return Response({'error': f'Invalid item type: {item_type}'}, status=400)
            
            # Find active circulation
            circ = Circulation.objects.filter(item_id=item_id, item_type=item_type, type__in=['ISSUE', 'RENEWAL'], return_date__isnull=True).last()
            
            if not circ:
                return Response({'error': 'No active loan found for this item'}, status=404)
            
            circ.return_date = return_date
            circ.save()
            
            item.is_available = True
            item.save()
            
            return Response({'message': 'Item returned successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=False, methods=['post'])
    def renew_item(self, request):
        item_id = request.data.get('item_id')
        item_type = request.data.get('item_type', 'BOOK')
        new_due_date = request.data.get('due_date')
        
        try:
            # Find active circulation
            circ = Circulation.objects.filter(
                item_id=item_id, 
                item_type=item_type, 
                type__in=['ISSUE', 'RENEWAL'], 
                return_date__isnull=True
            ).last()
            
            if not circ:
                return Response({'error': 'No active loan found to renew'}, status=404)
            
            circ.type = 'RENEWAL'
            if new_due_date:
                circ.due_date = new_due_date
            circ.save()
            
            return Response({'message': 'Item renewed successfully', 'new_due_date': circ.due_date})
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        # Calculate Total Stock from Items
        # Item counts
        total_b = sum(Book.objects.values_list('count', flat=True))
        total_nb = sum(NonBookItem.objects.values_list('count', flat=True))
        
        # Action counters (Lifetime or specific period if needed, but here it's total)
        issues = Circulation.objects.filter(type='ISSUE').count()
        returns = Circulation.objects.filter(type='ISSUE', return_date__isnull=False).count()
        renewals = Circulation.objects.filter(type='RENEWAL').count()
        
        # Currently Out
        issued_b = sum(Circulation.objects.filter(item_type='BOOK', type='ISSUE', return_date__isnull=True).values_list('quantity', flat=True))
        issued_nb = sum(Circulation.objects.filter(item_type='NON_BOOK', type='ISSUE', return_date__isnull=True).values_list('quantity', flat=True))
        
        available_b = total_b - issued_b
        available_nb = total_nb - issued_nb
        
        return Response({
            'books_out': issued_b,
            'books_in': available_b,
            'total_books': total_b,
            'non_books_out': issued_nb,
            'non_books_in': available_nb,
            'total_non_books': total_nb,
            'total_out': issued_b + issued_nb,
            'total_in': available_b + available_nb,
            'total_items': total_b + total_nb,
            'issue_counter': issues,
            'return_counter': returns,
            'renewal_counter': renewals
        })

    @action(detail=False, methods=['get'])
    def report(self, request):
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        item_type = request.query_params.get('item_type')
        
        queryset = self.queryset.filter(type='ISSUE')
        
        if from_date:
            queryset = queryset.filter(date__date__gte=from_date)
        if to_date:
            queryset = queryset.filter(date__date__lte=to_date)
        if item_type:
            queryset = queryset.filter(item_type=item_type)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })

class GateLogViewSet(viewsets.ModelViewSet):
    queryset = GateLog.objects.all().order_by('-in_time')
    serializer_class = GateLogSerializer
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['member']
    
    @action(detail=False, methods=['post'])
    def log_entry(self, request):
        reg_no = request.data.get('reg_no')
        try:
            member = Member.objects.get(reg_no=reg_no)
            log = GateLog.objects.create(member=member)
            return Response(GateLogSerializer(log).data, status=status.HTTP_201_CREATED)
        except Member.DoesNotExist:
            return Response({'error': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def report(self, request):
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        
        queryset = self.queryset
        
        if from_date:
            queryset = queryset.filter(in_time__date__gte=from_date)
        if to_date:
            queryset = queryset.filter(in_time__date__lte=to_date)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by('-date')
    serializer_class = TransactionSerializer
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['member']
