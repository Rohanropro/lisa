import pandas as pd
import pymysql
from pymysql.err import IntegrityError

# Database connection
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='',  # no password as we used --initialize-insecure
    database='NepalAgriculture',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with connection.cursor() as cursor:
        # Read the workbook
        wb_path = r"C:\Users\ndjsj\Downloads\capstone project data.xlsx"
        
        # --- Production Sheet ---
        print("Reading production sheet...")
        prod_df = pd.read_excel(wb_path, sheet_name='nepals_crops_10_years_2072-2082')
        
        # Clean column names: strip whitespace
        prod_df.columns = [str(col).strip() for col in prod_df.columns]
        
        # The first three columns should be YEAR, DISTRICT, ECOLOGY
        # We'll rename them to standard names just in case
        prod_df = prod_df.rename(columns={
            prod_df.columns[0]: 'YEAR',
            prod_df.columns[1]: 'DISTRICT',
            prod_df.columns[2]: 'ECOLOGY'
        })
        
        # Now, we assume the columns are in the order:
        # [YEAR, DISTRICT, ECOLOGY, 
        #  Paddy_Area, Paddy_Production, Paddy_Yield,
        #  Maize_Area, Maize_Production, Maize_Yield, ...]
        # We'll group the columns from index 3 onward in sets of three.
        crop_groups = []
        n = len(prod_df.columns)
        i = 3
        while i < n:
            # The column at index i is the area column for a crop, and its header should be the crop name (possibly with spaces)
            area_col = prod_df.columns[i]
            production_col = prod_df.columns[i+1] if i+1 < n else None
            yield_col = prod_df.columns[i+2] if i+2 < n else None
            if production_col is None or yield_col is None:
                break
            crop_groups.append((area_col, production_col, yield_col))
            i += 3
        
        # List of crop names from the area column headers (cleaned)
        crop_names = [area_col.strip() for area_col, _, _ in crop_groups]
        print(f"Found crops: {crop_names}")
        
        # Insert ecological regions and districts and crops if not exist
        # We'll get distinct values from the data
        eco_regions = prod_df['ECOLOGY'].dropna().unique()
        districts = prod_df['DISTRICT'].dropna().unique()
        
        # Insert ecological regions
        for region in eco_regions:
            try:
                cursor.execute("INSERT IGNORE INTO EcologicalRegion (region_name) VALUES (%s)", (region,))
            except IntegrityError as e:
                print(f"Error inserting region {region}: {e}")
        
        # Insert districts (we need to know the region for each district)
        # We'll create a mapping from district to region by taking the first occurrence? 
        # Actually, each district belongs to one region, so we can drop duplicates.
        district_region_map = prod_df[['DISTRICT', 'ECOLOGY']].drop_duplicates()
        for _, row in district_region_map.iterrows():
            district_name = row['DISTRICT']
            region_name = row['ECOLOGY']
            # Get region_id
            cursor.execute("SELECT region_id FROM EcologicalRegion WHERE region_name = %s", (region_name,))
            region_result = cursor.fetchone()
            if region_result:
                region_id = region_result['region_id']
                try:
                    cursor.execute("INSERT IGNORE INTO District (district_name, region_id) VALUES (%s, %s)", (district_name, region_id))
                except IntegrityError as e:
                    print(f"Error inserting district {district_name}: {e}")
            else:
                print(f"Region {region_name} not found for district {district_name}")
        
        # Insert crops
        for crop in crop_names:
            try:
                cursor.execute("INSERT IGNORE INTO Crop (crop_name) VALUES (%s)", (crop,))
            except IntegrityError as e:
                print(f"Error inserting crop {crop}: {e}")
        
        # Commit the inserts for reference tables
        connection.commit()
        
        # Now insert production records
        print("Inserting production records...")
        for _, row in prod_df.iterrows():
            year = str(row['YEAR']).strip()
            # Skip rows where year is not a string like '2072/73' (e.g., the header row if any)
            if not year or year.lower() == 'year' or pd.isna(year):
                continue
            district_name = str(row['DISTRICT']).strip()
            if pd.isna(district_name) or district_name.lower() == 'district':
                continue
            ecology_name = str(row['ECOLOGY']).strip()
            if pd.isna(ecology_name) or ecology_name.lower() == 'ecology':
                continue
            
            # Get district_id and crop_id for each crop group
            for area_col, production_col, yield_col in crop_groups:
                crop_name = area_col.strip()  # because the area column header is the crop name
                area_val = row[area_col]
                production_val = row[production_col]
                yield_val = row[yield_col]
                
                # Skip if any of the values is NaN
                if pd.isna(area_val) or pd.isna(production_val) or pd.isna(yield_val):
                    continue
                
                # Get district_id
                cursor.execute("SELECT district_id FROM District WHERE district_name = %s", (district_name,))
                district_result = cursor.fetchone()
                if not district_result:
                    # This should not happen if we inserted all districts
                    continue
                district_id = district_result['district_id']
                
                # Get crop_id
                cursor.execute("SELECT crop_id FROM Crop WHERE crop_name = %s", (crop_name,))
                crop_result = cursor.fetchone()
                if not crop_result:
                    continue
                crop_id = crop_result['crop_id']
                
                # Insert production record
                try:
                    cursor.execute("""
                        INSERT INTO ProductionRecord 
                        (district_id, crop_id, agricultural_year, area_ha, production_mt, reported_yield_mt_ha)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (district_id, crop_id, year, float(area_val), float(production_val), float(yield_val)))
                except IntegrityError as e:
                    # Duplicate entry, we can ignore
                    pass
                except Exception as e:
                    print(f"Error inserting production record for {district_name}, {crop_name}, {year}: {e}")
        
        # Commit production records
        connection.commit()
        
        # --- Climate Sheet ---
        print("Reading climate sheet...")
        climate_df = pd.read_excel(wb_path, sheet_name='nepal_77_districts_climate_2072')
        # Clean column names
        climate_df.columns = [str(col).strip() for col in climate_df.columns]
        
        # Insert climate records
        print("Inserting climate records...")
        for _, row in climate_df.iterrows():
            district_name = str(row['District']).strip()
            if pd.isna(district_name) or district_name.lower() == 'district':
                continue
            ecology_name = str(row['Ecological_Zone']).strip()
            if pd.isna(ecology_name) or ecology_name.lower() == 'ecological_zone':
                continue
            year_bs = int(row['Year_BS']) if not pd.isna(row['Year_BS']) else None
            year_ad = int(row['Year_AD']) if not pd.isna(row['Year_AD']) else None
            month = int(row['Month']) if not pd.isna(row['Month']) else None
            mean_temp = float(row['Mean_Temp']) if not pd.isna(row['Mean_Temp']) else None
            max_temp = float(row['Max_Temp']) if not pd.isna(row['Max_Temp']) else None
            min_temp = float(row['Min_Temp']) if not pd.isna(row['Min_Temp']) else None
            total_rainfall = float(row['Total_Rainfall']) if not pd.isna(row['Total_Rainfall']) else None
            mean_humidity = float(row['Mean_Humidity']) if not pd.isna(row['Mean_Humidity']) else None
            total_solar_rad = float(row['Total_Solar_Rad']) if not pd.isna(row['Total_Solar_Rad']) else None
            
            # Skip if any required field is None
            if None in (district_name, ecology_name, year_bs, year_ad, month):
                continue
            
            # Get district_id
            cursor.execute("SELECT district_id FROM District WHERE district_name = %s", (district_name,))
            district_result = cursor.fetchone()
            if not district_result:
                continue
            district_id = district_result['district_id']
            
            # Insert climate record
            try:
                cursor.execute("""
                    INSERT INTO ClimateRecord 
                    (district_id, year_bs, year_ad, month, mean_temp, max_temp, min_temp, total_rainfall, mean_humidity, total_solar_rad)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (district_id, year_bs, year_ad, month, mean_temp, max_temp, min_temp, total_rainfall, mean_humidity, total_solar_rad))
            except IntegrityError as e:
                # Duplicate entry, ignore
                pass
            except Exception as e:
                print(f"Error inserting climate record for {district_name}, {year_bs}-{month}: {e}")
        
        # Commit climate records
        connection.commit()
        
        print("Data loading completed.")
        
finally:
    connection.close()