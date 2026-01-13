#!/bin/bash
set -e

LAYER_DIR="layer"
PYTHON_DIR="$LAYER_DIR/python"

rm -rf $LAYER_DIR
mkdir -p $PYTHON_DIR

pip install -r requirements.txt -t $PYTHON_DIR
cp scripts/custom_utils.py $PYTHON_DIR/

cd $LAYER_DIR
zip -r ../dependencies-layer.zip .
cd ..
