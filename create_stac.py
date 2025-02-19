#!/usr/bin/env python3

#
# Creates a STAC catalog from a nested dictionary of GEoTIF files
#

from pathlib import Path
import pystac
import rasterio
from shapely.geometry import Polygon, mapping
from datetime import datetime


catalog = pystac.Catalog(
    id="rqa-deforestation-test-data",
    description="RQADeforestation test data. Subset of Sentinel-1 Sigma0 containing the tile E051N018T3.",
)

collection = pystac.Collection(
    id="rqa-deforestation-test-data",
    description="RQADeforestation test data. Subset of Sentinel-1 Sigma0 containing the tile E051N018T3.",
    extent=pystac.Extent(
        spatial=pystac.SpatialExtent([[-180.0, -90.0, 180.0, 90.0]]),
        temporal=pystac.TemporalExtent(
            [[datetime(2020, 1, 1), datetime(2022, 12, 31)]]
        ),
    ),
)


def to_stac_item(raster_uri):
    with rasterio.open(raster_uri) as ds:
        bounds = ds.bounds
        bbox = [bounds.left, bounds.bottom, bounds.right, bounds.top]
        footprint = Polygon(
            [
                [bounds.left, bounds.bottom],
                [bounds.left, bounds.top],
                [bounds.right, bounds.top],
                [bounds.right, bounds.bottom],
            ]
        )
        tags = ds.tags()
        datetime = dt.fromisoformat(tags["sensing_date"])
        item = pystac.Item(
            id=raster_uri + ".json",
            geometry=mapping(footprint),
            bbox=bbox,
            datetime=datetime,
            properties=tags,
            href=raster_uri,
        )
        item.add_asset(
            key="image",
            asset=pystac.Asset(href=raster_uri, media_type=pystac.MediaType.GEOTIFF),
        )
        return item


for path in list(Path(".").rglob("*.tif")):
    raster_uri = str(path)
    item = to_stac_item(raster_uri)
    collection.add_item(item)

catalog.add_child(collection)
catalog.normalize_and_save("stac", catalog_type=pystac.CatalogType.SELF_CONTAINED)
