from django.urls import reverse
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .gmail_service import send_email
from .models import EmailVerification, PasswordResetOTP,User
from .serializers import (
    LoginSerializer,
    RequestPasswordResetSerializer,
    SetNewPasswordSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # create email verification record
        verify_obj = EmailVerification.objects.create(user=user)
        verification_link = request.build_absolute_uri(
            reverse("users:verify", args=[verify_obj.token])
        )

        # send email
        body = f"""
            <h2>Welcome to PixelRevive!</h2>
            <p>Click the link below to verify your account:</p>
            <a href="{verification_link}" style="padding:10px;background:#4CAF50;color:white;text-decoration:none;">Verify Email</a>
            """

        try:
            send_email(user.email, 'Verify your PixelRevive email', body, html=True)
        except Exception as e:
            print(f"Email send failed: {e}")
        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Account created. Check your email to verify your account.",
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

    def get(self, request, token):
        try:
            verify_obj = EmailVerification.objects.get(token=token)
            
            # Check if token is expired
            if verify_obj.expires_at < timezone.now():
                return Response({"error": "Verification link expired"}, status=400)
            
            user = verify_obj.user
            user.is_verified = True
            user.save()
            verify_obj.delete()

            return Response({"message": "Email verified successfully!"})
        
        except EmailVerification.DoesNotExist:
            return Response({"error": "Invalid or expired verification link"}, status=400)







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

        # Generate OTP
        otp_code = PasswordResetOTP.generate_otp()
        
        # Create OTP record
        PasswordResetOTP.objects.create(user=user, otp=otp_code)

        # Send OTP via email
        email_body = f"""
        <h2>Password Reset Request</h2>
        <p>Your OTP for password reset is:</p>
        <h1 style="color: #4CAF50; letter-spacing: 5px; font-size: 36px;">{otp_code}</h1>
        <p>This OTP will expire in 15 minutes.</p>
        <p>If you didn't request this, please ignore this email.</p>
        """

        send_email(
            to=user.email,
            subject="Your Password Reset OTP",
            body=email_body,
            html=True
        )

        return Response({"detail": "OTP sent to your email"})




class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": "Password has been reset successfully"})