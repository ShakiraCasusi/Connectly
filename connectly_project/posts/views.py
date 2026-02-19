from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from .models import User, Post, Comment, Like
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    PostSerializer,
    CommentSerializer,
    PostCommentCreateSerializer,
    PostCommentSerializer,
    LikeSerializer,
)
from .permissions import IsPostAuthor, IsAdmin
from singletons.logger_singleton import LoggerSingleton
from factories.post_factory import PostFactory

logger = LoggerSingleton().get_logger()


def _error(message, http_status):
    return Response({"error": message}, status=http_status)


def _get_domain_user(request):
    """
    Maps the authenticated user (from DRF's TokenAuthentication) to the application's
    domain user (`posts.User`).

    If the domain user profile does not exist, it is created on-the-fly. This makes
    the system resilient to users being created via methods that bypass the main
    user creation endpoint (e.g., `manage.py createsuperuser`).
    """
    if isinstance(request.user, User):
        return request.user

    username = getattr(request.user, "username", None)
    if not username:
        return None

    domain_user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': getattr(request.user, 'email', '')}
    )
    if created:
        logger.info(f"Auto-created missing domain profile for user: {username}")
    return domain_user



# Test/Debug Endpoint

class TestAuth(APIView):
    """
    Test endpoint to verify authentication is working.
    Use this to debug authentication issues.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Test GET with authentication"""
        return Response({
            "status": "authenticated",
            "user": {
                "id": request.user.id,
                "username": request.user.username,
                "is_authenticated": request.user.is_authenticated,
            },
            "auth_header_received": request.META.get('HTTP_AUTHORIZATION', 'Not found'),
            "message": "If you see this, authentication is working!"
        })

    def post(self, request):
        """Test POST with authentication"""
        return Response({
            "status": "authenticated",
            "user": {
                "id": request.user.id,
                "username": request.user.username,
            },
            "data_received": request.data,
            "message": "POST authentication is working!"
        })



# User Views

class UserListCreate(APIView):
    """
    User creation (POST) is public (no auth required).
    User listing (GET) requires authentication.
    """
    authentication_classes = [TokenAuthentication]
    
    def get_permissions(self):
        """
        Allow unauthenticated POST (user registration).
        Require authentication for GET (list users).
        """
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        logger.info(f"User list accessed by: {request.user.username}")
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        # POST doesn't require authentication (public registration)
        logger.info(f"User creation attempted (username: {request.data.get('username', 'unknown')})")

        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            domain_user = serializer.save()
            logger.info("User created successfully (auth + domain profile).")
            return Response(UserSerializer(domain_user).data, status=status.HTTP_201_CREATED)
        
        logger.warning(f"User creation failed: {serializer.errors}")
        # Normalize to the project's consistent {"error": "..."} format where possible
        if isinstance(serializer.errors, dict) and "error" in serializer.errors:
            err = serializer.errors["error"]
            if isinstance(err, list) and err:
                return _error(str(err[0]), status.HTTP_400_BAD_REQUEST)
            return _error(str(err), status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Post Views

class PostListCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # DRF's IsAuthenticated ensures user is authenticated at this point
        username = getattr(request.user, 'username', 'unknown')
        logger.info(f"Posts retrieved by: {username}")
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        # DRF's IsAuthenticated permission already handles auth check
        # This method only runs if user is authenticated
        data = request.data
        username = getattr(request.user, 'username', 'unknown')
        logger.info(f"Post creation attempted by: {username}")

        try:
            post = PostFactory.create_post(
                post_type=data.get("post_type"),
                title=data.get("content", ""),
                metadata=data.get("metadata", {})
            )

            domain_user = _get_domain_user(request)
            if not domain_user:
                logger.warning("Authenticated user has no domain profile (posts.User).")
                return _error("User profile not found", status.HTTP_400_BAD_REQUEST)

            post.author = domain_user
            post.save()

            logger.info("Post created successfully via factory.")
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            logger.warning(f"Post creation failed: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
        )
        

class PostDetail(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsPostAuthor]

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)

        logger.info(f"Post {pk} viewed by: {request.user.username}")

        serializer = PostSerializer(post)
        return Response(serializer.data)

    def put(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)

        logger.info(f"Post {pk} updated attempted by: {request.user.username}")

        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Post {pk} update successfully.")
            return Response(serializer.data)
        
        logger.warning(f"Post {pk} update failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)

        logger.info(f"Post {pk} deleted by: {request.user.username}")
        post.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


# Comment Views

class CommentListCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"Comment retrieved by: {request.user.username}")
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        # The `permission_classes = [IsAuthenticated]` on the class already ensures the user is authenticated.
        # If the check fails, DRF returns a 401 response before this method is called.
        logger.info(f"Comment creation attempted by: {request.user.username}")
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            domain_user = _get_domain_user(request)
            if not domain_user:
                logger.warning("Authenticated user has no domain profile (posts.User).")
                return _error("User profile not found", status.HTTP_400_BAD_REQUEST)

            serializer.save(author=domain_user)
            logger.info("Comment created successfully.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        logger.warning(f"Comment creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Like + Post-Scoped Comments

class PostLike(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        post = Post.objects.filter(pk=pk).first()
        if not post:
            return _error("Post not found", status.HTTP_404_NOT_FOUND)

        domain_user = _get_domain_user(request)
        if not domain_user:
            return _error("User profile not found", status.HTTP_400_BAD_REQUEST)

        if Like.objects.filter(user=domain_user, post=post).exists():
            return _error("Post already liked", status.HTTP_400_BAD_REQUEST)

        like = Like.objects.create(user=domain_user, post=post)
        return Response(LikeSerializer(like).data, status=status.HTTP_201_CREATED)


class PostCommentCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        post = Post.objects.filter(pk=pk).first()
        if not post:
            return _error("Post not found", status.HTTP_404_NOT_FOUND)

        domain_user = _get_domain_user(request)
        if not domain_user:
            return _error("User profile not found", status.HTTP_400_BAD_REQUEST)

        serializer = PostCommentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            # Enforce consistent error response format
            content_errs = serializer.errors.get("content") if isinstance(serializer.errors, dict) else None
            if isinstance(content_errs, list) and content_errs:
                return _error(str(content_errs[0]), status.HTTP_400_BAD_REQUEST)
            return _error("Invalid request body", status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(
            post=post,
            author=domain_user,
            text=serializer.validated_data["content"],
        )
        return Response(PostCommentSerializer(comment).data, status=status.HTTP_201_CREATED)


class PostCommentList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        post = Post.objects.filter(pk=pk).first()
        if not post:
            return _error("Post not found", status.HTTP_404_NOT_FOUND)

        qs = Comment.objects.filter(post=post).order_by("-created_at")

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginator.page_size_query_param = "page_size"
        paginator.max_page_size = 100

        page = paginator.paginate_queryset(qs, request, view=self)
        serializer = PostCommentSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
