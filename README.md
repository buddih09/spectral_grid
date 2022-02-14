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
Pull overpass api docker image.
```
sudo docker pull wiktorn/overpass-api
```
Make a clone of overpass world. This gets a preprocessed planet file that is already indexed downloaded from an existing server. 
```
sudo docker run \
	-e OVERPASS_META=yes \
	-e OVERPASS_MODE=clone \
	-e OVERPASS_DIFF_URL=https://planet.openstreetmap.org/replication/minute/ \
	-v <destination_directory_for_saving_data>:/db \
	-p 80:80 \
	-i -t \
	--name overpass_world \
	wiktorn/overpass-api

```
Example: To initialize the container on Shiva...
```
sudo docker run -e OVERPASS_META=yes -e OVERPASS_MODE=clone -e OVERPASS_DIFF_URL=https://planet.openstreetmap.org/replication/minute/ -v "/media/queen/Data/EVA/overpass_db/:/db" -p 80:80 -i -t --name overpass_world wiktorn/overpass-api
```
After initialization is finished, the docker container will stop. Once you start it again (with docker start command) it will start downloading diffs, applying them to database, and serving API requests.
```
sudo docker start overpass_world
```
