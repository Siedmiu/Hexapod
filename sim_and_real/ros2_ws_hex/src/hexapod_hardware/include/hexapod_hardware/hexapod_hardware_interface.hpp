#ifndef HEXAPOD_HARDWARE__HEXAPOD_HARDWARE_INTERFACE_HPP_
#define HEXAPOD_HARDWARE__HEXAPOD_HARDWARE_INTERFACE_HPP_

#include <memory>
#include <string>
#include <vector>

#include "hardware_interface/handle.hpp"
#include "hardware_interface/hardware_info.hpp"
#include "hardware_interface/system_interface.hpp"
#include "hardware_interface/types/hardware_interface_return_values.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_lifecycle/node_interfaces/lifecycle_node_interface.hpp"
#include "rclcpp_lifecycle/state.hpp"

namespace hexapod_hardware
{
class HexapodHardwareInterface : public hardware_interface::SystemInterface
{
public:
  // Wymagane metody z SystemInterface
  hardware_interface::CallbackReturn on_init(
    const hardware_interface::HardwareInfo & info) override;

  hardware_interface::CallbackReturn on_activate(
    const rclcpp_lifecycle::State & previous_state) override;

  hardware_interface::CallbackReturn on_deactivate(
    const rclcpp_lifecycle::State & previous_state) override;

  std::vector<hardware_interface::StateInterface> export_state_interfaces() override;

  std::vector<hardware_interface::CommandInterface> export_command_interfaces() override;

  hardware_interface::return_type read(
    const rclcpp::Time & time, const rclcpp::Duration & period) override;

  hardware_interface::return_type write(
    const rclcpp::Time & time, const rclcpp::Duration & period) override;

private:
  // Parametry konfiguracji
  std::string port_name_;
  int baud_rate_;
  
  // Stany stawów (18 stawów = 6 nóg × 3 stawy)
  std::vector<double> hw_positions_;
  std::vector<double> hw_velocities_;
  std::vector<double> hw_commands_;
  
  // Komunikacja z ESP32 (do zaimplementowania później)
  // std::unique_ptr<SerialCommunication> serial_;
};

}  // namespace hexapod_hardware

#endif  // HEXAPOD_HARDWARE__HEXAPOD_HARDWARE_INTERFACE_HPP_