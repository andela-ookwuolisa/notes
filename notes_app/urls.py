from django.urls import path, re_path
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path('', views.index),
    re_path(r'^users/(?P<user_id>\d+)?$', login_required(views.UserView.as_view())),
    re_path(r'^notes/(?P<note_id>\d+)?$', login_required(views.NoteView.as_view())),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('register/', views.register),
    # re_path(r'.*', views.not_found),
]
