from staticmap import StaticMap, CircleMarker, Line
import math

def render_clean_map(markers, output_file="map.png", width=800, height=600, zoom=None, center=None):
    """
    Render a static map with markers using CartoDB Positron (Light) tiles.
    
       Args:
        markers: List of (lat, lon, bearing) tuples.
        output_file: Path to save the image.
        width: Image width.
        height: Image height.
        zoom: Optional zoom level (int).
        center: Optional center [lon, lat].
    """
    # Standard OpenStreetMap tiles (Colorful)
    # tile_url = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    tile_url = "https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png"
    # tile_url = "https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png"
    
    m = StaticMap(width, height, url_template=tile_url)
    
    for lat, lon, bearing in markers:
        # staticmap uses (lon, lat) for markers
        marker = CircleMarker((lon, lat), "#FF0000", 5)
        m.add_marker(marker)
        
        if bearing is not None:
            # Calculate end point for bearing line
            # Length of the line in degrees (approx)
            length = 0.0005
            # Convert bearing to radians
            rad = math.radians(bearing)
            
            # Calculate delta
            # bearing 0 is North (positive lat), 90 is East (positive lon)
            d_lat = length * math.cos(rad)
            # Adjust longitude delta for latitude to preserve angle on Mercator map
            d_lon = length * math.sin(rad) / math.cos(math.radians(lat))
            
            end_lat = lat + d_lat
            end_lon = lon + d_lon
            
            line = Line([(lon, lat), (end_lon, end_lat)], "#FF0000", 2)
            m.add_line(line)
        
    image = m.render(zoom=zoom, center=center)
    image.save(output_file)
    print(f"Map saved to {output_file}")

