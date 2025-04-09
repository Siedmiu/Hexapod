# README - Hexapod

## Wprowadzenie

Docker to narzędzie do wirtualizacji kontenerów, które umożliwia uruchamianie aplikacji w izolowanym środowisku, podobnie do maszyny wirtualnej, lecz z mniejszym narzutem i lepszą integracją z systemem operacyjnym. Dzięki Dockerowi ten projekt:
- Umożliwia łatwe budowanie spójnych środowisk produkcyjnych i deweloperskich,
- Izoluje zależności oprogramowania,
- Ułatwia przełączanie się między różnymi konfiguracjami bez wpływu na system hosta.

# Dockeryzacja projektu

## Różnice między kontenerem produkcyjnym a deweloperskim

Kontener produkcyjny (oparty na Dockerfile.prod):
- Uruchamia aplikację lub symulację automatycznie po starcie.
- Zawiera kompletną konfigurację systemu, ROS2 oraz zależności potrzebne do symulacji.
- Przeznaczony jest do wdrożeń i prezentacji stabilnej wersji aplikacji.
- Uruchamiany zwykle z interfejsem graficznym (GUI) wspomaganym przez X11.

Kontener deweloperski (oparty na Dockerfile.dev):
- Uruchamia interaktywną powłokę (bash) dla łatwego debugowania i testowania.
- Montuje lokalny katalog roboczy, umożliwiając modyfikację kodu bez przebudowy obrazu.
- Skonfigurowany głównie do pracy developerskiej z szybkimi iteracjami zmian w kodzie.

## Sposób użycia

1. Aby zbudować i uruchomić kontener produkcyjny, wykonaj (w razie problemów użyj sudo):
   - `sudo ./setup-prod.sh` – budowanie obrazu.
   - `sudo ./setup-import-prod.sh` – import obrazu produkcyjnego z pliku .tar (dostępny wkrótce).

2. Aby zbudować środowisko deweloperskie, wykonaj (w razie problemów użyj sudo):
   - `sudo ./setup-dev.sh` – pobranie repozytorium, budowa workspace i uruchomienie kontenera deweloperskiego.
      - Uwaga: Jeśli przy pierwszym uruchomieniu pojawi się komunikat:
     "bash: line 1: /opt/ros/jazzy/setup.bash: No such file or directory"
     uruchom skrypt ponownie.
   - `sudo ./setup-import-dev.sh` – import obrazu deweloperskiego z pliku .tar (dostępny wkrótce).

3. Eksport i import obrazu Dockera (opcjonalnie):
   - Aby wyeksportować obraz produkcyjny do pliku .tar, wykonaj:
     - `sudo docker save -o hexapod-prod.tar hexapod-prod` 
     - lub analogicznie 
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

## Skrypty

### setup-prod.sh
- Buduje obraz produkcyjny przy użyciu Dockerfile.prod.
- Umożliwia uruchomienie kontenera produkcyjnego, który pozwala korzystać z interfejsu graficznego (X11).
- W komentarzach zawarto przykłady eksportu obrazu (docker save) oraz importu (docker load).

### setup-import-prod.sh
- Importuje obraz Docker z pliku `hexapod-prod.tar`.
- Po imporcie dopasowuje prawa do pliku obrazu, by użytkownik miał do niego pełny dostęp.
- Uruchamia kontener produkcyjny.

### setup-import-dev.sh
- Podobnie jak import prod, ale dla obrazu deweloperskiego (`hexapod-dev.tar`).
- Ustawia odpowiednie prawa dostępu do pliku obrazu.
- Uruchamia kontener deweloperski z woluminem montującym katalog roboczy.

### setup-dev.sh
- Aktualizuje system oraz instaluje Docker, o ile nie jest zainstalowany.
- Jeśli katalog Hexapod nie istnieje, klonuje repozytorium z GitHub i buduje workspace.
- Dopasowuje prawa dostępu do klastra repozytorium.
- Buduje obraz deweloperski z wykorzystaniem Dockerfile.dev.
- Uruchamia kontener deweloperski.

## Dockerfile

### Dockerfile.prod
- Definiuje środowisko produkcyjne.
- Instaluje zależności systemowe, ROS2, Gazebo oraz narzędzia budowlane.
- Klonuje repozytorium Hexapod, buduje workspace i ustawia automatyczne source'owanie środowiska.

### Dockerfile.dev
- Definiuje środowisko deweloperskie.
- Konfiguruje zawierające ROS2 i Gazebo środowisko, zapewniając łatwy dostęp do terminala (CMD ["/bin/bash"]).

---
