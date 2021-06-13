import json
from django.test import TestCase
from logueo.views import *
from django.test.client import RequestFactory
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User


# Using the standard RequestFactory API to create a form POST request


class loginTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        User.objects.create_user(username="ivi", password="ivi")

    def test_1login_correct_login(self):
        data = {"user": "ivi", "pass": "ivi"}
        json_data = json.dumps(data)
        request = self.factory.post(
            '/users/login/', content_type='aplication/json', data=json_data)
        response = login(request)
        self.assertEqual(response.status_code, 200)

    def test_2login_Invalid_request_information(self):
        data = {"user": "ivi", "noPass": "ivi"}
        json_data = json.dumps(data)
        request = self.factory.post(
            '/users/login/', content_type='aplication/json', data=json_data)
        response = login(request)
        self.assertEqual(response.status_code, 400)

    def test_3login_username_or_password_does_not_belong_to_any_user(self):
        data = {"user": "ivi", "pass": "Nopass"}
        json_data = json.dumps(data)
        request = self.factory.post(
            '/users/login/', content_type='aplication/json', data=json_data)
        response = login(request)
        self.assertEqual(response.status_code, 401)

    def test_4login_session_in_the_database(self):
        data = {"user": "ivi", "pass": "ivi"}
        json_data = json.dumps(data)
        request = self.factory.post(
            '/users/login/', content_type='aplication/json', data=json_data)
        check = User.objects.get(username="ivi")
        self.assertIsNotNone(check)


class registerTestCase(TestCase):
    def setUp(self):
        User.objects.create_user(username="usCreate", password="paUsed")
        self.factory = APIRequestFactory()

    def test_1register_correct_register(self):
        data = {"user": "ivi", "pass": "Turing000"}
        json_data = json.dumps(data)
        request = self.factory.post(
            '/users/', content_type='aplication/json', data=json_data)
        response = register(request)
        self.assertEqual(response.status_code, 200)

    def test_2register_username_not_available(self):
        data = {"user": "usCreate", "pass": "OtherPass"}
        json_data = json.dumps(data)
        request = self.factory.post(
            '/users/', content_type='aplication/json', data=json_data)
        response = register(request)
        self.assertEqual(response.status_code, 401)

    def test_3register_missing_information(self):
        data = {"user": "usCreate", "fail": "paUsed"}
        json_data = json.dumps(data)
        request = self.factory.post(
            '/users/', content_type='aplication/json', data=json_data)
        response = login(request)
        self.assertEqual(response.status_code, 400)

    def test_4register_user_in_the_database(self):

        check = User.objects.get(username="usCreate")
        self.assertIsNotNone(check)
