#!/bin/sh

set -e

echo "***Be sure you are on master branch.***"
echo "Change mech/__init__.py version."
echo "Update the CHANGELOG.md file."
echo "Commit those changes before running this script."

VERSION=`python setup.py --version`

echo "# Releasing mikemech v$VERSION..."

echo "# Running tests..."
pytest

git push

echo "# Git tag & push..."
git tag -a "v$VERSION" -m "v$VERSION"
git push --tags

echo "# Upload to pypi..."
# Clear build & dist
rm -rf build/* dist/*
# Build source and wheel packages
python setup.py sdist bdist_wheel
# Upload w/Twine
twine upload dist/*

echo "# All done!"
