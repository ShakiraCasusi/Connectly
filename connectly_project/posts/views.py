from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import User, Post
from .serializers import UserSerializer, PostSerializer

# User endpoints
@api_view(['GET'])
def user_list(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def user_create(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"id": serializer.instance.id, "message": "User created successfully"})
    return Response(serializer.errors)

# Post endpoints
@api_view(['GET'])
def post_list(request):
    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def post_create(request):
    data = request.data
    try:
        author = User.objects.get(id=data.get('author'))
    except User.DoesNotExist:
        return Response({"error": "Author not found"}, status=400)
    serializer = PostSerializer(data=data)
    if serializer.is_valid():
        serializer.save(author=author)
        return Response({"id": serializer.instance.id, "message": "Post created successfully"})
    return Response(serializer.errors)

from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to Connectly API. Use /posts/users/ or /posts/posts/")
