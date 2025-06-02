#!/bin/bash
set -e

# Funkcja pomocnicza
push_image() {
  local local_tag="$1"
  local remote_tag="$2"
  echo "Tagowanie obrazu $local_tag jako $remote_tag"
  docker tag "$local_tag" "$remote_tag"
  echo "Wysyłanie $remote_tag do Docker Hub..."
  docker push "$remote_tag"
}

echo "Wybierz obraz do pushowania:"
echo "1) hexapod-prod (prod)"
echo "2) hexapod-dev (dev)"
echo "3) oba"
read -p "Twój wybór [1/2/3]: " choice

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
    echo "Nieprawidłowy wybór."
    exit 1
    ;;
esac

echo "Gotowe."
