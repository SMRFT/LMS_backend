from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (LibraryUserViewSet, MemberViewSet, BookViewSet, NonBookItemViewSet, 
                    PeriodicalViewSet, BackVolumeViewSet, DepartmentViewSet, 
                    SubjectViewSet, CirculationViewSet, GateLogViewSet, 
                    TransactionViewSet, MemberTypeViewSet, LoginView, RegisterView)

router = DefaultRouter()
router.register(r'staff', LibraryUserViewSet)
router.register(r'members', MemberViewSet)
router.register(r'books', BookViewSet)
router.register(r'nonbooks', NonBookItemViewSet)
router.register(r'periodicals', PeriodicalViewSet)
router.register(r'backvolumes', BackVolumeViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'membertypes', MemberTypeViewSet)
router.register(r'circulation', CirculationViewSet)
router.register(r'gate', GateLogViewSet)
router.register(r'transactions', TransactionViewSet)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('', include(router.urls)),
]
