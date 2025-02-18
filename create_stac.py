import shutil
import tempfile
from pathlib import Path
import pystac
import rasterio
from shapely.geometry import Polygon, mapping
from datetime import datetime as dt


catalog = pystac.Catalog(
    id="rqa-deforestation-test-data",
    description="RQADeforestation test data. Subset of Sentinel-1 Sigma0.",
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
            id=raster_uri,
            geometry=mapping(footprint),
            bbox=bbox,
            datetime=datetime,
            properties=tags,
            href=raster_uri,
        )
        item.add_asset(
            key="image",
            asset=pystac.Asset(href=ds.files[0], media_type=pystac.MediaType.GEOTIFF),
        )
        return item


for path in list(Path(".").rglob("*.tif")):
    raster_uri = str(path)
    item = to_stac_item(raster_uri)
    catalog.add_item(item)

catalog.set_self_href("catalog.json")
catalog.save()
