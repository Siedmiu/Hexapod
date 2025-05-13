# ========================================== Narzędzie: get\_inertia – obliczanie tensoru bezwładności z plików STL

Oryginalne narzędzie `get_inertia` zostało stworzone przez Guido Bocchio i jest dostępne w repozytorium: [https://github.com/bocchio/get\_inertia](https://github.com/bocchio/get_inertia)

Narzędzie służy do obliczania macierzy bezwładności (inercji) dla obiektów zapisanych w plikach STL 3D.

---

## Modyfikacje wprowadzone w tej wersji (2025):

W ramach własnego projektu dokonałam modyfikacji kodu:

1. **Usunięto ograniczenie wyboru dla argumentu "-r/--reference"**, aby umożliwić podanie dowolnych współrzędnych w formacie `x, y, z`.
2. **Naprawiono zależności** – zaktualizowano lub poprawiono sposób importowania bibliotek wymaganych przez skrypt, m.in. `pint`.

Zmodyfikowany kod oraz oryginalna licencja znajdują się w tym folderze.

---

## Jak korzystać z narzędzia

### Uruchamianie programu

Program można uruchomić z linii poleceń w następujący sposób:

```
python3 get_inertia [opcje] <ścieżka_do_pliku.stl>
```

### Dostępne opcje

* `-f`, `--format`: Format wyjścia tensora bezwładności. Dostępne opcje:

  * `text` (domyślnie): Wyświetla tensor w formacie tekstowym.
  * `urdf`: Wyświetla tensor w formacie URDF (używanym w robotyce).

* `-u`, `--units`: Jednostki długości modelu STL. Domyślnie: `meters`.

* `-s`, `--scale`: Współczynnik skali modelu STL. Domyślnie: `1.0`.

* `-m`, `--mass`: Masa całkowita modelu STL w kilogramach. Domyślnie: `1.0`.

* `-r`, `--reference`: Punkt odniesienia, względem którego tensor bezwładności jest obliczany. Można podać:

  * `center of mass` lub `cog`: Środek masy modelu.
  * Współrzędne w formacie `x, y, z` (np. "1, 0, 0").

* `<ścieżka_do_pliku.stl>`: Ścieżka do pliku STL, który ma zostać przetworzony.

### Przykład użycia

```
python3 get_inertia -m 2.5 -u meters -s 1.0 -f urdf -r "1, 0, 0" Hexapod_Leg.stl
```

---

## Licencja: Clear BSD License

Copyright (c) \ [2021] Guido Bocchio
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the limitations in the disclaimer below) provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

---

## Autorzy:

* Oryginalny autor: **Guido Bocchio**
* Zmiany i adaptacja: **Paulina Lokś**

