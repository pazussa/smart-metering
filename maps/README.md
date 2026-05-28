# GIS

`maps/assets.geojson` is generated with:

```bash
python -m src.export_geojson
```

Load the GeoJSON directly in QGIS, or connect QGIS to PostGIS after running:

```bash
docker-compose up -d postgres
python -m src.database_loader --reset
```

Suggested styling:

- `asset_type = feeder`: large neutral point.
- `asset_type = transformer`: color by `latest_loss_percent`.
- `asset_type = smart_meter`: small point.
- `asset_type = macro_meter`: larger point with a distinct marker.

