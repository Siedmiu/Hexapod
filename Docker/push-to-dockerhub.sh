#!/bin/bash
set -e

# Helper function
push_image() {
  local local_tag="$1"
  local remote_tag="$2"
  echo "Tagging image $local_tag as $remote_tag"
  docker tag "$local_tag" "$remote_tag"
  echo "Pushing $remote_tag to Docker Hub..."
  docker push "$remote_tag"
}

echo "Select image to push:"
echo "1) hexapod-prod (prod)"
echo "2) hexapod-dev (dev)"
echo "3) both"
read -p "Your choice [1/2/3]: " choice

case "$choice" in
  1)
    push_image hexapod-prod natantulo/hexapod:prod
    ;;
  2)
    push_image hexapod-dev natantulo/hexapod:dev
    ;;
  3)
    push_image hexapod-prod natantulo/hexapod:prod
    push_image hexapod-dev natantulo/hexapod:dev
    ;;
  *)
    echo "Invalid choice."
    exit 1
    ;;
esac

echo "Done."
