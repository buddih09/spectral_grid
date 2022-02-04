# spectral_grid
Code for heuristic fixed-size partitioning method and electrical grid generation

# Usage
```python

python3 test_grid_generation.py

python3 test_core_partition.py -type grid --plot

python3 test_core_partition.py -type rand --plot

python3 test_core_partition.py -type tree --plot

python3 test_core_partition.py -type comp --plot

```
# Overpass local server
```
sudo docker run \
	-e OVERPASS_META=yes \
	-e OVERPASS_MODE=clone \
	-e OVERPASS_DIFF_URL=https://planet.openstreetmap.org/replication/minute/ \
	-v /big/docker/overpass_clone_db/:/db \
	-p 80:80 \
	-i -t \
	--name overpass_world \
	wiktorn/overpass-api

```
