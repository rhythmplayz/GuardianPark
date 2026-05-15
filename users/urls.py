from django.urls import path
from .views import RFIDCheckView, RegisterView, LoginView, SlotLeaveStatusView, UserDashboardSlotStatusView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('rfid-check/', RFIDCheckView.as_view(), name='rfid-check'),
    path('slot-leave-status/<str:slot_number>/', SlotLeaveStatusView.as_view(), name='slot-leave-status'),
   path('dashboard/update-status/', UserDashboardSlotStatusView.as_view(), name='dashboard-update-status'),
]