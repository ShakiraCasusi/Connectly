from django.shortcuts import render
from django.http import JsonResponse
from .models import User
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Post
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer
# from django.contrib.auth.models import User

from django.contrib.auth import get_user_model

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from django.contrib.auth.hashers import make_password

from django.contrib.auth import authenticate
from django.http import HttpResponse

from rest_framework.exceptions import PermissionDenied



User = get_user_model()

# Create your views here.

# from django.contrib.auth import authenticate

# def login_view():
#     user = authenticate(username="new_user", password="secure_pass123")
#     if user is not None:
#         print("Authentication successful!")
#     else:
#         print("Invalid credentials.")


# R - Read from CRUD
def get_users(request):
    try:
        users = list(User.objects.values('id', 'username','email', 'created_at'))
        return JsonResponse(users, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
# R - Read SINGLE User from CRUD
def get_user(request, id):
    if request.method == 'GET':
        try:            
            user_id = request.GET.get("id") # added security to avoid SQL injection
            user = User.objects.filter(id=user_id).first()                        
            
            # is_valid = check_password("secure_password123", user.password)            
            # print(is_valid)  # Returns True if the password matches

            # Django verifies user credentials by hashing the entered password and comparing it with the stored hash.
            # Authenticating a user
            user = authenticate(username="john_doe", password="mypassword123")
            if user is not None:
                print("Authentication successful!")
            else:
                print("Invalid credentials.")


            return JsonResponse({'id': user.id, 'username': user.username, 'email': user.email}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


# C - Create from CRUD
@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            #user = User.objects.create(username=data['username'], email=data['email'])
            
            # hashed_password = make_password("secure_password123") 
            # print(hashed_password)  # Outputs a hashed version of the password          

            user = User.objects.create_user(username="new_user", password="secure_pass123")
            print(user.password) # Outputs a hashed password

            return JsonResponse({'id': user.id, 'message': 'User created successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400) 
        
# U - Update from CRUD
@csrf_exempt
def update_user(request, user_id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)           
            user = User.objects.filter(id=user_id).first()            
            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            user.save() # save user back to database
            return JsonResponse({'id': user.id, 'message': 'User updated successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

# D - Delete from CRUD
@csrf_exempt
def delete_user(request, user_id):
    if request.method == 'DELETE':
        try:
            user = User.objects.filter(id=user_id).first()            
            user.delete() # delete user from the database
            return JsonResponse({'message': 'User deleted successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


def get_posts(request):
    try:
        posts = list(Post. objects.values('id', 'content', 'author', 'created_at'))
        return JsonResponse(posts, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def create_post(request):
    # import pdb; pdb.set_trace()  # Add this breakpoint
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            author = User.objects.get(id=data['author'])
            post = Post.objects.create(content=data['content'], author=author)
            return JsonResponse({'id': post.id, 'message': 'Post created successfully'}, status=201)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Author not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


'''                
class UserListCreate(APIView):

    def get(self, request):
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
            
    def post(self, request):

        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')        

        if User.objects.filter(username=username).exists():
            return HttpResponse("Username already exists", status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return HttpResponse("Email already exists", status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            serializer = UserSerializer(data=user)                
            if serializer.is_valid():
                serializer.save()
                return HttpResponse(f"User {user.username} created successfully", status=status.HTTP_201_CREATED)
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=status.HTTP_400_BAD_REQUEST)
'''


class UserListCreate(APIView):

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
            
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # user = User.objects.create_user(username=username, email=email, password=password)
            serializer = UserSerializer(data=request.data)  # Use request.data to validate and save the new user
            if serializer.is_valid():
                serializer.save()
                return Response({"message": f"User {username} created successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class PostListCreate(APIView):
    def get(self, request):
          posts = Post.objects.all()
          serializer = PostSerializer(posts, many=True)
          return Response(serializer.data)
     
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_Request)
    

class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        post = Post.objects.get(pk=pk)
        if post.author != request.user:
            raise PermissionDenied("You are not allowed to access this post.")
        return Response({"content": post.content})


class CommentListCreate(APIView):
    def get(self, request):
          comments = Comment.objects.all()
          serializer = CommentSerializer(comments, many=True)
          return Response(serializer.data)
     
     
    def post(self, request):
        serializer = CommentSerializer(data=request.data)        
        if serializer.is_valid():
             serializer.save()
             return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProtectedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "You are authenticated!"})


class AdminOnlyView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({"message": "Welcome, Admin!"})    


class LoginView(APIView):

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if user is not None:
            return Response({"message": "Authentication successful!"})
        else:
            return Response({"message": f"Invalid credentials for {username} | {password}."}, status=401)            


class LoginViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.login_url = reverse('login')  # Make sure to set the correct URL name for your LoginView

    def test_login_success(self):
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpass123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Authentication successful!')

    def test_login_failure(self):
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Invalid credentials for testuser | wrongpass.')