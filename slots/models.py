# slots/models.py
from django.db import models
from django.conf import settings

class Slot(models.Model):
    # Fixed lowercase 'l'
    slot_number = models.CharField(max_length=50, unique=True)
    
    # Removed the on_index line completely
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='parked_slots'
    )
    
    will_leave_status = models.BooleanField(default=False)

    def __str__(self):
        return f"Slot {self.slot_number} - {'Occupied' if self.user else 'Available'}"