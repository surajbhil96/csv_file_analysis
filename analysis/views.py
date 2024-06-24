import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import UploadFileForm
from .models import UploadedFile

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('analyze_file')
    else:
        form = UploadFileForm()
    return render(request, 'analysis/upload.html', {'form': form})

def analyze_file(request):
    try:
        file = UploadedFile.objects.latest('uploaded_at')
    except UploadedFile.DoesNotExist:
        return render(request, 'analysis/no_file.html')

    try:
        df = pd.read_csv(file.file.path)

        # Identifying missing values
        missing_values = df.isnull().sum()

        # Handling missing values (example: dropping rows with missing values)
        df_cleaned = df.dropna()

        # Perform basic analysis on the cleaned DataFrame
        description = df_cleaned.describe().to_html()
        head = df_cleaned.head().to_html()

        # Create a plot
        plt.figure(figsize=(10, 6))
        sns.histplot(df_cleaned.select_dtypes(include=[float, int]).iloc[:, 0], kde=True)
        plot_path = os.path.join(settings.MEDIA_ROOT, 'plot.png')
        plt.savefig(plot_path)
        plt.close()

        context = {
            'description': description,
            'head': head,
            'plot_url': settings.MEDIA_URL + 'plot.png',
            'missing_values': missing_values,  # Include missing values in the context
        }
        return render(request, 'analysis/analyze.html', context)

    except Exception as e:
        return render(request, 'analysis/error.html', {'error': str(e)})