# README - Hexapod

## Wprowadzenie

Docker to narzędzie do wirtualizacji kontenerów, które umożliwia uruchamianie aplikacji w izolowanym środowisku, podobnie do maszyny wirtualnej, lecz z mniejszym narzutem i lepszą integracją z systemem operacyjnym. Dzięki Dockerowi ten projekt:
- Umożliwia łatwe budowanie spójnych środowisk produkcyjnych i deweloperskich,
- Izoluje zależności oprogramowania,
- Ułatwia przełączanie się między różnymi konfiguracjami bez wpływu na system hosta.
- Wspiera środowiska MoveIt/RViz obok symulacji w Gazebo.

# Dockeryzacja projektu

## Różnice między kontenerem produkcyjnym a deweloperskim

Kontener produkcyjny (oparty na Dockerfile.prod):
- Uruchamia aplikację lub symulację automatycznie po starcie. Domyślnie startuje symulacja w Gazebo, tryb MoveIt/RViz aktywowany argumentem "moveit"
- Automatycznie aktualizuje repozytorium do najnowszej wersji przy każdym uruchomieniu
- Zawiera kompletną konfigurację systemu, ROS2 oraz zależności potrzebne do symulacji.
- Przeznaczony jest do wdrożeń i prezentacji stabilnej wersji aplikacji.
- Uruchamiany zwykle z interfejsem graficznym (GUI) wspomaganym przez X11.

Kontener deweloperski (oparty na Dockerfile.dev):
- Uruchamia interaktywną powłokę (bash) dla łatwego debugowania i testowania.
- Montuje lokalny katalog roboczy (`Hexapod-ROS2-System`), umożliwiając modyfikację kodu bez przebudowy obrazu.
- Skonfigurowany głównie do pracy developerskiej z szybkimi iteracjami zmian w kodzie.

## Sposób użycia

1. Aby zbudować i uruchomić kontener produkcyjny, wykonaj (w razie problemów użyj sudo):
   - `sudo ./setup-prod.sh` – budowanie obrazu i uruchomienie Gazebo.
   - `sudo ./setup-prod.sh moveit` – budowanie obrazu i uruchomienie MoveIt.
   - `sudo ./setup-import-prod.sh` – pobieranie obrazu produkcyjnego z Docker Hub.

2. Aby zbudować środowisko deweloperskie, wykonaj (w razie problemów użyj sudo):
   - `sudo ./setup-dev.sh` – pobranie repozytorium, budowa workspace i uruchomienie kontenera deweloperskiego.
   - `sudo ./setup-import-dev.sh` – pobieranie obrazu deweloperskiego z Docker Hub.

**Uwaga:** Kontener produkcyjny automatycznie pobiera najnowsze zmiany z repozytorium przy każdym uruchomieniu. Kontener deweloperski używa lokalnego kodu z zamontowanego katalogu.

3. Wewnątrz środowiska deweloperskiego możesz uruchomić:
   - Uruchomienie Gazebo:
     - `ros2 launch hex_gz gazebo.launch.py`
   - Uruchomienie RViz/MoveIt:
     - `ros2 launch hexapod_moveit_config demo.launch.py`

3. Docker Hub vs lokalne budowanie:
   - **Skrypty setup-prod.sh i setup-dev.sh**: Budują obrazy lokalnie z najnowszym kodem repozytorium [Hexapod-ROS2-System](https://github.com/Siedmiu/Hexapod-ROS2-System)
   - **Skrypty setup-import-prod.sh i setup-import-dev.sh**: Pobierają gotowe obrazy z Docker Hub (`natantulo/hexapod:prod` i `natantulo/hexapod:dev`)
   - **Eksport lokalny** (opcjonalnie):
     - `sudo docker save -o hexapod-prod.tar hexapod-prod`
     - `sudo docker save -o hexapod-dev.tar hexapod-dev`
     - `sudo docker load -i hexapod-prod.tar`

## Dodatkowe informacje i wskazówki

- **Uprawnienia skryptów**: Jeśli wystąpi błąd "Permission denied", nadaj uprawnienia wykonywania:
  ```bash
  chmod +x *.sh
  ```
- Aby korzystać z kontenerów graficznych, upewnij się, że polecenie `xhost +local:docker` jest wykonywane, co umożliwia dostęp do X11.
- W niektórych przypadkach po instalacji Dockera konieczne może być ponowne logowanie lub restart systemu, aby zmiany w grupach użytkowników zostały zastosowane.
- Skrypty wykorzystują sudo, co wymaga uprzedniego ustawienia odpowiednich uprawnień.
- Jeśli w eksploratorze plików widzisz ikonę kłódki przy pliku lub folderze, użyj polecenia:
  `sudo chown -R $USER:$USER <nazwa pliku/folderu>`
- Aby wyczyścić nieużywane dane budowy i systemu Dockera, można użyć:
  - `docker builder prune --all` – usuwa nieużywane dane builda.
  - `docker system prune --all --volumes` – usuwa nieużywane kontenery, obrazy, sieci i woluminy.
- Aby otworzyć dodatkowy terminal do uruchomionego kontenera:
  - Uruchom obraz jako kontener w tle: `docker run -d -it <image_id>`
  - Sprawdź identyfikator kontenera: `docker ps`
  - Otwórz pierwszy terminal i wykonaj: `docker exec -it <container_id> bash`
  - Następnie otwórz kolejny terminal i powtórz `docker exec ...`, aby uzyskać kolejny interaktywny dostęp.

## Skrypty

- setup-prod.sh: Buduje obraz produkcyjny przy użyciu Dockerfile.prod i uruchamia kontener z GUI.
- setup-import-prod.sh: Pobiera obraz produkcyjny z Docker Hub (natantulo/hexapod:prod) i uruchamia kontener.
- setup-dev.sh: Buduje obraz deweloperski przy użyciu Dockerfile.dev z zamontowanym katalogiem projektu i uruchamia kontener.
- setup-import-dev.sh: Pobiera obraz deweloperski z Docker Hub (natantulo/hexapod:dev) i uruchamia kontener.

## Dockerfile

- Dockerfile.prod: Definiuje środowisko produkcyjne z ROS2, Gazebo, MoveIt oraz dodatkowymi narzędziami.
- Dockerfile.dev: Definiuje środowisko deweloperskie, które automatycznie sourcuje potrzebne skrypty przy wejściu do terminala.

## Obsługa GPU

Skrypty automatycznie wykrywają dostępne karty graficzne (NVIDIA, AMD, Intel) i konfigurują kontener do wykorzystania akceleracji sprzętowej.

Aby ręcznie sprawdzić czy akceleracja graficzna działa poprawnie, możesz użyć argumentu `diagnose`:
```bash
./setup-prod.sh diagnose
./setup-dev.sh diagnose
```