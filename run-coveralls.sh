#!/bin/bash

echo "$TRAVIS_PYTHON_VERSION"
if [ "$TRAVIS_PYTHON_VERSION" == "3.5" ] ; then
    echo "Running coveralls..."
    coveralls
else
    echo "Skipping coveralls."
fi
