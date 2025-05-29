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
- Zawiera kompletną konfigurację systemu, ROS2 oraz zależności potrzebne do symulacji.
- Przeznaczony jest do wdrożeń i prezentacji stabilnej wersji aplikacji.
- Uruchamiany zwykle z interfejsem graficznym (GUI) wspomaganym przez X11.

Kontener deweloperski (oparty na Dockerfile.dev):
- Uruchamia interaktywną powłokę (bash) dla łatwego debugowania i testowania.
- Montuje lokalny katalog roboczy, umożliwiając modyfikację kodu bez przebudowy obrazu.
- Skonfigurowany głównie do pracy developerskiej z szybkimi iteracjami zmian w kodzie.

## Sposób użycia

1. Aby zbudować i uruchomić kontener produkcyjny, wykonaj (w razie problemów użyj sudo):
   - `sudo ./setup-prod.sh` – budowanie obrazu i uruchomienie Gazebo.
   - `sudo ./setup-prod.sh moveit` – budowanie obrazu i uruchomienie MoveIt.
   - `sudo ./setup-import-prod.sh` – import obrazu produkcyjnego z pliku .tar (dostępny wkrótce).

2. Aby zbudować środowisko deweloperskie, wykonaj (w razie problemów użyj sudo):
   - `sudo ./setup-dev.sh` – pobranie repozytorium, budowa workspace i uruchomienie kontenera deweloperskiego.
     - Uwaga: Jeśli przy pierwszym uruchomieniu pojawi się komunikat:
       "bash: line 1: /opt/ros/jazzy/setup.bash: No such file or directory"
       uruchom skrypt ponownie.
   - `sudo ./setup-import-dev.sh` – import obrazu deweloperskiego z pliku .tar (dostępny wkrótce).

3. Wewnątrz środowiska deweloperskiego możesz uruchomić:
   - Uruchomienie Gazebo:
     - `ros2 launch hex_gz gazebo.launch.py`
   - Uruchomienie RViz/MoveIt:
     - `ros2 launch hexapod_moveit_config demo.launch.py`

3. Eksport i import obrazu Dockera (opcjonalnie):
   - Aby wyeksportować obraz produkcyjny do pliku .tar, wykonaj:
     - `sudo docker save -o hexapod-prod.tar hexapod-prod`
     - lub analogicznie dla obrazu deweloperskiego:
     - `sudo docker save -o hexapod-dev.tar hexapod-dev`
   - Aby zaimportować obraz na innej maszynie, wykonaj:
     - `sudo docker load -i hexapod-prod.tar` 
     - lub analogicznie 
     - `sudo docker load -i hexapod-prod.tar`

## Dodatkowe informacje i wskazówki

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
- setup-import-prod.sh: Importuje obraz produkcyjny z pliku hexapod-prod.tar i uruchamia kontener.
- setup-dev.sh: Buduje obraz deweloperski przy użyciu Dockerfile.dev z zamontowanym katalogiem projektu i uruchamia kontener.
- setup-import-dev.sh: Importuje obraz deweloperski z pliku hexapod-dev.tar i uruchamia kontener.

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

### Aktualizacja kodu projektu

Aby zaktualizować kod projektu w środowisku produkcyjnym bez pełnego przebudowania obrazu:
```bash
./setup-prod.sh pull
```

Ta opcja:
- Pobiera najnowsze zmiany z repozytorium GitHub
- Przebudowuje workspace ROS2 z nowymi zmianami
- Kopiuje zaktualizowany kod z kontenera do katalogu hosta
- Pozwala na szybkie testowanie nowych wersji bez długiego procesu budowania obrazu
