# slots/models.py
from django.db import models
from django.conf import settings

class Slot(models.Model):
    slot_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='parked_slots'
    )
    will_leave_status = models.BooleanField(default=False)
    # New Field: Triggers a notification if sensors detect movement without permission
    security_alert = models.BooleanField(default=False) 

    def __str__(self):
        return f"Slot {self.slot_number}"