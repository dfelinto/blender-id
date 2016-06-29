#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo $DIR

# Copy requirements.txt into current folder
cp ../requirements.txt .
# Build image
docker build -t armadillica/blender_id .
# Remove requirements.txt
rm requirements.txt
