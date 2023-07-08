from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    # ex: /polls/
    path("", views.index, name="index"),
    # ex: /polls/login/
    path("login/", views.login_view, name="login"),
    # ex: /polls/logout/
    path("logout/", views.register, name="register"),
    # ex: /polls/register/
    path("register/", views.logout_view, name="logout"),
    # ex: /polls/5/ 
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    # ex: /polls/5/results/
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    # ex: /polls/5/vote/
    path("<int:question_id>/vote/", views.vote, name="vote"),
    #ex: /polls/votes/
    path("votes/", views.user_votes, name="votes"),
]
