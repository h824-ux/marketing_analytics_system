from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import os
from .models import Dataset
from django.conf import settings
from .matp import test_variables, run_python_code
import time

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend, Why?
# Create your views here.

@login_required
def anal(request, dataset_id=None):
    if dataset_id is None:
        # return HttpResponse("My About page.")
        return render(request, 'anal/anal.html')

    try:
        dataset = get_object_or_404(Dataset, id=dataset_id, user=request.user)
        
        # Run the analysis
        if run_python_code(dataset):
            context = {
                'dataset': dataset,
                'category_plot': 'category.png',
                'price_plot': 'price.png',
                'age_plot': 'age.png',
                'month_plots': [
                    {'year': '2021', 'file': 'month_2021.png'},
                    {'year': '2022', 'file': 'month_2022.png'},
                    {'year': '2023', 'file': 'month_2023.png'}
                ],
                'timestamp': int(time.time())
            }
            return render(request, 'anal/anal.html', context)
        else:
            messages.error(request, 'Error generating plots')
            return redirect('/')
            
    except Exception as e:
        messages.error(request, f'Error analyzing dataset: {str(e)}')
        return redirect('/')

@login_required
def upload_dataset_view(request):
    if request.method == 'POST':
        if 'files' in request.FILES:
            uploaded_file = request.FILES['files']
            try:
                # Create new dataset first
                dataset = Dataset.objects.create(
                    dataset_name=os.path.splitext(uploaded_file.name)[0],
                    user=request.user,
                    upload_date=timezone.now().date(),
                    upload_time=timezone.now().time()
                )
                
                # Ensure the media/datasets directory exists
                os.makedirs(os.path.join('media', 'datasets'), exist_ok=True)
                
                # Save the file
                file_path = os.path.join('media', 'datasets', f"{dataset.dataset_name}.csv")
                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                # Now read and validate the CSV
                df = pd.read_csv(file_path)
                required_columns = ['Product Category', 'Product Price', 'Purchase Date', 'Customer Age', 'Gender']
                
                # Check columns
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    # If validation fails, delete the dataset and file
                    dataset.delete()
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    messages.error(request, f'Missing columns in dataset: {", ".join(missing_columns)}')
                    return redirect('/')
                
                messages.success(request, 'Dataset uploaded successfully!')
                test_variables()
                return redirect('anal:anal', dataset_id=dataset.id)
                
            except Exception as e:
                # Clean up if there's an error
                if 'dataset' in locals():
                    dataset.delete()
                if 'file_path' in locals() and os.path.exists(file_path):
                    os.remove(file_path)
                messages.error(request, f'Error uploading dataset: {str(e)}')
                messages.error(request, 'Your dataset must include the following columns:')
                messages.error(request, 'Product Category, Product Price, Purchase Date, Customer Age, Gender')
                return redirect('/')
    
    return redirect('/')

def home_view(request):
    if request.user.is_authenticated:
        try:
            user_datasets = Dataset.objects.filter(user=request.user).order_by('-upload_date', '-upload_time')
            return render(request, 'home.html', {
                'datasets': user_datasets,
                'user': request.user
            })
        except Exception as e:
            messages.error(request, f"Error loading datasets: {str(e)}")
            return render(request, 'home.html', {'datasets': []})
    else:
        # For anonymous users, just render the template without datasets
        return render(request, 'home.html', {'datasets': []})

def demo(request):
    return render(request, 'anal/demo.html')

def demo2(request):
    return render(request, 'anal/demo2.html')

def category(request):
    return render(request, 'anal/category.html')

def price(request):
    return render(request, 'anal/price.html')

def price2(request):
    return render(request, 'anal/price-2.html')

def ageselect(request):
    return render(request, 'anal/age-select.html')

def age(request):
    return render(request, 'anal/age.html')

def age2(request):
    return render(request, 'anal/age-2.html')

def gender(request):
    return render(request, 'anal/gender.html')

def month(request):
        # Get selected plots from query parameters
    selected_plots = request.GET.getlist('plots')
    
    # If no plots selected, show all by default
    if not selected_plots:
        selected_plots = ['month2023', 'month2022', 'month2021']
    
    context = {
        'selected_plots': selected_plots,
        'timestamp': int(time.time())  # Add timestamp to prevent caching
    }
    return render(request, 'anal/month.html', context)

def onetwo(request):
    return render(request, 'anal/1-2.html')


def onethree(request):
    selected_plots = request.GET.getlist('plots')
    
    # If no plots selected, show all by default
    if not selected_plots:
        selected_plots = ['1-3-2023', '1-3-2022', '1-3-2021']
    
    context = {
        'selected_plots': selected_plots,
        'timestamp': int(time.time())  # Add timestamp to prevent caching
    }
    return render(request, 'anal/1-3.html', context)

def onefour(request):
    return render(request, 'anal/1-4.html')

def onefive(request):
    return render(request, 'anal/1-5.html')

def twothree(request):
    selected_plots = request.GET.getlist('plots')
    
    # If no plots selected, show all by default
    if not selected_plots:
        selected_plots = ['2-3-2023', '2-3-2022', '2-3-2021']
    
    context = {
        'selected_plots': selected_plots,
        'timestamp': int(time.time())  # Add timestamp to prevent caching
    }
    return render(request, 'anal/2-3.html', context)

def twofour(request):
    return render(request, 'anal/2-4.html')

def twofive(request):
    return render(request, 'anal/2-5.html')

def threefour(request):
    selected_plots = request.GET.getlist('plots')
    
    # If no plots selected, show all by default
    if not selected_plots:
        selected_plots = ['3-4-2023', '3-4-2022', '3-4-2021']
    
    context = {
        'selected_plots': selected_plots,
        'timestamp': int(time.time())  # Add timestamp to prevent caching
    }
    return render(request, 'anal/3-4.html', context)

def threefive(request):
    selected_plots = request.GET.getlist('plots')
    
    # If no plots selected, show all by default
    if not selected_plots:
        selected_plots = ['3-5-2023', '3-5-2022', '3-5-2021']
    
    context = {
        'selected_plots': selected_plots,
        'timestamp': int(time.time())  # Add timestamp to prevent caching
    }
    return render(request, 'anal/3-5.html', context)
