#!/bin/bash
set -e

VERSION=$1
if [ -z "$VERSION" ]; then
  echo "Usage: $0 <version>"
  exit 1
fi

if ! command -v gh &> /dev/null; then
    echo "gh command could not be found, please install it first"
    exit 1
fi

MANIFEST_FILES=$(find . -name "manifest.json")
NUM_FILES=$(echo "$MANIFEST_FILES" | wc -l)

if [ "$NUM_FILES" -eq 0 ]; then
    echo "Error: No manifest.json found."
    exit 1
elif [ "$NUM_FILES" -gt 1 ]; then
    echo "Error: Multiple manifest.json files found. Please specify the path to the manifest.json file."
    echo "$MANIFEST_FILES"
    exit 1
fi

MANIFEST_PATH=$MANIFEST_FILES

# Using python to update the json file to avoid issues with sed
python -c "import json; data = json.load(open('$MANIFEST_PATH')); data['version'] = '$VERSION'; json.dump(data, open('$MANIFEST_PATH', 'w'), indent=2)"

git add "$MANIFEST_PATH"
git commit -m "chore(release): $VERSION"
gh release create "$VERSION" --generate-notes
