from django.urls import path
from .views import ClearAlertView, RFIDCheckView, RegisterView, LoginView, SlotLeaveStatusView, UserActiveSlotView, UserDashboardSlotStatusView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('rfid-check/', RFIDCheckView.as_view(), name='rfid-check'),
    path('slot-leave-status/<str:slot_number>/', SlotLeaveStatusView.as_view(), name='slot-leave-status'),
    path('dashboard/update-status/', UserDashboardSlotStatusView.as_view(), name='dashboard-update-status'),
    path('dashboard/active-slot/', UserActiveSlotView.as_view(), name='active-slot'),
    path('dashboard/clear-alert/', ClearAlertView.as_view(), name='clear-alert'),
]