from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import Account, Choice, Question, Vote

# Create your views here.


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('polls:index')
        else:
            messages.error(request,'Username or password is not correct.')
            return redirect('polls:login')
    else:
        return render(request, "polls/login.html")


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:        
            user = User.objects.create_user(username=username, password=password)
            Account.objects.create(user=user)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('polls:index')
        except IntegrityError:
            messages.error(request, 'This username is already in use.')
            return redirect('polls:login')
    return render(request, "polls/login.html")


def logout_view(request):
    logout(request)
    return redirect('polls:login')


#@login_required
def index(request):
    if not request.user.is_authenticated:
        return redirect('polls:login')
    term = request.GET.get('search', '')
    if term:
        questions = Question.objects.filter(question_text__contains=term)
        if not questions:
            messages.error(request, 'No polls matched your search.')
    else:
        questions = Question.objects.none()
    latest_questions = Question.objects.order_by("-pub_date")[:5]
    context = { "questions": questions, 'latest_questions': latest_questions }
    return render(request, "polls/index.html", context)

def get_queryset(self):
    """
    Return the last five published questions (not including those set to be
    published in the future).
    """
    return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request, "polls/detail.html", {
                "question": question,
                "error_message": "You didn't select a choice.",
        },)
    else:
        selected_choice.votes += 1
        selected_choice.save()
        vote = Vote(user=request.user, choice=selected_choice)
        vote.save()
        # Always return an HttpResponseRedirect after successfully dealing POST data.
        # This prevents data from being posted twice if a user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


def user_votes(request):
    if not request.user.is_authenticated:
        return redirect('polls:login')
    user_votes = Vote.objects.filter(user=request.user).select_related('choice__question')
    return render(request, 'polls/votes.html', { 'user_votes': user_votes })
