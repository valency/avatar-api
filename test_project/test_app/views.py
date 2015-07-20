import base64
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication, TokenAuthentication
from django.contrib.auth.signals import user_logged_in, user_logged_out
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.views.decorators.csrf import csrf_exempt, requires_csrf_token

from rest_framework import HTTP_HEADER_ENCODING
from rest_framework.views import APIView


def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, type('')):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


@api_view(["POST", "GET"])
def create_user_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
    if request.method == 'GET':
        username = request.GET['username']
        email = request.GET['email']
        password = request.GET['password']
    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()
    return Response({'detail': "Create user"})


@api_view(["POST", "GET"])
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', 'not filled')
        password = request.POST.get('password', 'not filled')
    if request.method == 'GET':
        username = request.GET['username']
        password = request.GET['password']
    user = authenticate(username=username, password=password)
    if user is not None:
         # rotate_token(request)
        user_logged_in.send(sender=user.__class__, request=request, user=user)
        token = Token.objects.get_or_create(user=user)
        return Response({'detail': 'POST answer', 'token': token[0].key, })
    else:
        # the authentication system was unable to verify the username and password
        return Response({'detail': "The username or password were incorrect.",
                        status: status.HTTP_404_NOT_FOUND})

@api_view(["POST", "GET"])
def change_password_view(request):
    user=request.user
    if request.method == 'POST':
        old_password = request.POST.get('old_password', 'not filled')
        new_password = request.POST.get('new_password', 'not filled')
    if request.method == 'GET':
        old_password = request.GET['old_password']
        new_password = request.GET['new_password']
    if not user.check_password(old_password):
        return Response({'detail': "Old password does not match."})
    else:
        user.set_password(new_password)
        user.save()
        return Response({'detail': "password set."})


@api_view(["POST"])
def logout_view(request):
        user = getattr(request, 'username', None)
        if hasattr(user, 'is_authenticated') and not user.is_authenticated():
            user = None
            user_logged_out.send(sender=user.__class__, request=request, user=user)
        if hasattr(request, 'username'):
            from django.contrib.auth.models import AnonymousUser
            request.user = AnonymousUser()
        return Response({'detail': "You have logged out successfully."})


class AuthView(APIView):
    """
    Authentication is needed for this methods
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        return Response({'detail': "I suppose you are authenticated"})
