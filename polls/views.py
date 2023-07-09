from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
import traceback

from .models import Account, Choice, Question, Vote

# Create your views here.


TO_LOGIN = 'polls:login'

"""
Cross Site Request Forgery (CSRF)
Comment out the below row (the decorator) for a fix
"""
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("polls:index"))
        else:
            messages.error(request,'Username or password is not correct.')
            return redirect(TO_LOGIN)
    else:
        return render(request, "polls/login.html")


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        try:        
            user = User.objects.create_user(username=username, password=password, email=email)
            Account.objects.create(user=user)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("polls:index"))
        except IntegrityError:
            messages.error(request, 'This username is already taken.')
            return redirect(TO_LOGIN)
        except ValueError:
            messages.error(request, 'You must fill all the fields.')
            return redirect(TO_LOGIN)
    return render(request, "polls/login.html")


def logout_view(request):
    logout(request)
    return redirect(TO_LOGIN)


def index(request):
    if not request.user.is_authenticated:
        return redirect(TO_LOGIN)
    term = request.GET.get('search', '')
    if term:
        """
        A03:2021-Injection
        Comment out the below row and uncomment the next one for a fix
        """
        questions = Question.objects.raw("SELECT * FROM polls_question WHERE question_text LIKE '%%%s%%'" % term)
        #questions = Question.objects.filter(question_text__contains=term)
        if not questions:
            messages.error(request, 'No polls matched your search.')
    else:
        questions = Question.objects.none()
    latest_questions = Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:20]
    context = { "questions": questions, 'latest_questions': latest_questions }
    return render(request, "polls/index.html", context)


class DetailView(LoginRequiredMixin, generic.DetailView):
    login_url = 'polls:login'
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())


"""
A01:2021-Broken Access Control
Comment out the below row and uncomment the next two rows for a fix
"""
class ResultsView(generic.DetailView):
#class ResultsView(LoginRequiredMixin, generic.DetailView):
    #login_url = 'polls:login'
    model = Question
    template_name = "polls/results.html"


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request, "polls/detail.html", {
                "question": question,
                "error_message": "You did not select a choice.",
        },)
    else:
        try:
            Vote.objects.create(user=request.user, choice=selected_choice)
        except IntegrityError as e:
            """
            A05:2021-Security Misconfiguration
            Comment out the two below rows and uncomment the third one for a fix
            """
            messages.error(request, "Error: " + str(e))
            messages.error(request, str(traceback.format_exc()))
            #messages.error(request, "You have already voted for this choice.")
            return redirect("polls:detail", pk=question_id)
        else:
            selected_choice.votes += 1
            selected_choice.save()
            return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


def profile(request):
    if not request.user.is_authenticated:
        return redirect(TO_LOGIN)
    """
    A02:2021-Cryptographic Failures
    Comment out the below row and uncomment the next one for a fix
    """
    user = request.user
    #user = request.user.get_username()
    user_votes = Vote.objects.filter(user=request.user).select_related('choice__question').order_by("-vote_time")
    return render(request, 'polls/profile.html', { 'user': user, 'user_votes': user_votes })
