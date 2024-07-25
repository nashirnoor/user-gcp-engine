from django.urls import path
from .views import SignUpView, LoginView, VerifyOTPView, UpdateFullNameView,LogoutView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('update-fullname/', UpdateFullNameView.as_view(), name='update-fullname'),
    path('logout/', LogoutView.as_view(), name='logout'),

]