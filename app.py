from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
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
        
        # Daily sales
        daily_sales = df.groupby(df['Date'].dt.date)['Price'].agg(['sum', 'count']).reset_index()
        daily_sales = daily_sales.rename(columns={'sum': 'total', 'count': 'transactions'})
        
        # Weekly sales
        df['Week'] = df['Date'].dt.isocalendar().week
        weekly_sales = df.groupby(['Week'])['Price'].agg(['sum', 'count']).reset_index()
        
        # Profile distribution
        profile_stats = df.groupby('Profile')['Price'].agg(['sum', 'count']).reset_index()
        
        # Hourly distribution
        hourly_stats = df.groupby(df['Date'].dt.hour)['Price'].count().reset_index()
        
        return jsonify({
            'daily_sales': daily_sales.to_dict('records'),
            'weekly_sales': weekly_sales.to_dict('records'),
            'profile_stats': profile_stats.to_dict('records'),
            'hourly_stats': hourly_stats.to_dict('records')
        })
    return jsonify({'error': 'Invalid file format'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
