from rest_framework import viewsets
from .models import Post
from .serializers import PostSerializer, UserRegistrationSerializer, UserLoginSerializer
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action

User = get_user_model()


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["title", "content"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False, methods=["get"], url_path="get-by-slug", url_name="get-by-slug"
    )
    def get_by_slug(self, request):
        slug = request.query_params.get("slug")
        if not slug:
            return Response(
                {"detail": "Slug parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        post = Post.objects.filter(slug=slug).first()
        if not post:
            return Response(
                {"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = PostSerializer(post)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="my-posts", url_name="my-posts")
    def my_posts(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user_posts = Post.objects.filter(author=request.user)
        serializer = PostSerializer(user_posts, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["patch"],
        url_path="update-by-slug",
        url_name="update-by-slug",
    )
    def update_by_slug(self, request):
        slug = request.query_params.get("slug")
        if not slug:
            return Response(
                {"detail": "Slug parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        post = Post.objects.filter(slug=slug).first()
        if not post:
            return Response(
                {"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if post.author != request.user:
            return Response(
                {"detail": "You do not have permission to edit this post"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["delete"],
        url_path="delete-by-slug",
        url_name="delete-by-slug",
    )
    def delete_by_slug(self, request):
        slug = request.query_params.get("slug")

        post = Post.objects.filter(slug=slug).first()
        if not post:
            return Response(
                {"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )

        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserRegistrationViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"user": UserRegistrationSerializer(user).data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False, methods=["patch"], url_path="update-user", url_name="update-user"
    )
    def update_user(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = UserRegistrationSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"user": UserRegistrationSerializer(user).data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")

        try:
            response = super().post(request, *args, **kwargs)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

        response_data = response.data
        user_obj = User.objects.get(username=username)
        response_data["user"] = UserLoginSerializer(
            user_obj, context={"request": request}
        ).data

        return Response(response_data)
