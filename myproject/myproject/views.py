# from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages  # Import messages framework

def homepage(request):
    # return HttpResponse("Hello World! I'm Home.")
    return render(request, 'home.html')


def upload_file_view(self, request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('files')  # Get the uploaded file
        if uploaded_file:
            # Process the uploaded file (e.g., save it, read it, etc.)
            # For example, you can save it to a model or handle it as needed
            # Here, you can add your file processing logic

            messages.success(request, "File uploaded successfully!")  # Success message
            return redirect('/anal/anal/')  # Redirect to anal/anal.html
        else:
            self.add_error("No file uploaded.")
    return render(request, "home.html")  # Render the home page if not a POST request