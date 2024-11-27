from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def process_csv(file_path):
    df = pd.read_csv(file_path, skiprows=1)  # Skip the first row with total
    df['Date'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    return df

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.endswith('.csv'):
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        df = process_csv(filepath)
        
        # Get filter parameters
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        profiles = request.form.getlist('profiles[]')
        min_price = request.form.get('min_price')
        max_price = request.form.get('max_price')
        
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
            'Username': 'count'  # Count unique tickets
        }).reset_index()
        profile_stats.columns = ['Profile', 'total_sales', 'total_transactions', 'tickets_sold']
        
        # Calculate percentages for tickets distribution
        total_tickets = profile_stats['tickets_sold'].sum()
        profile_stats['percentage'] = (profile_stats['tickets_sold'] / total_tickets * 100).round(2)
        
        # Convert all numeric columns to native Python types
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
            'daily_sales': daily_sales.to_dict('records'),
            'weekly_sales': weekly_sales.to_dict('records'),
            'profile_stats': profile_stats.to_dict('records'),
            'hourly_stats': hourly_stats.to_dict('records'),
            'filter_options': {
                'profiles': all_profiles,
                'price_range': price_range,
                'date_range': date_range
            }
        }
        
        # Convert all numpy types to native Python types
        response_data = convert_to_native_types(response_data)
        
        return jsonify(response_data)
    return jsonify({'error': 'Invalid file format'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
