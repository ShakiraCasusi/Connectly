from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from .models import User, Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer
from .permissions import IsPostAuthor, IsAdmin
from singletons.logger_singleton import LoggerSingleton
from factories.post_factory import PostFactory

logger = LoggerSingleton().get_logger()

# -------------------------
# User Views
# -------------------------
class UserListCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"User list accessed by: {request.user.username}")
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        logger.info(f"User creation attempted by: {request.user.username}")

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("User created successfully.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        logger.warning(f"User creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -------------------------
# Post Views
# -------------------------
class PostListCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"Posts retrieved by: {request.user.username}")
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            logger.warning("Unauthorized post creation attempt.")
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=401
            )
        
        data = request.data
        logger.info(f"Post creation attempted by: {request.user.username}")

        try:
            post = PostFactory.create_post(
                post_type=data.get("post_type"),
                title=data.get("content", ""),
                metadata=data.get("metadata", {})
            )

            post.author = request.user
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

# -------------------------
# Comment Views
# -------------------------
class CommentListCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"Comment retrieved by: {request.user.username}")
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            logger.warning("Unauthorized comment creation attempt.")
            return Response(
                {"detail": "Authentication credentials were not provided."}, 
                status=401
            )
    
        logger.info(f"Comment creation attempted by: {request.user.username}")

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            logger.info("Comment created successfully.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        logger.warning(f"Comment creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
