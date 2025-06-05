#!/bin/bash

echo "===== GPU Diagnostics for Hexapod Docker Containers ====="
echo ""

echo "=== System Information ==="
echo "Hostname: $(hostname)"
echo "Kernel: $(uname -r)"
echo "Distribution: $(grep PRETTY_NAME /etc/os-release | cut -d= -f2 | tr -d '\"')"
echo ""

echo "=== Graphics Environment Variables ==="
echo "DISPLAY: $DISPLAY"
echo "XDG_RUNTIME_DIR: $XDG_RUNTIME_DIR"
echo "LIBGL_ALWAYS_SOFTWARE: $LIBGL_ALWAYS_SOFTWARE"
echo "NVIDIA_VISIBLE_DEVICES: $NVIDIA_VISIBLE_DEVICES"
echo "NVIDIA_DRIVER_CAPABILITIES: $NVIDIA_DRIVER_CAPABILITIES"
echo "__NV_PRIME_RENDER_OFFLOAD: $__NV_PRIME_RENDER_OFFLOAD"
echo "__GLX_VENDOR_LIBRARY_NAME: $__GLX_VENDOR_LIBRARY_NAME"
echo ""

echo "=== PCI Devices ==="
if command -v lspci > /dev/null; then
  lspci | grep -E "VGA|3D|Display" || echo "No PCI graphics devices found"
else
  echo "lspci tool is not available"
fi
echo ""

echo "=== /dev/dri Devices ==="
ls -la /dev/dri/ 2>/dev/null || echo "No /dev/dri/ directory"
echo ""

echo "=== NVIDIA device mounts ==="
ls -la /dev/nvidia* 2>/dev/null || echo "No NVIDIA devices"
echo ""

echo "=== NVIDIA Libraries ==="
echo "Checking NVIDIA libraries on system..."
ldconfig -p | grep -i nvidia || echo "No NVIDIA libraries found"
echo ""
 
echo "=== OpenGL Test ==="
echo "Renderer OpenGL:"
if command -v glxinfo > /dev/null; then
  glxinfo | grep -E "OpenGL renderer|direct rendering" || echo "No OpenGL renderer information found"
else
  echo "glxinfo tool is not available"
fi
echo ""

echo "=== OpenGL Version ==="
if command -v glxinfo > /dev/null; then
  glxinfo | grep "OpenGL version" || echo "No OpenGL version information found"
else
  echo "glxinfo tool is not available"
fi
echo ""

echo "=== OpenGL Vendor Information ==="
if command -v glxinfo > /dev/null; then
  glxinfo | grep -E "OpenGL vendor|OpenGL implementation" || echo "No OpenGL vendor information found"
else
  echo "glxinfo tool is not available"
fi
echo ""

echo "=== Hardware Acceleration Check ==="
echo "Running glxgears for 3 seconds..."
if command -v glxgears > /dev/null; then
  timeout 3s glxgears 2>&1 | grep -i "fps" || echo "No FPS information"
else
  echo "glxgears tool is not available"
fi
echo ""

echo "=== glmark2 Test ==="
if command -v glmark2 > /dev/null; then
  echo "Running short glmark2 test..."
  glmark2 --size 800,600 --benchmark builtin:duration=2.0 || echo "glmark2 test failed"
else
  echo "glmark2 tool is not available"
fi
echo ""

echo "=== NVIDIA GPU Information ==="
if command -v nvidia-smi > /dev/null; then
  nvidia-smi || echo "nvidia-smi exited with an error"
  echo ""
elif [ -f /proc/driver/nvidia/version ]; then
  echo "NVIDIA driver is installed, but nvidia-smi is not available"
  cat /proc/driver/nvidia/version
  echo ""
fi

echo "=== AMD GPU Information ==="
if command -v radeontop > /dev/null && (lspci | grep -iq amd || lspci | grep -iq radeon); then
  echo "Detected AMD card. You can manually run: radeontop -d"
  echo ""
elif command -v radeontop > /dev/null; then
  echo "radeontop tool is available, but no AMD card detected"
  echo ""
fi

echo "=== Gazebo Performance Test ==="
if command -v gz > /dev/null; then
  echo "Running Gazebo performance test..."
  timeout 5s gz sim -v 4 -r -s || echo "Gazebo test failed"
  echo ""
fi

echo "===== Diagnostics Completed ====="
echo ""
echo "Tips:"
echo "1. If 'OpenGL renderer' shows 'llvmpipe', it means software rendering, not hardware."
echo "2. For NVIDIA cards, check if nvidia-smi shows GPU-using processes."
echo "3. For AMD/Intel, verify OpenGL renderer shows your GPU name."
echo "4. If performance does not improve, try:"
echo "   - Run 'xhost +' on the host before starting the container"
echo "   - Ensure user belongs to 'video' and 'render' groups"
echo "   - Run 'sudo nvidia-smi' on the host to verify GPU functionality"
echo "   - Check NVIDIA driver installation: 'nvidia-settings'"
echo ""
echo "To fix software rendering issues, try:"
echo "1. Add user to 'video' and 'render' groups: sudo usermod -aG video,render \$USER"
echo "2. Run 'xhost +' on host before container startup"
echo "3. Check X11 configuration: 'xrandr --listproviders'"
echo "4. Run 'sudo prime-select nvidia' on the host (if using hybrid graphics)"
echo ""
echo "To monitor GPU usage during simulation, run in another terminal:"
echo "- For NVIDIA: sudo nvidia-smi --query-gpu=utilization.gpu --format=csv -l 1"
echo ""