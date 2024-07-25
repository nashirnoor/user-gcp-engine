from rest_framework import generics, permissions, status
from rest_framework.response import Response
from knox.models import AuthToken
from knox.views import LogoutView as KnoxLogoutView
from django.contrib.auth import get_user_model
from .serializers import SignUpSerializer, UserSerializer, UpdateFullNameSerializer
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from django.utils.crypto import get_random_string
from django.http import HttpResponse


User = get_user_model()

class SignUpView(generics.CreateAPIView):
    serializer_class = SignUpSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "User created successfully."
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        otp = get_random_string(6, allowed_chars='0123456789')
        print("Your one time otp is: ",otp)

        cache_key = f'otp_{user.id}'
        cache.set(cache_key, otp, timeout=300) 

        subject = 'Your One-Time Password'
        message = f'Your OTP is: {otp}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list)

        return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)

class VerifyOTPView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        otp = request.data.get('otp')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        cache_key = f'otp_{user.id}'
        stored_otp = cache.get(cache_key)

        if not stored_otp or otp != stored_otp:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        cache.delete(cache_key)

        token = AuthToken.objects.create(user)[1]

        return Response({
            "message": "Login successful",
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token
        }, status=status.HTTP_200_OK)
    

class UpdateFullNameView(generics.UpdateAPIView):
    serializer_class = UpdateFullNameSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "message": "Full name updated successfully",
            "user": serializer.data
        }, status=status.HTTP_200_OK)

class LogoutView(KnoxLogoutView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        super().post(request, format)
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
    

#Just for showing the front-end after deploying
def home(request):
    return HttpResponse("Welcome Python user management This is the home page.")