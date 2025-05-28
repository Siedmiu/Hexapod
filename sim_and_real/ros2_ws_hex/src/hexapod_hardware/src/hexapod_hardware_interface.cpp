#include "hexapod_hardware/hexapod_hardware_interface.hpp"

#include <chrono>
#include <cmath>
#include <limits>
#include <memory>
#include <vector>
#include <unordered_map>

// DODANE: Biblioteki do komunikacji szeregowej
#include <fcntl.h>      // open()
#include <unistd.h>     // close(), write(), read()
#include <termios.h>    // struktury do konfiguracji portu
#include <errno.h>      // obsługa błędów
#include <cstring>      // strerror()

#include "hardware_interface/types/hardware_interface_type_values.hpp"
#include "rclcpp/rclcpp.hpp"

namespace hexapod_hardware
{

hardware_interface::CallbackReturn HexapodHardwareInterface::on_init(
  const hardware_interface::HardwareInfo & info)
{
  if (hardware_interface::SystemInterface::on_init(info) != hardware_interface::CallbackReturn::SUCCESS)
  {
    return hardware_interface::CallbackReturn::ERROR;
  }

  // Odczytaj parametry z URDF
  port_name_ = info_.hardware_parameters["port_name"];
  baud_rate_ = std::stoi(info_.hardware_parameters["baud_rate"]);

  RCLCPP_INFO(rclcpp::get_logger("HexapodHardwareInterface"), 
    "Port: %s, Baud: %d", port_name_.c_str(), baud_rate_);

  // Zainicjalizuj wektory dla 18 stawów
  hw_positions_.resize(info_.joints.size(), 0.0);
  hw_velocities_.resize(info_.joints.size(), 0.0);
  hw_commands_.resize(info_.joints.size(), 0.0);

  // DODANE: Inicjalizacja zmiennych UART
  serial_fd_ = -1;
  serial_connected_ = false;

  // DODANE: Inicjalizacja mapowania joint → servo
  initializeJointMapping();

  // DODANE: Cache dla optymalizacji
  last_sent_commands_.resize(info_.joints.size(), std::numeric_limits<double>::quiet_NaN());
  command_tolerance_ = 0.01;  // 0.01 radiany = ~0.57°

  RCLCPP_INFO(rclcpp::get_logger("HexapodHardwareInterface"), 
    "Initialized with %zu joints", info_.joints.size());

  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn HexapodHardwareInterface::on_activate(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(rclcpp::get_logger("HexapodHardwareInterface"), "Activating hardware interface");
  
  // DODANE: Otwórz port szeregowy
  if (!openSerialPort()) {
    RCLCPP_ERROR(rclcpp::get_logger("HexapodHardwareInterface"), 
      "Failed to open serial port %s", port_name_.c_str());
    return hardware_interface::CallbackReturn::ERROR;
  }

  RCLCPP_INFO(rclcpp::get_logger("HexapodHardwareInterface"), 
    "Serial port %s opened successfully", port_name_.c_str());
  
  // Na razie symuluj pozycje początkowe (joint3_* = 60°)
  for (size_t i = 0; i < info_.joints.size(); ++i)
  {
    if (info_.joints[i].name.find("joint3_") != std::string::npos)
    {
      hw_positions_[i] = 1.047;  // 60 stopni w radianach
      hw_commands_[i] = 1.047;
    }
    else
    {
      hw_positions_[i] = 0.0;
      hw_commands_[i] = 0.0;
    }
  }

  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn HexapodHardwareInterface::on_deactivate(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(rclcpp::get_logger("HexapodHardwareInterface"), "Deactivating hardware interface");
  
  // DODANE: Zamknij port szeregowy
  closeSerialPort();
  
  return hardware_interface::CallbackReturn::SUCCESS;
}

std::vector<hardware_interface::StateInterface> HexapodHardwareInterface::export_state_interfaces()
{
  std::vector<hardware_interface::StateInterface> state_interfaces;
  
  for (size_t i = 0; i < info_.joints.size(); ++i)
  {
    state_interfaces.emplace_back(hardware_interface::StateInterface(
      info_.joints[i].name, hardware_interface::HW_IF_POSITION, &hw_positions_[i]));
    state_interfaces.emplace_back(hardware_interface::StateInterface(
      info_.joints[i].name, hardware_interface::HW_IF_VELOCITY, &hw_velocities_[i]));
  }

  return state_interfaces;
}

std::vector<hardware_interface::CommandInterface> HexapodHardwareInterface::export_command_interfaces()
{
  std::vector<hardware_interface::CommandInterface> command_interfaces;
  
  for (size_t i = 0; i < info_.joints.size(); ++i)
  {
    command_interfaces.emplace_back(hardware_interface::CommandInterface(
      info_.joints[i].name, hardware_interface::HW_IF_POSITION, &hw_commands_[i]));
  }

  return command_interfaces;
}

hardware_interface::return_type HexapodHardwareInterface::read(
  const rclcpp::Time & /*time*/, const rclcpp::Duration & /*period*/)
{
  // Na razie symuluj że pozycje actual = commanded
  for (size_t i = 0; i < hw_positions_.size(); ++i)
  {
    hw_positions_[i] = hw_commands_[i];  // Symulacja: pozycja = komenda
    hw_velocities_[i] = 0.0;             // Brak pomiary prędkości
  }

  return hardware_interface::return_type::OK;
}

hardware_interface::return_type HexapodHardwareInterface::write(
  const rclcpp::Time & /*time*/, const rclcpp::Duration & /*period*/)
{
  if (!serial_connected_) {
    return hardware_interface::return_type::ERROR;
  }

  // NOWE: Iteruj przez wszystkie stawy i wyślij komendy
  for (size_t i = 0; i < hw_commands_.size(); ++i)
  {
    // 1. Sprawdź czy komenda się zmieniła znacząco
    if (!shouldSendCommand(i, hw_commands_[i])) {
      continue;
    }

    // 2. Pobierz nazwę stawu
    std::string joint_name = info_.joints[i].name;

    // 3. Sprawdź czy mamy mapowanie dla tego stawu
    // if (joint_to_servo_map_.find(joint_name) == joint_to_servo_map_.end()) {
    //   RCLCPP_WARN_THROTTLE(
    //     rclcpp::get_logger("HexapodHardwareInterface"), 
    //     rclcpp::Clock(), 5000,
    //     "No servo mapping for joint: %s", joint_name.c_str());
    //   continue;
    // }

    // 4. Konwertuj ROS angle → servo degrees
    int servo_degrees = convertRadiansToServoDegrees(joint_name, hw_commands_[i]);
    
    // 5. Pobierz numer serwa
    int servo_number = joint_to_servo_map_[joint_name];
    
    // 6. Wyślij komendę
    if (sendServoCommand(servo_number, servo_degrees)) {
      last_sent_commands_[i] = hw_commands_[i];  // Cache
      
      RCLCPP_DEBUG(rclcpp::get_logger("HexapodHardwareInterface"),
                   "Joint %s (servo %d): %.3f rad → %d°", 
                   joint_name.c_str(), servo_number, hw_commands_[i], servo_degrees);
    } else {
      RCLCPP_WARN(rclcpp::get_logger("HexapodHardwareInterface"), 
                  "Failed to send command for %s", joint_name.c_str());
    }
  }

  return hardware_interface::return_type::OK;
}

// DODANE: Inicjalizacja mapowania joint → servo
void HexapodHardwareInterface::initializeJointMapping()
{
  // Mapowanie zgodne z ESP32
  joint_to_servo_map_ = {
    {"joint1_3", 0},  {"joint2_3", 1},  {"joint3_3", 2},
    {"joint1_2", 3},  {"joint2_2", 4},  {"joint3_2", 5},
    {"joint1_1", 6},  {"joint2_1", 7},  {"joint3_1", 8},
    {"joint1_6", 9},  {"joint2_6", 10}, {"joint3_6", 11},
    {"joint1_5", 12}, {"joint2_5", 13}, {"joint3_5", 14},
    {"joint1_4", 15}, {"joint2_4", 16}, {"joint3_4", 17}
  };

  RCLCPP_INFO(rclcpp::get_logger("HexapodHardwareInterface"), 
              "Initialized joint→servo mapping for %zu joints", joint_to_servo_map_.size());
}

// DODANE: Konwersja radiany → stopnie serwa
int HexapodHardwareInterface::convertRadiansToServoDegrees(const std::string& joint_name, double angle_rad)
{
  // Konwersja na stopnie
  double deg = angle_rad * 180.0 / M_PI;
  
  int servo_degrees;
  
  if (joint_name.find("joint1_") != std::string::npos) {
    // joint1_*: [-45°, +45°] → [0°, 180°]
    servo_degrees = static_cast<int>((deg + 45.0) * (180.0 / 90.0));
  }
  else if (joint_name.find("joint2_") != std::string::npos) {
    // joint2_*: [-60°, +60°] → [0°, 180°] 
    servo_degrees = static_cast<int>((deg + 60.0) * (180.0 / 120.0));
  }
  else if (joint_name.find("joint3_") != std::string::npos) {
    // joint3_*: [0°, +90°] → [0°, 180°]
    servo_degrees = static_cast<int>(deg * (180.0 / 90.0));
  }
  else {
    RCLCPP_WARN(rclcpp::get_logger("HexapodHardwareInterface"), 
                "Unknown joint type: %s, using 90°", joint_name.c_str());
    return 90;
  }
  
  // Ograniczenie do bezpiecznego zakresu
  servo_degrees = std::max(0, std::min(180, servo_degrees));
  
  return servo_degrees;
}

// DODANE: Sprawdź czy wysyłać komendę
bool HexapodHardwareInterface::shouldSendCommand(size_t joint_index, double new_command)
{
  // Sprawdź czy to pierwsza komenda
  if (std::isnan(last_sent_commands_[joint_index])) {
    return true;
  }
  
  // Sprawdź czy zmiana jest wystarczająco duża
  double change = std::abs(new_command - last_sent_commands_[joint_index]);
  return change >= command_tolerance_;
}

// DODANE: Wyślij komendę do konkretnego serwa
bool HexapodHardwareInterface::sendServoCommand(int servo_number, int angle_degrees)
{
  std::string command = "servo" + std::to_string(servo_number) + 
                       " " + std::to_string(angle_degrees) + "\n";
  
  return sendSerialData(command);
}

// DODANE: Metoda do otwierania portu szeregowego
bool HexapodHardwareInterface::openSerialPort()
{
  // 1. Otwórz port szeregowy
  serial_fd_ = open(port_name_.c_str(), O_RDWR | O_NOCTTY | O_NDELAY);
  
  if (serial_fd_ == -1) {
    RCLCPP_ERROR(rclcpp::get_logger("HexapodHardwareInterface"), 
      "Cannot open port %s: %s", port_name_.c_str(), strerror(errno));
    return false;
  }

  // 2. Konfiguruj parametry portu
  struct termios options;
  
  // Pobierz obecne ustawienia
  if (tcgetattr(serial_fd_, &options) != 0) {
    RCLCPP_ERROR(rclcpp::get_logger("HexapodHardwareInterface"), 
      "Failed to get port attributes: %s", strerror(errno));
    close(serial_fd_);
    serial_fd_ = -1;
    return false;
  }

  // Ustaw prędkość transmisji (115200 baud)
  cfsetispeed(&options, B115200);
  cfsetospeed(&options, B115200);

  // Konfiguracja: 8 bitów danych, bez parity, 1 stop bit
  options.c_cflag &= ~PARENB;  // Bez parity
  options.c_cflag &= ~CSTOPB;  // 1 stop bit
  options.c_cflag &= ~CSIZE;   // Wyczyść maskę rozmiaru
  options.c_cflag |= CS8;      // 8 bitów danych
  options.c_cflag |= CREAD;    // Włącz odczyt
  options.c_cflag |= CLOCAL;   // Ignoruj linie kontrolne modemu

  // Raw mode (bez przetwarzania znaków)
  options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
  options.c_iflag &= ~(IXON | IXOFF | IXANY);
  options.c_oflag &= ~OPOST;

  // Timeout: 0 (non-blocking)
  options.c_cc[VTIME] = 0;
  options.c_cc[VMIN] = 0;

  // Zastosuj ustawienia
  if (tcsetattr(serial_fd_, TCSANOW, &options) != 0) {
    RCLCPP_ERROR(rclcpp::get_logger("HexapodHardwareInterface"), 
      "Failed to set port attributes: %s", strerror(errno));
    close(serial_fd_);
    serial_fd_ = -1;
    return false;
  }

  // Opróżnij bufory
  tcflush(serial_fd_, TCIOFLUSH);

  serial_connected_ = true;
  return true;
}

// DODANE: Metoda do zamykania portu
void HexapodHardwareInterface::closeSerialPort()
{
  if (serial_fd_ != -1) {
    close(serial_fd_);
    serial_fd_ = -1;
    serial_connected_ = false;
    RCLCPP_INFO(rclcpp::get_logger("HexapodHardwareInterface"), 
      "Serial port closed");
  }
}

// DODANE: Metoda do wysyłania danych
bool HexapodHardwareInterface::sendSerialData(const std::string& data)
{
  if (!serial_connected_ || serial_fd_ == -1) {
    return false;
  }

  ssize_t bytes_written = ::write(serial_fd_, data.c_str(), data.length());
  
  if (bytes_written < 0) {
    RCLCPP_ERROR(rclcpp::get_logger("HexapodHardwareInterface"), 
      "Serial write error: %s", strerror(errno));
    serial_connected_ = false;
    return false;
  }

  if (static_cast<size_t>(bytes_written) != data.length()) {
    RCLCPP_WARN(rclcpp::get_logger("HexapodHardwareInterface"), 
      "Partial write: %zd/%zu bytes", bytes_written, data.length());
    return false;
  }

  return true;
}

}  // namespace hexapod_hardware

// Rejestracja pluginu
#include "pluginlib/class_list_macros.hpp"
PLUGINLIB_EXPORT_CLASS(
  hexapod_hardware::HexapodHardwareInterface, hardware_interface::SystemInterface)