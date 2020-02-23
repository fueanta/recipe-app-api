from django.urls import path

from user import views


app_name = 'user'

urlpatterns = [
    path(
        route='create/',
        view=views.CreateUserView.as_view(),
        name='create',
    ),
    path(
        route='token/',
        view=views.CreateTokenView.as_view(),
        name='token',
    ),
]
