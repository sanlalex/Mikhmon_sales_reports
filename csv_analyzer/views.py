from django.shortcuts import render
from django.views.decorators.http import require_http_methods
import pandas as pd
import numpy as np
from datetime import datetime
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def process_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}")
        raise

def format_number(value):
    if isinstance(value, (int, np.integer)):
        return f"{value:,}"
    elif isinstance(value, (float, np.floating)):
        return f"{value:,.2f}"
    return value

def index(request):
    return render(request, 'index.html')

@require_http_methods(["POST"])
def upload_csv(request):
    if 'csv_file' not in request.FILES:
        return render(request, 'partials/results.html', {'error': 'Veuillez sélectionner un fichier CSV'})
    
    file = request.FILES['csv_file']
    if not file.name.endswith('.csv'):
        return render(request, 'partials/results.html', {'error': 'Seuls les fichiers CSV sont acceptés'})

    try:
        # Créer le dossier uploads s'il n'existe pas
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)

        # Sauvegarder le fichier
        filepath = os.path.join(settings.MEDIA_ROOT, file.name)
        with open(filepath, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Traiter le CSV
        df = process_csv(filepath)
        
        # Calculer les statistiques
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        total_rows = len(df)
        
        stats = {
            'columns': df.columns.tolist(),
            'data': df.head(10).values.tolist(),  # Afficher les 10 premières lignes
            'total_sales': format_number(df[numeric_columns].sum().sum()),
            'average_sales': format_number(df[numeric_columns].mean().mean()),
            'transaction_count': format_number(total_rows)
        }
        
        return render(request, 'partials/results.html', stats)
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement du fichier: {str(e)}")
        return render(request, 'partials/results.html', {'error': f"Erreur lors du traitement du fichier: {str(e)}"})
