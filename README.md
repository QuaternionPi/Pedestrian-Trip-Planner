
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

### Required Libraries

This project relies on several third-party libraries that are not included with the standard Python installation. Below is a list of necessary libraries along with their purpose within the project:

- **geopandas**: For handling and analyzing geospatial data.
- **networkx**: Essential for graph creation and network analysis.
- **shapely**: Used for geometric calculations and operations.
- **matplotlib**: Needed for visualizing data and routes.
- **gpxpy**: Utilized for generating and processing GPX files for GPS devices.

### Installation

Ensure `Python 3.x` is installed on your system, then install the required libraries using the following command:

  ```sh
  pip3 install geopandas networkx shapely matplotlib gpxpy
  ```

Alternatively, there is a `requirements.txt` file provided with the project. You can install all dependencies using:

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

## Expected Outputs

When you run the Pedestrian Trip Planner, you can expect the following outputs based on your provided inputs:

- **Terminal Feedback**: The application will provide feedback throughout the execution process, offering status updates, error messages, and warnings in a clear, user-friendly manner.

- **Route Visualization**: If the route calculation is successful, you will see a visual map representation of the planned route. This visualization helps in understanding the path layout and the interaction with various geographic features.

- **GPX File**: The application will generate a GPX file suitable for use in GPS devices. This file contains the planned route and is ready for navigation purposes. We recommend visualizing GPX files with [GPX Studio](https://gpx.studio/).

- **Caching Messages**: The application will notify you about the caching of data during the first run of the program, essential for optimizing performance.

## Developers

This project was brought to life thanks to the contributions of dedicated individuals:

- **David Wiebe**: Responsible for conceptualizing the project idea and authoring the majority of the codebase, David's vision and expertise have been instrumental in shaping the Pedestrian Trip Planner.

- **Ricky Xu**: Ricky's contributions include the development of complex functions such as the `point_niceness` and `save_paths_as_gpx` functions. Additionally, Ricky enhanced the project with the capability to process user-defined start and end points for route planning.

## Acknowledgments

- CMPT 353 Computational Data Science course staff and our friends at Simon Fraser University.
- OpenStreetMap contributors for providing the data that powers this project.
