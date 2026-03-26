from django.shortcuts import render, redirect 
from django.contrib.auth.forms import AuthenticationForm 
from django.contrib.auth import login, logout
from .forms import SignupForm, FeedbackForm
from django.contrib import messages  # Import messages framework
from .models import Feedback, RequestSupport

# Create your views here.
def register_view(request):
    if request.method == "POST": 
        form = SignupForm(request.POST) 
        if form.is_valid(): 
            user = form.save()  # Save the user instance
            login(request, user)  # Log the user in
            return redirect('/')  # Redirect to home page
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")  # Error message
    else:
        form = SignupForm()
    return render(request, "users/register.html", { "form": form })

def login_view(request): 
    if request.method == "POST": 
        form = AuthenticationForm(data=request.POST)
        if form.is_valid(): 
            login(request, form.get_user())
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect("/")
    else: 
        form = AuthenticationForm()
    return render(request, "users/login.html", { "form": form })

def logout_view(request):
    logout(request)
    return redirect('homepage')  # Use the name you defined in your main urls.py

def feedback(request):
    if request.method == "POST": 
        form = FeedbackForm(request.POST)
        if form.is_valid(): 
            feedback_obj = form.save(commit=False)
            if request.user.is_authenticated:
                feedback_obj.user = request.user
            feedback_obj.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect("users:feedback")
    else: 
        form = FeedbackForm()
    return render(request, 'users/feedback.html', { "form": form })

def support(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            user = request.user
            # Create and save the support request with User object
            RequestSupport.objects.create(
                firstname=user.first_name or '',
                lastname=user.last_name or '',
                username=user,  # Pass the User object directly
                companyname=getattr(user, 'companyname', '') if hasattr(user, 'companyname') else '',
                email=user.email or ''
            )
            messages.success(request, "Support Requested! The help support team will send you an email in your email account.")
        else:
            messages.error(request, "You must be logged in to request support.")
        return redirect("users:support")
    return render(request, 'users/support.html')