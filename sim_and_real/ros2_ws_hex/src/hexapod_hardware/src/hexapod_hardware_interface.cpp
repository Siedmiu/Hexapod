#include "hexapod_hardware/hexapod_hardware_interface.hpp"

#include <chrono>
#include <cmath>
#include <limits>
#include <memory>
#include <vector>

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

  RCLCPP_INFO(rclcpp::get_logger("HexapodHardwareInterface"), 
    "Initialized with %zu joints", info_.joints.size());

  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn HexapodHardwareInterface::on_activate(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  RCLCPP_INFO(rclcpp::get_logger("HexapodHardwareInterface"), "Activating hardware interface");
  
  // TODO: Otwórz komunikację z ESP32
  // serial_ = std::make_unique<SerialCommunication>(port_name_, baud_rate_);
  
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
  
  // TODO: Zamknij komunikację z ESP32
  // serial_.reset();
  
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
  // TODO: Odczytaj rzeczywiste pozycje z ESP32
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
  // TODO: Wyślij komendy do ESP32
  // Na razie tylko loguj co kilka sekund
  static auto last_log = std::chrono::steady_clock::now();
  auto now = std::chrono::steady_clock::now();
  
  if (std::chrono::duration_cast<std::chrono::seconds>(now - last_log).count() >= 2)
  {
    RCLCPP_INFO(rclcpp::get_logger("HexapodHardwareInterface"), 
      "Commands: [%.3f, %.3f, %.3f, ...]", 
      hw_commands_[0], hw_commands_[1], hw_commands_[2]);
    last_log = now;
  }

  return hardware_interface::return_type::OK;
}

}  // namespace hexapod_hardware

// Rejestracja pluginu
#include "pluginlib/class_list_macros.hpp"
PLUGINLIB_EXPORT_CLASS(
  hexapod_hardware::HexapodHardwareInterface, hardware_interface::SystemInterface)