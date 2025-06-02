#!/bin/bash

echo "===== Diagnostyka GPU dla kontenerów Docker Hexapod ====="
echo ""

echo "=== Informacje o systemie ==="
echo "Nazwa hosta: $(hostname)"
echo "Jądro: $(uname -r)"
echo "Dystrybucja: $(cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 | tr -d '"')"
echo ""

echo "=== Zmienne środowiskowe związane z grafiką ==="
echo "DISPLAY: $DISPLAY"
echo "XDG_RUNTIME_DIR: $XDG_RUNTIME_DIR"
echo "LIBGL_ALWAYS_SOFTWARE: $LIBGL_ALWAYS_SOFTWARE"
echo "NVIDIA_VISIBLE_DEVICES: $NVIDIA_VISIBLE_DEVICES"
echo "NVIDIA_DRIVER_CAPABILITIES: $NVIDIA_DRIVER_CAPABILITIES"
echo "__NV_PRIME_RENDER_OFFLOAD: $__NV_PRIME_RENDER_OFFLOAD"
echo "__GLX_VENDOR_LIBRARY_NAME: $__GLX_VENDOR_LIBRARY_NAME"
echo ""

echo "=== Urządzenia PCI ==="
if command -v lspci > /dev/null; then
  lspci | grep -E "VGA|3D|Display" || echo "Nie znaleziono urządzeń graficznych PCI"
else
  echo "Brak narzędzia lspci"
fi
echo ""

echo "=== Urządzenia w /dev/dri ==="
ls -la /dev/dri/ 2>/dev/null || echo "Brak katalogu /dev/dri/"
echo ""

echo "=== Montowanie urządzeń NVIDIA ==="
ls -la /dev/nvidia* 2>/dev/null || echo "Brak urządzeń NVIDIA"
echo ""

echo "=== Biblioteki NVIDIA ==="
echo "Sprawdzanie bibliotek NVIDIA w systemie..."
ldconfig -p | grep -i nvidia || echo "Nie znaleziono bibliotek NVIDIA w systemie"
echo ""
 
echo "=== Test OpenGL ==="
if command -v glxinfo > /dev/null; then
  echo "Renderer OpenGL:"
  glxinfo | grep -E "OpenGL renderer|direct rendering" || echo "Nie znaleziono informacji o rendererze OpenGL"
  echo ""
  echo "Wersja OpenGL:"
  glxinfo | grep "OpenGL version" || echo "Nie znaleziono informacji o wersji OpenGL"
  echo ""
  echo "Informacje o dostawcy OpenGL:"
  glxinfo | grep -E "OpenGL vendor|OpenGL implementation" || echo "Nie znaleziono informacji o dostawcy OpenGL"
else
  echo "Brak narzędzia glxinfo"
fi
echo ""

echo "=== Sprawdzanie akceleracji sprzętowej ==="
if command -v glxgears > /dev/null; then
  echo "Uruchamianie glxgears na 3 sekundy..."
  timeout 3s glxgears 2>&1 | grep -i "fps" || echo "Brak informacji o FPS"
else
  echo "Brak narzędzia glxgears"
fi
echo ""

if command -v glmark2 > /dev/null; then
  echo "Uruchamianie krótkiego testu glmark2..."
  glmark2 --size 800,600 --benchmark builtin:duration=2.0 || echo "Test glmark2 nie powiódł się"
else
  echo "Brak narzędzia glmark2"
fi
echo ""

if command -v nvidia-smi > /dev/null; then
  echo "=== Informacje o GPU NVIDIA ==="
  nvidia-smi || echo "nvidia-smi zakończył się błędem"
  echo ""
elif [ -f /proc/driver/nvidia/version ]; then
  echo "Sterownik NVIDIA jest zainstalowany, ale brak narzędzia nvidia-smi"
  cat /proc/driver/nvidia/version
  echo ""
fi

if command -v radeontop > /dev/null && (lspci | grep -iq amd || lspci | grep -iq radeon); then
  echo "=== Informacje o GPU AMD ==="
  echo "Wykryto kartę AMD. Możesz ręcznie uruchomić: radeontop -d"
  echo ""
elif command -v radeontop > /dev/null; then
  echo "Narzędzie radeontop jest dostępne, ale nie wykryto karty AMD"
  echo ""
fi

# Test wydajności Gazebo (jeśli dostępne)
if command -v gz > /dev/null; then
  echo "=== Test wydajności Gazebo ==="
  echo "Uruchamianie testu wydajności Gazebo..."
  timeout 5s gz sim -v 4 -r -s || echo "Test Gazebo nie powiódł się"
  echo ""
fi

echo "===== Diagnostyka zakończona ====="
echo ""
echo "Wskazówki:"
echo "1. Jeśli 'OpenGL renderer' pokazuje 'llvmpipe', to oznacza renderowanie programowe, a nie sprzętowe."
echo "2. Dla kart NVIDIA sprawdź, czy nvidia-smi pokazuje procesy wykorzystujące GPU."
echo "3. Dla kart AMD/Intel, sprawdź czy OpenGL renderer pokazuje nazwę twojej karty graficznej."
echo "4. Jeśli nie widzisz poprawy wydajności, spróbuj:"
echo "   - Uruchomić 'xhost +' na hoście przed uruchomieniem kontenera"
echo "   - Sprawdzić czy użytkownik należy do grupy 'video' i 'render'"
echo "   - Uruchomić 'sudo nvidia-smi' na hoście, aby sprawdzić czy karta działa"
echo "   - Sprawdzić czy sterowniki NVIDIA są zainstalowane poprawnie: 'nvidia-settings'"
echo ""
echo "Aby naprawić problem z renderowaniem programowym, spróbuj:"
echo "1. Dodać użytkownika do grup 'video' i 'render': sudo usermod -aG video,render \$USER"
echo "2. Uruchomić 'xhost +' na hoście przed startem kontenera"
echo "3. Sprawdzić konfigurację X11: 'xrandr --listproviders'"
echo "4. Uruchomić 'sudo prime-select nvidia' na hoście (jeśli masz grafikę hybrydową)"
echo ""
echo "Aby sprawdzić wykorzystanie GPU podczas działania symulacji, uruchom w osobnym terminalu:"
echo "- Dla NVIDIA: sudo nvidia-smi --query-gpu=utilization.gpu --format=csv -l 1"
echo ""