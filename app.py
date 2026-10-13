from flask import Flask, render_template, jsonify, request
import pymysql
from pymysql.cursors import DictCursor
import os
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env file

app = Flask(__name__)

# Database connection helper
def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'NepalAgriculture'),
        charset='utf8mb4',
        cursorclass=DictCursor
    )

# Helper function to execute query and return results
def execute_query(query, args=None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, args or ())
            results = cursor.fetchall()
            return results
    finally:
        conn.close()

# Route for the main dashboard
@app.route('/')
def index():
    return render_template('index.html')

# Health check endpoint
@app.route('/api/health')
def health():
    try:
        conn = get_db_connection()
        conn.cursor().execute('SELECT 1')
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# API endpoint for KPIs
@app.route('/api/kpis')
def get_kpis():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Total crops
            cursor.execute('SELECT COUNT(*) as count FROM Crop')
            total_crops = cursor.fetchone()['count']
            
            # Total districts
            cursor.execute('SELECT COUNT(*) as count FROM District')
            total_districts = cursor.fetchone()['count']
            
            # Production record count
            cursor.execute('SELECT COUNT(*) as count FROM ProductionRecord')
            production_count = cursor.fetchone()['count']
            
            # Climate record count
            cursor.execute('SELECT COUNT(*) as count FROM ClimateRecord')
            climate_count = cursor.fetchone()['count']
        
        conn.close()
        return jsonify({
            'total_crops': total_crops,
            'total_districts': total_districts,
            'production_count': production_count,
            'climate_count': climate_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API endpoint for filter options (districts, crops, years)
@app.route('/api/filters')
def get_filters():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Districts
            cursor.execute('''SELECT d.district_id, d.district_name 
                             FROM District d 
                             ORDER BY d.district_name''')
            districts = [{'id': row['district_id'], 'name': row['district_name']} for row in cursor.fetchall()]
            
            # Crops
            cursor.execute('SELECT crop_id, crop_name FROM Crop ORDER BY crop_name')
            crops = [{'id': row['crop_id'], 'name': row['crop_name']} for row in cursor.fetchall()]
            
            # Agricultural years from production records
            cursor.execute('''SELECT DISTINCT agricultural_year 
                             FROM ProductionRecord 
                             ORDER BY agricultural_year''')
            years = [row['agricultural_year'] for row in cursor.fetchall()]
        
        conn.close()
        return jsonify({
            'districts': districts,
            'crops': crops,
            'years': years
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API endpoint for production data (for charts and table)
@app.route('/api/production')
def get_production():
    try:
        # Get query parameters for filtering
        district_id = request.args.get('district_id')
        crop_id = request.args.get('crop_id')
        year = request.args.get('year')
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Base query
            query = '''
                SELECT pr.*, d.district_name, c.crop_name, e.region_name
                FROM ProductionRecord pr
                JOIN District d ON pr.district_id = d.district_id
                JOIN Crop c ON pr.crop_id = c.crop_id
                JOIN EcologicalRegion e ON d.region_id = e.region_id
                WHERE 1=1
            '''
            params = []
            
            if district_id:
                query += ' AND pr.district_id = %s'
                params.append(district_id)
            if crop_id:
                query += ' AND pr.crop_id = %s'
                params.append(crop_id)
            if year:
                query += ' AND pr.agricultural_year = %s'
                params.append(year)
            
            query += ' ORDER BY pr.agricultural_year, d.district_name, c.crop_name'
            
            cursor.execute(query, params)
            results = cursor.fetchall()
        
        conn.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API endpoint for climate data
@app.route('/api/climate')
def get_climate():
    try:
        # Get query parameters for filtering
        district_id = request.args.get('district_id')
        year_bs = request.args.get('year_bs')
        month = request.args.get('month')
        season = request.args.get('season')  # Winter, Spring, Summer, Autumn
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Base query
            query = '''
                SELECT cr.*, d.district_name, e.region_name
                FROM ClimateRecord cr
                JOIN District d ON cr.district_id = d.district_id
                JOIN EcologicalRegion e ON d.region_id = e.region_id
                WHERE 1=1
            '''
            params = []
            
            if district_id:
                query += ' AND cr.district_id = %s'
                params.append(district_id)
            if year_bs:
                query += ' AND cr.year_bs = %s'
                params.append(year_bs)
            if month:
                query += ' AND cr.month = %s'
                params.append(month)
            
            # Season filtering: we need to map month to season
            # We'll handle this in the application logic for now, but we can also do it in SQL
            # For simplicity, we'll return all data and let the frontend handle season filtering
            # Or we can add season mapping here.
            # Let's define the season mapping: Winter: 12,1,2; Spring: 3,4,5; Summer: 6,7,8,9; Autumn: 10,11
            # We'll add this to the query if season is provided
            if season:
                # We'll implement a simple CASE statement or use IN
                # For now, we'll skip season filtering in the API and do it in the frontend
                # But we should at least validate the season parameter
                pass
            
            query += ' ORDER BY cr.year_bs, cr.month, d.district_name'
            
            cursor.execute(query, params)
            results = cursor.fetchall()
        
        conn.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)