import json
from unittest.mock import patch

from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from .models import Note
from django.http import JsonResponse


class TestModel(TestCase):
    def setUp(self):
        self.super_user = User(username='super')
        self.super_user.set_password('test123')
        self.super_user.is_superuser = True
        self.super_user.save()

        self.user = User(username='user')
        self.user.set_password('test123')
        self.user.save()

        self.note = Note.objects.create(title='Note title', text='A note text', author=self.user)
    
    def test_note_returns_text_and_title(self):
        note = Note.objects.get(title='Note title')

        self.assertEqual(self.note.title, note.title)
        self.assertEqual(self.note.text, note.text)

    def test_note_updated_at_and_created_at_on_same_day(self):
        created = self.note.created_at
        updated = self.note.updated_at

        self.note.text = 'An updated text'
        self.note.save()

        self.assertEqual(updated, self.note.updated_at)
        self.assertEqual(created, self.note.created_at)
    
    def test_note_returns_serialized_object(self):
        dict_instance = self.note.to_dict()
        self.assertIsInstance(dict_instance, dict)


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()

        self.super_user = User(username='super')
        self.super_user.set_password('test123')
        self.super_user.is_superuser = True
        self.super_user.save()

        self.user = User(username='user')
        self.user.set_password('test123')
        self.user.save()
    
    def login(self):
        auth_cred={'username': 'user', 'password': 'test123'}
        response = self.client.post('/login/', auth_cred)
        return response
    
    def test_index(self):
        response = self.client.get('')
        resp = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(resp['message'], 'Welcome to notes app')
    
    def test_not_found(self):
        response = self.client.get('/invalid')
        self.assertEqual(response.status_code, 404)

    @patch('notes_app.views.login')
    def test_login(self, login):
        response = self.login()
        resp = json.loads(response.content)
        login.assert_called()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(resp['message'], 'Login successful')
    
    def test_invalid_login(self):
        auth_cred={'username': 'user', 'password': 'test12345'}
        response = self.client.post('/login/', auth_cred)
        resp = json.loads(response.content)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(resp['message'], 'Login failed. Invalid username or password')

    @patch('notes_app.views.logout')
    def test_logout(self, logout):
        response = self.client.get('/logout/')
        resp = json.loads(response.content)
        logout.assert_called()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(resp['message'], 'logout successful')

    @patch('notes_app.views.User')
    def test_register_user_with_valid_details(self, User):
        user = User()
        user_details={'username': 'new_user', 'password': 'test123'}
        response = self.client.post('/register/', user_details)
        resp = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(resp['message'], 'successful')
        user.save.assert_called()

    def test_register_user_with_invalid_details(self):
        user_details={'username': 'user', 'password': 'test1234'}
        response = self.client.post('/register/', user_details)
        resp = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(resp['message'], {'username': ['A user with that username already exists.']})

class TestUserView(TestCase):
    def setUp(self):
        self.client = Client()

        self.super_user = User(username='super')
        self.super_user.set_password('test123')
        self.super_user.is_superuser = True
        self.super_user.save()

        self.user = User(username='user')
        self.user.set_password('test123')
        self.user.save()
    
    def login(self):
        auth_cred={'username': 'user', 'password': 'test123'}
        response = self.client.post('/login/', auth_cred)
        return response
    
    def super_login(self):
        auth_cred={'username': 'super', 'password': 'test123'}
        response = self.client.post('/login/', auth_cred)
        return response


    def test_get_returns_user_object(self):
        self.login()
        response = self.client.get('/users/')
        resp = json.loads(response.content)
        self.assertEqual(resp['data']['username'], 'user')
        self.assertEqual(response.status_code, 200)
    
    def test_get_returns_users_list_for_superusers(self):
        self.super_login()
        response = self.client.get('/users/')
        resp = json.loads(response.content)
        self.assertEqual(len(resp['data']), 2)
        self.assertEqual(resp['data'][1]['username'], 'user')
        self.assertEqual(response.status_code, 200)
    
    def test_get_returns_any_user_for_superusers(self):
        self.super_login()
        response = self.client.get('/users/2')
        resp = json.loads(response.content)
        self.assertEqual(resp['data']['username'], 'user')
        self.assertEqual(response.status_code, 200)
    
    def test_get_does_not_return_any_user_for_non_superusers(self):
        self.login()
        response = self.client.get('/users/2')
        self.assertEqual(response.status_code, 403)
    
    @patch('notes_app.views.register')
    def test_post(self, register):
        self.login()
        register.return_value = JsonResponse({})
        response = self.client.post('/users/')
        register.assert_called()


class TestNoteView(TestCase):
    def setUp(self):
        self.client = Client()

        self.super_user = User(username='super')
        self.super_user.set_password('test123')
        self.super_user.is_superuser = True
        self.super_user.save()

        self.user = User(username='user')
        self.user.set_password('test123')
        self.user.save()

        self.note = Note.objects.create(title='Note title', text='A note text', author=self.user)

    def login(self):
        auth_cred={'username': 'user', 'password': 'test123'}
        response = self.client.post('/login/', auth_cred)
        return response
    
    def super_login(self):
        auth_cred={'username': 'super', 'password': 'test123'}
        response = self.client.post('/login/', auth_cred)
        return response

    def test_get_returns_notes(self):
        self.login()
        response = self.client.get('/notes/')
        resp = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(resp['data'][0]['title'], self.note.title)
    
    def test_returns_302_for_unauthenticated_user(self):
        response = self.client.get('/notes/')
        self.assertEqual(response.status_code, 302)
    
    def test_post_creates_notes(self):
        self.login()
        note = {'title':'new note', 'text':'the content'}
        response = self.client.post('/notes/', note)
        resp = json.loads(response.content)
        self.assertEqual(resp['data']['title'], 'new note')
    
    def test_post_returns_error_for_invalid_input(self):
        self.login()
        note = {'text':'the content'}
        response = self.client.post('/notes/', note)
        self.assertEqual(response.status_code, 400)
    
    def test_put_updates_note_content(self):
        self.login()
        note = Note.objects.get()
        data = {'title': 'a new title'}
        response = self.client.put(f'/notes/{note.id}', data, content_type = 'application/json')
        resp = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(resp['data']['title'], 'a new title')

    def test_put_returns_404_for_non_owners(self):
        self.super_login()
        note = Note.objects.get()
        data = {'title': 'a new title'}
        response = self.client.put(f'/notes/{note.id}', data, content_type = 'application/json')
        resp = json.loads(response.content)
        self.assertEqual(response.status_code, 404)
    
    def test_delete_notes(self):
        self.login()
        note = Note.objects.get()
        response = self.client.delete(f'/notes/{note.id}')
        self.assertEqual(response.status_code, 203)
    
    def test_delete_returns_404_for_non_owner(self):
        self.super_login()
        note = Note.objects.get()
        response = self.client.delete(f'/notes/{note.id}')
        self.assertEqual(response.status_code, 404)
        
