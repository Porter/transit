# Transit Visualization

This project fetches real-time transit vehicle locations from the 511.org API and renders them on a static map.

## Setup with `uv`

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

1.  **Install `uv`** (if not already installed):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Install dependencies**:
    Run the following command to create a virtual environment and install the required packages defined in `pyproject.toml`:
    ```bash
    uv sync
    ```

3.  **Run the project**:
    ```bash
    uv run main.py
    ```

## Configuration

Create a `.env` file in the root directory to configure the application.

### Example `.env`

```dotenv
# Required: Your 511.org API Key
API_KEY='your-api-key-here'

# Optional: Center of the map (Longitude, Latitude)
# If set, the map will be fixed to this location with a zoom level of 14.
# If omitted, the map will automatically zoom to fit all found vehicles.
MAP_CENTER='-122.439851, 37.7718' #Representing San Francisco
```

## Map Behavior: Fixed vs. Auto-Fit

The way the map is rendered depends on whether you provide a `MAP_CENTER` in your `.env` file.

### 1. Encapsulating Box (Auto-Fit)
**Configuration:** Remove or comment out `MAP_CENTER` in `.env`.

When no center is provided, the application calculates a bounding box that includes **all** the vehicle markers found. The map's zoom level and center are automatically adjusted to ensure every vehicle is visible within the image. This is useful for seeing the full extent of the transit network's current activity.

### 2. Zoomed In (Fixed View)
**Configuration:** Set `MAP_CENTER='-122.439851, 37.7718'` (to show SF or your desired coordinates).

When a center is provided, the map ignores the bounding box of the vehicles and instead locks the view to the specified coordinates with a fixed zoom level (currently set to 14). This is useful if you want to monitor a specific neighborhood or area, regardless of where the buses are currently located.