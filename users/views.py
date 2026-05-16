# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, LoginSerializer
from django.contrib.auth import get_user_model
from slots.models import Slot
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token



User = get_user_model()

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # 1. Generate or fetch the matching database key token
                token, _ = Token.objects.get_or_create(user=user)
                
                # 2. Return the EXACT key 'token' that your frontend line 39 checks for
                return Response({
                    "message": "Login successful!",
                    "token": token.key, 
                    "user": {
                        "username": user.username,
                        "rfid": getattr(user, 'rfid', '')
                    }
                }, status=status.HTTP_200_OK)
                
            return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RFIDCheckView(APIView):
    def post(self, request):
        # Extract the rfid string sent from the hardware/client
        rfid_tag = request.data.get('rfid')

        if not rfid_tag:
            return Response({"error": "RFID tag is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. Check if a user exists with this RFID number
            user = User.objects.get(rfid=rfid_tag)
            
            # 2. Look for the first available parking slot (where user is None)
            available_slot = Slot.objects.filter(user__isnull=True).first()

            if available_slot:
                # 3. Assign the user to this slot
                available_slot.user = user
                available_slot.save()

                # Return the available slot number back to the hardware/display
                return Response({
                    "status": "success",
                    "slot_number": available_slot.slot_number
                }, status=status.HTTP_200_OK)
            else:
                # User exists, but the parking lot is completely full
                return Response({
                    "status": "full",
                    "slot_number": 0,
                    "message": "No available slots left"
                }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            # If user does not exist, return 0 as requested
            return Response({
                    "status": "invalid",
                }, status=status.HTTP_404_NOT_FOUND)
        
class SlotLeaveStatusView(APIView):
    def get(self, request, slot_number):
        try:
            # Look up the slot using the slot number from the URL
            slot = Slot.objects.get(slot_number=slot_number)
            
            # Check the will_leave_status boolean and map to "Yes" or "No"
            status_text = "Yes" if slot.will_leave_status else "No"
            
            slot.user = None
            slot.will_leave_status = False
            slot.save()
            return Response({
                "slot_number": slot_number,
                "will_leave_status": status_text
            }, status=status.HTTP_200_OK)
            
        except Slot.DoesNotExist:
            return Response({
                "error": f"Slot {slot_number} does not exist"
            }, status=status.HTTP_404_NOT_FOUND)


class UserDashboardSlotStatusView(APIView):
    # Enforce that the user must be logged in to access this endpoint
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        # Find the slot assigned to the logged-in user
        try:
            slot = Slot.objects.get(user=request.user)
        except Slot.DoesNotExist:
            return Response({
                "error": "You do not have an active parking slot assigned to your account."
            }, status=status.HTTP_404_NOT_FOUND)

        # Get the new status from the request body
        new_status = request.data.get('will_leave_status')

        if new_status is None or not isinstance(new_status, bool):
            return Response({
                "error": "Please provide a valid boolean value for 'will_leave_status' (true or false)."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update and save the slot status
        slot.will_leave_status = new_status
        slot.save()

        return Response({
            "message": f"Slot {slot.slot_number} status updated successfully.",
            "slot_number": slot.slot_number,
            "will_leave_status": "Yes" if slot.will_leave_status else "No"
        }, status=status.HTTP_200_OK)
    
class UserActiveSlotView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Find the slot assigned to the logged-in user
            slot = Slot.objects.get(user=request.user)
            return Response({
                "has_slot": True,
                "slot_number": slot.slot_number,
                "will_leave_status": slot.will_leave_status,
                "security_alert": slot.security_alert
            }, status=status.HTTP_200_OK)
        except Slot.DoesNotExist:
            return Response({
                "has_slot": False,
                "message": "No active parking slot assigned."
            }, status=status.HTTP_200_OK)

class ClearAlertView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            slot = Slot.objects.get(user=request.user)
            slot.security_alert = False
            slot.save()
            return Response({"message": "Alert cleared."}, status=status.HTTP_200_OK)
        except Slot.DoesNotExist:
            return Response({"error": "No active slot found."}, status=status.HTTP_404_NOT_FOUND)
        

class TriggerAlertView(APIView):
    # Public endpoint or specialized hardware access (No auth token required for the ESP32)
    def post(self, request):
        slot_number = request.data.get('slot_number')
        security_alert = request.data.get('security_alert', False)

        if not slot_number:
            return Response({"error": "Slot number is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            slot = Slot.objects.get(slot_number=slot_number)
            slot.security_alert = security_alert
            slot.save()
            return Response({
                "message": f"Security alert status for Slot {slot_number} updated to {security_alert}.",
                "slot_number": slot_number,
                "security_alert": slot.security_alert
            }, status=status.HTTP_200_OK)
        except Slot.DoesNotExist:
            return Response({"error": f"Slot {slot_number} does not exist."}, status=status.HTTP_404_NOT_FOUND)