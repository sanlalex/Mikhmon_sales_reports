from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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
        df = pd.read_csv(file_path, skiprows=1)
        df['Date'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
        return df
    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}")
        raise

def convert_to_native_types(obj):
    if isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, pd.Timestamp):
        return obj.strftime('%Y-%m-%d')
    elif isinstance(obj, dict):
        return {key: convert_to_native_types(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_native_types(item) for item in obj]
    return obj

def apply_filters(df, start_date=None, end_date=None, profiles=None, min_price=None, max_price=None):
    filtered_df = df.copy()
    
    if start_date:
        filtered_df = filtered_df[filtered_df['Date'].dt.date >= pd.to_datetime(start_date).date()]
    if end_date:
        filtered_df = filtered_df[filtered_df['Date'].dt.date <= pd.to_datetime(end_date).date()]
    if profiles:
        filtered_df = filtered_df[filtered_df['Profile'].isin(profiles)]
    if min_price is not None:
        filtered_df = filtered_df[filtered_df['Price'] >= float(min_price)]
    if max_price is not None:
        filtered_df = filtered_df[filtered_df['Price'] <= float(max_price)]
        
    return filtered_df

def index(request):
    return render(request, 'index.html')

@csrf_exempt
@require_http_methods(["POST"])
def upload_file(request):
    logger.info(f"Received {request.method} request to /upload/")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    if 'file' not in request.FILES:
        logger.warning("No file in request")
        return JsonResponse({'error': 'No file part'}, status=400)
    
    file = request.FILES['file']
    if file.name == '':
        logger.warning("Empty filename")
        return JsonResponse({'error': 'No selected file'}, status=400)
    
    if not file.name.endswith('.csv'):
        logger.warning(f"Invalid file type: {file.name}")
        return JsonResponse({'error': 'Only CSV files are allowed'}, status=400)

    try:
        # Create uploads directory if it doesn't exist
        if not os.path.exists(settings.MEDIA_ROOT):
            logger.info(f"Creating upload directory: {settings.MEDIA_ROOT}")
            os.makedirs(settings.MEDIA_ROOT)

        # Save file
        filepath = os.path.join(settings.MEDIA_ROOT, file.name)
        logger.info(f"Saving file to: {filepath}")
        
        with open(filepath, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        logger.info("File saved successfully")

        # Process CSV
        df = process_csv(filepath)
        logger.info("CSV processed successfully")
        
        # Get filter parameters
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        profiles = request.POST.getlist('profiles[]')
        min_price = request.POST.get('min_price')
        max_price = request.POST.get('max_price')
        
        logger.info(f"Filter parameters: start_date={start_date}, end_date={end_date}, profiles={profiles}, min_price={min_price}, max_price={max_price}")
        
        # Apply filters
        filtered_df = apply_filters(df, start_date, end_date, profiles, min_price, max_price)
        
        # Get unique profiles for filter options
        all_profiles = df['Profile'].unique().tolist()
        price_range = {
            'min': float(df['Price'].min()),
            'max': float(df['Price'].max())
        }
        date_range = {
            'min': df['Date'].min().strftime('%Y-%m-%d'),
            'max': df['Date'].max().strftime('%Y-%m-%d')
        }
        
        # Daily sales
        daily_sales = filtered_df.groupby(filtered_df['Date'].dt.date)['Price'].agg(['sum', 'count']).reset_index()
        daily_sales = daily_sales.rename(columns={'sum': 'total', 'count': 'transactions'})
        daily_sales['Date'] = daily_sales['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))
        
        # Weekly sales
        filtered_df['Week'] = filtered_df['Date'].dt.strftime('%Y-W%W')
        weekly_sales = filtered_df.groupby(['Week'])['Price'].agg(['sum', 'count']).reset_index()
        
        # Profile distribution
        profile_stats = filtered_df.groupby('Profile').agg({
            'Price': ['sum', 'count'],
            'Username': 'count'
        }).reset_index()
        profile_stats.columns = ['Profile', 'total_sales', 'total_transactions', 'tickets_sold']
        
        total_tickets = profile_stats['tickets_sold'].sum()
        profile_stats['percentage'] = (profile_stats['tickets_sold'] / total_tickets * 100).round(2)
        
        profile_stats = profile_stats.astype({
            'total_sales': float,
            'total_transactions': int,
            'tickets_sold': int,
            'percentage': float
        })
        
        # Hourly distribution
        hourly_stats = filtered_df.groupby(filtered_df['Date'].dt.hour)['Price'].count().reset_index()
        hourly_stats = hourly_stats.astype({
            'Date': int,
            'Price': int
        })
        
        response_data = {
            'profiles': all_profiles,
            'price_range': price_range,
            'date_range': date_range,
            'daily_sales': daily_sales.to_dict('records'),
            'weekly_sales': weekly_sales.to_dict('records'),
            'profile_stats': profile_stats.to_dict('records'),
            'hourly_stats': hourly_stats.to_dict('records')
        }
        
        logger.info("Data processed successfully")
        logger.info("Sending response")
        
        response = JsonResponse(convert_to_native_types(response_data))
        response["Access-Control-Allow-Origin"] = "http://localhost:8000"
        response["Access-Control-Allow-Credentials"] = "true"
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
