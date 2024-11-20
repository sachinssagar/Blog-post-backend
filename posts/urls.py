from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, UserRegistrationViewSet, UserLoginView

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="posts")
router.register(r"register", UserRegistrationViewSet, basename="register")


urlpatterns = [
    path("", include(router.urls)),
    path("login/", UserLoginView.as_view(), name="user-login"),
]
