import json
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from .models import Note

def user_to_dict(obj):
    return {
        k: getattr(obj, k)
        for k in obj.__dict__.keys()
        if k in ('id','username', 'is_superuser', 'date_joined')
    }


def index(request):
    return JsonResponse({'message':'Welcome to notes app'})

def not_found(request):
    return JsonResponse({'message':'Oops! You must have wandered deep into the forest, now you are lost'}, status=404)


@csrf_exempt
def login_view(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    if request.method == 'GET':
        return JsonResponse(
            {'message':'This page requires login to access'},
            status=401)
    if user is not None:
        login(request, user)
        return JsonResponse({'message':'Login successful'})
    else:
        return JsonResponse(
            {'message':'Login failed. Invalid username or password'},
            status=401)


@csrf_exempt
def logout_view(request):
    logout(request)
    return JsonResponse({'message':'logout successful'})

@csrf_exempt
def register(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = User(username=username)
    user.set_password(password)
    try:
        user.full_clean()
    except ValidationError as e:
        return JsonResponse({'message':e.message_dict}, status=400)
    else:
        user.save()
    return JsonResponse({'message':'successful'}, status=201)


class UserView(View):
    def get(self, request, user_id=None):
        current_user = request.user
        if current_user.is_superuser and user_id:
            try:
                user = User.objects.get(pk=user_id)
                res = user_to_dict(user)
            except User.DoesNotExist:
                return JsonResponse({'message':'User not found'}, status=404)
        elif current_user.is_superuser and not user_id:
            res = [user_to_dict(u) for u in User.objects.all()]
        elif user_id and not current_user.is_superuser:
            return JsonResponse({'message':'Admin access only'}, status=403)
        else:
            user = User.objects.get(pk=current_user.id)
            res = user_to_dict(user)
        return JsonResponse({'data':res})

    def post(self, request, user_id=None):
        return register(request)

class NoteView(View):
    def get(self, request, note_id=None):
        current_user = request.user
        if note_id:
            try:
                note = Note.objects.get(pk=note_id)
                return JsonResponse({'message':'successful','data':note.to_dict()})
            except Note.DoesNotExist:
                return JsonResponse({'message':'Note not found'}, status=404)
        elif current_user.is_superuser:
            res = list(Note.objects.all())
        else:
            res = list(current_user.notes.all())
        data = [n.to_dict() for n in res]

        return JsonResponse({'message':'successful','data':data})

    def post(self, request, note_id=None):
        current_user = request.user
        title = request.POST.get('title')
        text = request.POST.get('text')
        note = Note(title=title, text=text, author=current_user)
        try:
            note.full_clean()
        except ValidationError as e:
            return JsonResponse({'message':e.message_dict}, status=400)
        else:
            note.save()
        return JsonResponse({'data':note.to_dict(), 'message':'successful'}, status=201)
    
    def put(self, request, note_id):
        request_body = json.loads(request.body)
        title = request_body.get('title')
        text = request_body.get('text')

        current_user = request.user
        try:
            note = current_user.notes.get(id=note_id)
        except Note.DoesNotExist:
            return JsonResponse({'message':'Note not found'}, status=404)
        
        if title:
            note.title = title
        if text:
            note.text = text
        try:
            note.full_clean()
        except ValidationError as e:
            return JsonResponse({'message':e.message_dict}, status=400)
        else:
            note.save()
        return JsonResponse({'data':note.to_dict(), 'message':'successful'})
    
    def delete(self, request, note_id):
        current_user = request.user
        try:
            current_user.notes.get(id=note_id).delete()
            return JsonResponse({'message':'successful'}, status=203)
        except Note.DoesNotExist:
            return JsonResponse({'message':'Note not found'}, status=404)

