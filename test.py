import geopandas as gpd

# Load GeoJSON files
states_gdf = gpd.read_file('static/geojson/india_state.geojson')
districts_gdf = gpd.read_file('static/geojson/india_district.geojson')

# Print unique state names
print("State Names (NAME_1):")
print(states_gdf['NAME_1'].str.upper().unique())

# Print unique district names for A&N Islands (if present)
print("\nDistrict Names for A&N Islands (NAME_2):")
andaman_districts = districts_gdf[districts_gdf['NAME_1'].str.upper() == 'ANDAMAN AND NICOBAR ISLANDS']
print(andaman_districts['NAME_2'].str.upper().unique() if not andaman_districts.empty else "No districts found")