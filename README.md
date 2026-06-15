# Surface Analyser

A tool for analyzing **land cover data** using **ESA WorldCover 2020** maps. This project processes high-resolution land cover classifications and provides interactive visualization capabilities.

---

## 📌 About

### Purpose
This tool enables:
- **Land cover classification analysis** from ESA WorldCover 2020 data
- **Interactive exploration** of global land cover types
- **Custom map merging** for specific regions of interest

### Data Source
- **ESA WorldCover 2020**: Global land cover map at 10m resolution
- **Data Format**: GeoTIFF files
- **Coverage**: Worldwide land surface classification

### Use Cases
- Environmental research
- Land use planning
- Climate change studies
- Biodiversity analysis

---
## ✨ Features

### Core Capabilities
- **Data Processing**: Merge and process ESA WorldCover tiles
- **Interactive Visualization**: Explore land cover classifications
- **Classification Analysis**: Analyze distribution of land cover types
- **Custom Regions**: Focus on specific geographic areas

### Land Cover Classes
The ESA WorldCover 2020 dataset includes:
- Tree cover
- Shrubland
- Grassland
- Cropland
- Built-up
- Bare/sparse vegetation
- Snow/ice
- Permanent water bodies
- Herbaceous wetland
- Mangroves
- Moss and lichen

---
## 🚀 Usage

### Prerequisites
- **ESA WorldCover Data**: Must be downloaded separately (see Data Setup)
- **Python 3.11+**
- **Devenv** (recommended)

### Data Setup

1. **Download ESA WorldCover 2020 data**:
   - Access from: [ESA WorldCover Portal](https://worldcover2020.esa.int/)
   - Download the **2020 version** tiles for your region of interest
   - Create directory: `mkdir -p data/raw`

2. **Place raw data**:
```
surface_analyser/
└── data/
└── raw/          # Place ESA WorldCover tiles here
```

4. **Merge maps**:
```sh
devenv shell
python map_merge.py
```

This will create a single merged GeoTIFF in data/
Note: The merged file is ~100GB


### Running the Analysis

Start Jupyter with Devenv:
```sh
devenv shell
jupyter notebook
```

Open the interactive notebook:

Open interactive_landcover_map.ipynb
Run all cells to load and visualize the data


Or use Voila for web deployment:
```sh
voila interactive_landcover_map.ipynb
```

# Process data with main script
python main.py

# Merge additional maps
python map_merge.py


📁 Project Structure

```text

surface_analyser/
├── interactive_landcover_map.ipynb  # Main analysis notebook
├── main.py                          # Core processing script
├── map_merge.py                     # Map merging logic
├── data/                            # Data directory
│   ├── raw/                         # ESA WorldCover tiles (input)
│   └── merged.tif                   # Merged output (~100GB)
├── devenv.nix                       # Devenv packages
├── devenv.yaml                      # Devenv config
├── devenv.lock                      # Locked dependencies
└── .envrc                           # Direnv configuration
```

📜 License
This project is licensed under the MIT License.
Copyright (c) 2026 Simon Korten
