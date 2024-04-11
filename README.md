
# Pedestrian Trip Planner

## Overview

The Pedestrian Trip Planner is a sophisticated tool developed as a final project for CMPT 353 Computational Data Science at Simon Fraser University. It is designed to generate optimally nice pedestrian routes around the City of Vancouver, leveraging OpenStreetMap data to ensure accurate and pedestrian-friendly pathfinding.

## Features

- **Optimized Route Planning**: Calculate pedestrian routes that prioritize scenic and walkable paths.
- **Dynamic Start and End Points**: Users can specify custom starting and ending locations for their route.
- **Caching Mechanism**: Improves performance by caching essential geospatial data locally.
- **Interactive User Interface**: Provides clear feedback and instructions through styled terminal messages.
- **Geographic Bounds Validation**: Ensures user-defined locations are within the project's focus area, the lower mainland of British Columbia.

## Getting Started

### Prerequisites

- Python 3.x
- Required Python packages: `geopandas`, `networkx`, `shapely`, `matplotlib`, `gpxpy`

### Installation

1. Clone the repository to your local machine.
2. You may want to install the required Python packages using `pip`:

   ```sh
   pip3 install -r requirements.txt
   ```

### Data Preparation

1. Download the British Columbia OpenStreetMap data (british-columbia-latest-free.shp.zip) from [GeoFabrik](https://download.geofabrik.de/north-america/canada/british-columbia.html).
2. Unzip the downloaded file to a known directory, which will be referred to as `<path-to-osm-unzipped>` in the command-line arguments.

## Usage

Run the Pedestrian Trip Planner using one of the following formats:

- **Default Mode** (using predefined locations for start and end points):

  ```sh
  python3 main.py <path-to-osm-unzipped>
  ```

  Example:

  ```sh
  python3 main.py ./british-columbia-latest-free.shp
  ```

- **Custom Mode** (specifying start and end points):

  ```sh
  python3 main.py <path-to-osm-unzipped> <start_lon> <start_lat> <end_lon> <end_lat>
  ```

  Example:

  ```sh
  python3 main.py ./british-columbia-latest-free.shp -123.1423 49.2871 -123.1217 49.2744
  ```

Note: The first run of the program will store approximately 230 MB of cache in the project directory to enhance performance.

## Developers

This project was brought to life thanks to the contributions of dedicated individuals:

- **David Wiebe**: Responsible for conceptualizing the project idea and authoring the majority of the codebase, David's vision and expertise have been instrumental in shaping the Pedestrian Trip Planner.

- **Ricky Xu**: Ricky's contributions include the development of complex functions such as the `point_niceness` and `save_paths_as_gpx` functions. Additionally, Ricky enhanced the project with the capability to process user-defined start and end points for route planning.

## Acknowledgments

- CMPT 353 Computational Data Science course staff and our friends at Simon Fraser University.
- OpenStreetMap contributors for providing the data that powers this project.
