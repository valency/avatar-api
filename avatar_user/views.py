import uuid

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from avatar.common import *
from avatar_user.serializers import *


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


@api_view(['POST'])
def login_or_register(request):
    if "username" in request.POST and "password" in request.POST:
        try:
            log("Trying find user with username: " + request.POST["username"])
            Account.objects.get(username=request.POST["username"])
        except ObjectDoesNotExist:
            log("Not found, perform registration...")
            perform_register(request.POST["username"], request.POST["password"])
            log("Successfully registered.")
        log("Logging in...")
        return perform_login(request.POST["username"], request.POST["password"])
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def register(request):
    log("Received registration request.")
    if "username" in request.POST and "password" in request.POST:
        return perform_register(request.POST["username"], request.POST["password"])
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def perform_register(username, password):
    try:
        Account.objects.get(username=username)
        return Response(status=status.HTTP_409_CONFLICT)
    except ObjectDoesNotExist:
        account = Account(username=username, password=password, register_time=datetime.now())
        account.save()
        return Response({"id": account.id})


@api_view(['POST'])
def login(request):
    log("Received login request.")
    if "username" in request.POST and "password" in request.POST:
        return perform_login(request.POST["username"], request.POST["password"])
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def perform_login(username, password):
    try:
        account = Account.objects.get(username=username, password=password)
        account.ticket = str(uuid.uuid4())
        account.last_login = datetime.now()
        account.save()
        return Response({
            "id": account.id,
            "ticket": account.ticket
        })
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def change_password(request):
    if "id" in request.POST and "old" in request.POST and "new" in request.POST:
        try:
            account = Account.objects.get(id=request.POST["id"], password=request.POST["old"])
            account.password = request.POST["new"]
            account.last_update = datetime.now()
            account.ticket = None
            account.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def verify(request):
    if "id" in request.GET and "ticket" in request.GET:
        try:
            Account.objects.get(id=request.GET["id"], ticket=request.GET["ticket"])
            return Response(status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_all_users(request):
    user_id = []
    for user in Account.objects.all():
        user_id.append(user.id)
    return Response(user_id)
