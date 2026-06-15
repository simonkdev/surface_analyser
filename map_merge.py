from pathlib import Path
import os

import rasterio
from rasterio.transform import Affine
from rasterio.windows import Window, from_bounds
from tqdm import tqdm

# === Settings ===
INPUT_DIR = Path("data/raw")  # Change this to your folder
OUTPUT_PATH = Path("data/worldcover_2020_merged.tif")
CHUNK_SIZE = int(os.environ.get("MERGE_CHUNK_SIZE", "1024"))
GDAL_CACHE_MB = int(os.environ.get("GDAL_CACHEMAX", "64"))
COMPRESSION = os.environ.get("MERGE_COMPRESSION", "zstd")
ZSTD_LEVEL = int(os.environ.get("MERGE_ZSTD_LEVEL", "1"))


def round_window(window):
    return Window(
        col_off=round(window.col_off),
        row_off=round(window.row_off),
        width=round(window.width),
        height=round(window.height),
    )


def chunk_windows(width, height, chunk_size):
    for row_off in range(0, height, chunk_size):
        rows = min(chunk_size, height - row_off)
        for col_off in range(0, width, chunk_size):
            cols = min(chunk_size, width - col_off)
            yield Window(col_off, row_off, cols, rows)


def inspect_sources(paths):
    with rasterio.open(paths[0]) as first:
        profile = first.profile.copy()
        crs = first.crs
        transform = first.transform
        xres = transform.a
        yres = -transform.e
        dtype = first.dtypes[0]
        count = first.count
        nodata = first.nodata
        left, bottom, right, top = first.bounds

    if xres <= 0 or yres <= 0:
        raise ValueError("Expected north-up rasters with positive pixel size.")

    for path in tqdm(paths[1:], desc="Inspecting tiles"):
        with rasterio.open(path) as src:
            if src.crs != crs:
                raise ValueError(f"CRS mismatch: {path}")
            if src.count != count:
                raise ValueError(f"Band count mismatch: {path}")
            if src.dtypes[0] != dtype:
                raise ValueError(f"Data type mismatch: {path}")
            if abs(src.transform.a - xres) > 1e-12 or abs((-src.transform.e) - yres) > 1e-12:
                raise ValueError(f"Resolution mismatch: {path}")

            left = min(left, src.bounds.left)
            bottom = min(bottom, src.bounds.bottom)
            right = max(right, src.bounds.right)
            top = max(top, src.bounds.top)

    output_transform = Affine.translation(left, top) * Affine.scale(xres, -yres)
    width = round((right - left) / xres)
    height = round((top - bottom) / yres)

    profile.update({
        "driver": "GTiff",
        "width": width,
        "height": height,
        "transform": output_transform,
        "count": count,
        "dtype": dtype,
        "crs": crs,
        "nodata": nodata,
        "compress": COMPRESSION,
        "tiled": True,
        "blockxsize": 512,
        "blockysize": 512,
        "NUM_THREADS": "ALL_CPUS",
        "BIGTIFF": "IF_SAFER",
        "SPARSE_OK": "TRUE",
    })
    if COMPRESSION.lower() == "zstd":
        profile["zstd_level"] = ZSTD_LEVEL

    return profile, output_transform


def copy_tile(src, dst, output_transform):
    tile_window = round_window(from_bounds(*src.bounds, transform=output_transform))
    nodata = src.nodata

    for read_window in chunk_windows(src.width, src.height, CHUNK_SIZE):
        data = src.read(window=read_window)
        if nodata is not None and (data == nodata).all():
            continue

        write_window = Window(
            tile_window.col_off + read_window.col_off,
            tile_window.row_off + read_window.row_off,
            read_window.width,
            read_window.height,
        )
        dst.write(data, window=write_window)

# === Collect input files ===
tif_files = sorted(INPUT_DIR.glob("*_Map.tif"))
if not tif_files:
    raise FileNotFoundError("No *_Map.tif files found in the specified directory.")

print(f"Found {len(tif_files)} tiles. Beginning merge...")
print(f"Using source chunk size: {CHUNK_SIZE} px; GDAL cache: {GDAL_CACHE_MB} MB")
print(f"Using GeoTIFF compression: {COMPRESSION}")
print(f"Writing output to: {OUTPUT_PATH}")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

with rasterio.Env(GDAL_CACHEMAX=GDAL_CACHE_MB):
    output_profile, output_transform = inspect_sources(tif_files)
    with rasterio.open(OUTPUT_PATH, "w", **output_profile) as dst:
        for path in tqdm(tif_files, desc="Writing tiles"):
            with rasterio.open(path) as src:
                copy_tile(src, dst, output_transform)

print("Merge complete!")
