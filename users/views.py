from django.urls import reverse
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .gmail_service import send_email
from .models import EmailVerification, PasswordResetToken, User
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

        # create reset token
        reset_token = PasswordResetToken.objects.create(user=user)

        reset_link = request.build_absolute_uri(
            reverse("users:password_reset_verify", args=[reset_token.token])
        )

        # send email via Gmail API
        send_email(
            to=user.email,
            subject="Reset Your Password",
            body=f"Click the link to reset your password: {reset_link}"
        )

        return Response({"detail": "Reset link sent to email"})


class VerifyResetTokenView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return Response({"detail": "Invalid or expired token"}, status=400)

        if reset_token.is_expired():
            reset_token.delete()
            return Response({"detail": "Token expired"}, status=400)

        return Response({"detail": "Token is valid"})


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": "Password has been reset successfully"})