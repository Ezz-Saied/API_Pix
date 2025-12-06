from django.urls import reverse
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from .models import EmailVerificationOTP, PasswordResetOTP, User
from .serializers import (
    LoginSerializer,
    RequestPasswordResetSerializer,
    SetNewPasswordSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    VerifyEmailOTPSerializer,
)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        otp_code = EmailVerificationOTP.generate_otp()
        
        EmailVerificationOTP.objects.create(user=user, otp=otp_code)

        email_body = f"""
            <h2>Welcome to PixelRevive!</h2>
            <p>Your verification code is:</p>
            <h1 style="color: #4CAF50; letter-spacing: 5px; font-size: 36px;">{otp_code}</h1>
            <p>This OTP will expire in 15 minutes.</p>
            <p>If you didn't create this account, please ignore this email.</p>
            """

        email = EmailMultiAlternatives(
            subject="Verify your PixelRevive email",
            body=f"Your verification code is: {otp_code}",
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email],
        )
        email.attach_alternative(email_body, "text/html")
        email.send()
        
        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Account created. Check your email for the verification code.",
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)







class VerifyEmailView(generics.GenericAPIView):
    serializer_class = VerifyEmailOTPSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response({"message": "Email verified successfully!"})







class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_object(self):
        return self.request.user
    
    
    
    
    


class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        otp_code = PasswordResetOTP.generate_otp()
        
        PasswordResetOTP.objects.create(user=user, otp=otp_code)

        email_body = f"""
        <h2>Password Reset Request</h2>
        <p>Your OTP for password reset is:</p>
        <h1 style="color: #4CAF50; letter-spacing: 5px; font-size: 36px;">{otp_code}</h1>
        <p>This OTP will expire in 15 minutes.</p>
        <p>If you didn't request this, please ignore this email.</p>
        """

        email = EmailMultiAlternatives(
            subject="Your Password Reset OTP",
            body=f"Your OTP is {otp_code}", 
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email],                
        )

        email.attach_alternative(email_body, "text/html")
        email.send()

        return Response({"detail": "OTP sent to your email"})




class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": "Password has been reset successfully"})