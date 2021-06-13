import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.password_validation import validate_password

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED
)
from rest_framework.response import Response


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):

    if request.method == 'POST':

        dicc_request = json.loads(request.body)

        if not("user" in dicc_request) or not("pass" in dicc_request):
            return HttpResponse('missing or insufficient information',
                                status=HTTP_400_BAD_REQUEST)

        username = dicc_request["user"]
        password = dicc_request["pass"]

        user = authenticate(username=username, password=password)

        if not user:
            return HttpResponse('username or password not valid',
                                status=HTTP_401_UNAUTHORIZED)

        token, _ = Token.objects.get_or_create(user=user)
        x = {}
        x['token'] = token.key
        return HttpResponse(json.dumps(x), status=HTTP_200_OK)
    else:
        return HttpResponse('incorrect information', HTTP_400_BAD_REQUEST)


def check_format_username(username):

    specialsym = [' ']

    result = True

    if any(char in specialsym for char in username):
        result = False

    return result


def check_disp_username(username):

    try:
        User.objects.get(username=username)
    except ObjectDoesNotExist:
        return True
    else:
        return False


@csrf_exempt
def register(request):
    if request.method == 'POST':

        dicc_request = json.loads(request.body)

        #username = request.POST.get('user')
        #password = request.POST.get('pass')

        if not("user" in dicc_request) or not("pass" in dicc_request):
            return HttpResponse('missing or insufficient information',
                                status=HTTP_400_BAD_REQUEST)

        else:
            username = dicc_request["user"]
            password = dicc_request["pass"]

            if check_format_username(username):

                if check_disp_username(username):
                    try:
                        validate_password(password, username)
                    except ValidationError:
                        return HttpResponse('no password',
                                            status=HTTP_401_UNAUTHORIZED)
                    else:
                        user = User.objects.create_user(username=username,
                                                        password=password)
                        user.is_staff = True
                        user.save()
                        return HttpResponse('registered', status=HTTP_200_OK)

                else:
                    return HttpResponse('username not available',
                                        status=HTTP_401_UNAUTHORIZED)

            else:
                return HttpResponse('username no valido',
                                    status=HTTP_401_UNAUTHORIZED)
    else:
        return HttpResponse('incorrect information',
                            status=HTTP_400_BAD_REQUEST)


@csrf_exempt
def logout(request):

    return HttpResponse("not", status=404)
