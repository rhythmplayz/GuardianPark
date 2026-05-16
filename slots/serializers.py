# slots/serializers.py
from rest_framework import serializers
from .models import Slot

class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slot
        fields = ['id', 'slot_number', 'user', 'will_leave_status']
        # We make slot_number read-only so physical bays can't accidentally be renamed via API
        read_only_fields = ['slot_number']