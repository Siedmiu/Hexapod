// auto-generated DO NOT EDIT

#pragma once

#include <algorithm>
#include <array>
#include <functional>
#include <limits>
#include <mutex>
#include <rclcpp/node.hpp>
#include <rclcpp_lifecycle/lifecycle_node.hpp>
#include <rclcpp/logger.hpp>
#include <set>
#include <sstream>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

#include <fmt/core.h>
#include <fmt/format.h>
#include <fmt/ranges.h>

#include <parameter_traits/parameter_traits.hpp>

#include <rsl/static_string.hpp>
#include <rsl/static_vector.hpp>
#include <rsl/parameter_validators.hpp>



namespace joint_trajectory_command_broadcaster {

// Use validators from RSL
using rsl::unique;
using rsl::subset_of;
using rsl::fixed_size;
using rsl::size_gt;
using rsl::size_lt;
using rsl::not_empty;
using rsl::element_bounds;
using rsl::lower_element_bounds;
using rsl::upper_element_bounds;
using rsl::bounds;
using rsl::lt;
using rsl::gt;
using rsl::lt_eq;
using rsl::gt_eq;
using rsl::one_of;
using rsl::to_parameter_result_msg;

// temporarily needed for backwards compatibility for custom validators
using namespace parameter_traits;

template <typename T>
[[nodiscard]] auto to_parameter_value(T value) {
    return rclcpp::ParameterValue(value);
}

template <size_t capacity>
[[nodiscard]] auto to_parameter_value(rsl::StaticString<capacity> const& value) {
    return rclcpp::ParameterValue(rsl::to_string(value));
}

template <typename T, size_t capacity>
[[nodiscard]] auto to_parameter_value(rsl::StaticVector<T, capacity> const& value) {
    return rclcpp::ParameterValue(rsl::to_vector(value));
}
    struct Params {
        bool use_local_topics = false;
        std::vector<std::string> joints = {};
        std::vector<std::string> extra_joints = {};
        std::vector<std::string> interfaces = {};
        std::vector<std::string> reverse_joints = {};
        std::vector<double> offsets = {};
        bool use_urdf_to_filter = true;
        struct MapInterfaceToJointState {
            std::string position = "position";
            std::string velocity = "velocity";
            std::string effort = "effort";
        } map_interface_to_joint_state;
        // for detecting if the parameter struct has been updated
        rclcpp::Time __stamp;
    };
    struct StackParams {
        bool use_local_topics = false;
        bool use_urdf_to_filter = true;
    };

  class ParamListener{
  public:
    // throws rclcpp::exceptions::InvalidParameterValueException on initialization if invalid parameter are loaded
    ParamListener(rclcpp::Node::SharedPtr node, std::string const& prefix = "")
    : ParamListener(node->get_node_parameters_interface(), node->get_logger(), prefix) {}

    ParamListener(rclcpp_lifecycle::LifecycleNode::SharedPtr node, std::string const& prefix = "")
    : ParamListener(node->get_node_parameters_interface(), node->get_logger(), prefix) {}

    ParamListener(const std::shared_ptr<rclcpp::node_interfaces::NodeParametersInterface>& parameters_interface,
                  std::string const& prefix = "")
    : ParamListener(parameters_interface, rclcpp::get_logger("joint_trajectory_command_broadcaster"), prefix) {
      RCLCPP_DEBUG(logger_, "ParameterListener: Not using node logger, recommend using other constructors to use a node logger");
    }

    ParamListener(const std::shared_ptr<rclcpp::node_interfaces::NodeParametersInterface>& parameters_interface,
                  rclcpp::Logger logger, std::string const& prefix = "") {
      logger_ = std::move(logger);
      prefix_ = prefix;
      if (!prefix_.empty() && prefix_.back() != '.') {
        prefix_ += ".";
      }

      parameters_interface_ = parameters_interface;
      declare_params();
      auto update_param_cb = [this](const std::vector<rclcpp::Parameter> &parameters){return this->update(parameters);};
      handle_ = parameters_interface_->add_on_set_parameters_callback(update_param_cb);
      clock_ = rclcpp::Clock();
    }

    Params get_params() const{
      std::lock_guard<std::mutex> lock(mutex_);
      return params_;
    }

    bool try_get_params(Params & params_in) const {
      if (mutex_.try_lock()) {
        if (const bool is_old = params_in.__stamp != params_.__stamp; is_old) {
          params_in = params_;
        }
        mutex_.unlock();
        return true;
      }
      return false;
    }

    bool is_old(Params const& other) const {
      std::lock_guard<std::mutex> lock(mutex_);
      return params_.__stamp != other.__stamp;
    }

    StackParams get_stack_params() {
      Params params = get_params();
      StackParams output;
      output.use_local_topics = params.use_local_topics;
      output.use_urdf_to_filter = params.use_urdf_to_filter;

      return output;
    }

    void refresh_dynamic_parameters() {
      auto updated_params = get_params();
      // TODO remove any destroyed dynamic parameters

      // declare any new dynamic parameters
      rclcpp::Parameter param;

    }

    rcl_interfaces::msg::SetParametersResult update(const std::vector<rclcpp::Parameter> &parameters) {
      auto updated_params = get_params();

      for (const auto &param: parameters) {
        if (param.get_name() == (prefix_ + "use_local_topics")) {
            updated_params.use_local_topics = param.as_bool();
            RCLCPP_DEBUG_STREAM(logger_, param.get_name() << ": " << param.get_type_name() << " = " << param.value_to_string());
        }
        if (param.get_name() == (prefix_ + "joints")) {
            updated_params.joints = param.as_string_array();
            RCLCPP_DEBUG_STREAM(logger_, param.get_name() << ": " << param.get_type_name() << " = " << param.value_to_string());
        }
        if (param.get_name() == (prefix_ + "extra_joints")) {
            updated_params.extra_joints = param.as_string_array();
            RCLCPP_DEBUG_STREAM(logger_, param.get_name() << ": " << param.get_type_name() << " = " << param.value_to_string());
        }
        if (param.get_name() == (prefix_ + "interfaces")) {
            updated_params.interfaces = param.as_string_array();
            RCLCPP_DEBUG_STREAM(logger_, param.get_name() << ": " << param.get_type_name() << " = " << param.value_to_string());
        }
        if (param.get_name() == (prefix_ + "reverse_joints")) {
            updated_params.reverse_joints = param.as_string_array();
            RCLCPP_DEBUG_STREAM(logger_, param.get_name() << ": " << param.get_type_name() << " = " << param.value_to_string());
        }
        if (param.get_name() == (prefix_ + "offsets")) {
            updated_params.offsets = param.as_double_array();
            RCLCPP_DEBUG_STREAM(logger_, param.get_name() << ": " << param.get_type_name() << " = " << param.value_to_string());
        }
        if (param.get_name() == (prefix_ + "map_interface_to_joint_state.position")) {
            updated_params.map_interface_to_joint_state.position = param.as_string();
            RCLCPP_DEBUG_STREAM(logger_, param.get_name() << ": " << param.get_type_name() << " = " << param.value_to_string());
        }
        if (param.get_name() == (prefix_ + "map_interface_to_joint_state.velocity")) {
            updated_params.map_interface_to_joint_state.velocity = param.as_string();
            RCLCPP_DEBUG_STREAM(logger_, param.get_name() << ": " << param.get_type_name() << " = " << param.value_to_string());
        }
        if (param.get_name() == (prefix_ + "map_interface_to_joint_state.effort")) {
            updated_params.map_interface_to_joint_state.effort = param.as_string();
            RCLCPP_DEBUG_STREAM(logger_, param.get_name() << ": " << param.get_type_name() << " = " << param.value_to_string());
        }
        if (param.get_name() == (prefix_ + "use_urdf_to_filter")) {
            updated_params.use_urdf_to_filter = param.as_bool();
            RCLCPP_DEBUG_STREAM(logger_, param.get_name() << ": " << param.get_type_name() << " = " << param.value_to_string());
        }
      }

      updated_params.__stamp = clock_.now();
      update_internal_params(updated_params);
      return rsl::to_parameter_result_msg({});
    }

    void declare_params(){
      auto updated_params = get_params();
      // declare all parameters and give default values to non-required ones
      if (!parameters_interface_->has_parameter(prefix_ + "use_local_topics")) {
          rcl_interfaces::msg::ParameterDescriptor descriptor;
          descriptor.description = "Defining if joint_states and dynamic_joint_states messages should be published into local namespace, e.g., /my_state_broadcaster/joint_states.";
          descriptor.read_only = false;
          auto parameter = to_parameter_value(updated_params.use_local_topics);
          parameters_interface_->declare_parameter(prefix_ + "use_local_topics", parameter, descriptor);
      }
      if (!parameters_interface_->has_parameter(prefix_ + "joints")) {
          rcl_interfaces::msg::ParameterDescriptor descriptor;
          descriptor.description = "Parameter to support broadcasting of only specific joints and interfaces. It has to be used in combination with the interfaces parameter. If either joints or interfaces is left empty, all available state interfaces will be published. Joint state broadcaster asks for access to all defined interfaces on all defined joints.";
          descriptor.read_only = false;
          auto parameter = to_parameter_value(updated_params.joints);
          parameters_interface_->declare_parameter(prefix_ + "joints", parameter, descriptor);
      }
      if (!parameters_interface_->has_parameter(prefix_ + "extra_joints")) {
          rcl_interfaces::msg::ParameterDescriptor descriptor;
          descriptor.description = "Names of extra joints to be added to joint_states and dynamic_joint_states with state set to 0.";
          descriptor.read_only = false;
          auto parameter = to_parameter_value(updated_params.extra_joints);
          parameters_interface_->declare_parameter(prefix_ + "extra_joints", parameter, descriptor);
      }
      if (!parameters_interface_->has_parameter(prefix_ + "interfaces")) {
          rcl_interfaces::msg::ParameterDescriptor descriptor;
          descriptor.description = "Parameter to support broadcasting of only specific joints and interfaces. It has to be used in combination with the joints parameter. If either joints or interfaces is left empty, all available state interfaces will be published.";
          descriptor.read_only = false;
          auto parameter = to_parameter_value(updated_params.interfaces);
          parameters_interface_->declare_parameter(prefix_ + "interfaces", parameter, descriptor);
      }
      if (!parameters_interface_->has_parameter(prefix_ + "reverse_joints")) {
          rcl_interfaces::msg::ParameterDescriptor descriptor;
          descriptor.description = "Names of joints to be reversed.";
          descriptor.read_only = false;
          auto parameter = to_parameter_value(updated_params.reverse_joints);
          parameters_interface_->declare_parameter(prefix_ + "reverse_joints", parameter, descriptor);
      }
      if (!parameters_interface_->has_parameter(prefix_ + "offsets")) {
          rcl_interfaces::msg::ParameterDescriptor descriptor;
          descriptor.description = "Offsets of joints to be added to the joint positions.";
          descriptor.read_only = false;
          auto parameter = to_parameter_value(updated_params.offsets);
          parameters_interface_->declare_parameter(prefix_ + "offsets", parameter, descriptor);
      }
      if (!parameters_interface_->has_parameter(prefix_ + "map_interface_to_joint_state.position")) {
          rcl_interfaces::msg::ParameterDescriptor descriptor;
          descriptor.description = "";
          descriptor.read_only = false;
          auto parameter = to_parameter_value(updated_params.map_interface_to_joint_state.position);
          parameters_interface_->declare_parameter(prefix_ + "map_interface_to_joint_state.position", parameter, descriptor);
      }
      if (!parameters_interface_->has_parameter(prefix_ + "map_interface_to_joint_state.velocity")) {
          rcl_interfaces::msg::ParameterDescriptor descriptor;
          descriptor.description = "";
          descriptor.read_only = false;
          auto parameter = to_parameter_value(updated_params.map_interface_to_joint_state.velocity);
          parameters_interface_->declare_parameter(prefix_ + "map_interface_to_joint_state.velocity", parameter, descriptor);
      }
      if (!parameters_interface_->has_parameter(prefix_ + "map_interface_to_joint_state.effort")) {
          rcl_interfaces::msg::ParameterDescriptor descriptor;
          descriptor.description = "";
          descriptor.read_only = false;
          auto parameter = to_parameter_value(updated_params.map_interface_to_joint_state.effort);
          parameters_interface_->declare_parameter(prefix_ + "map_interface_to_joint_state.effort", parameter, descriptor);
      }
      if (!parameters_interface_->has_parameter(prefix_ + "use_urdf_to_filter")) {
          rcl_interfaces::msg::ParameterDescriptor descriptor;
          descriptor.description = "Uses the robot_description to filter the joint_states topic. If true, the broadcaster will publish the data of the joints present in the URDF alone. If false, the broadcaster will publish the data of any interface that has type position, velocity, or effort.";
          descriptor.read_only = false;
          auto parameter = to_parameter_value(updated_params.use_urdf_to_filter);
          parameters_interface_->declare_parameter(prefix_ + "use_urdf_to_filter", parameter, descriptor);
      }
      // get parameters and fill struct fields
      rclcpp::Parameter param;
      param = parameters_interface_->get_parameter(prefix_ + "use_local_topics");
      RCLCPP_DEBUG_STREAM(logger_, param.get_name() << ": " << param.get_type_name() << " = " << param.value_to_string());
      updated_params.use_local_topics = param.as_bool();
      param = parameters_interface_->get_parameter(prefix_ + "joints");
      RCLCPP_DEBUG_STREAM(logger_, param.get_name() << ": " << param.get_type_name() << " = " << param.value_to_string());
      updated_params.joints = param.as_string_array();
      param = parameters_interface_->get_parameter(prefix_ + "extra_joints");
      RCLCPP_DEBUG_STREAM(logger_, param.get_name() << ": " << param.get_type_name() << " = " << param.value_to_string());
      updated_params.extra_joints = param.as_string_array();
      param = parameters_interface_->get_parameter(prefix_ + "interfaces");
      RCLCPP_DEBUG_STREAM(logger_, param.get_name() << ": " << param.get_type_name() << " = " << param.value_to_string());
      updated_params.interfaces = param.as_string_array();
      param = parameters_interface_->get_parameter(prefix_ + "reverse_joints");
      RCLCPP_DEBUG_STREAM(logger_, param.get_name() << ": " << param.get_type_name() << " = " << param.value_to_string());
      updated_params.reverse_joints = param.as_string_array();
      param = parameters_interface_->get_parameter(prefix_ + "offsets");
      RCLCPP_DEBUG_STREAM(logger_, param.get_name() << ": " << param.get_type_name() << " = " << param.value_to_string());
      updated_params.offsets = param.as_double_array();
      param = parameters_interface_->get_parameter(prefix_ + "map_interface_to_joint_state.position");
      RCLCPP_DEBUG_STREAM(logger_, param.get_name() << ": " << param.get_type_name() << " = " << param.value_to_string());
      updated_params.map_interface_to_joint_state.position = param.as_string();
      param = parameters_interface_->get_parameter(prefix_ + "map_interface_to_joint_state.velocity");
      RCLCPP_DEBUG_STREAM(logger_, param.get_name() << ": " << param.get_type_name() << " = " << param.value_to_string());
      updated_params.map_interface_to_joint_state.velocity = param.as_string();
      param = parameters_interface_->get_parameter(prefix_ + "map_interface_to_joint_state.effort");
      RCLCPP_DEBUG_STREAM(logger_, param.get_name() << ": " << param.get_type_name() << " = " << param.value_to_string());
      updated_params.map_interface_to_joint_state.effort = param.as_string();
      param = parameters_interface_->get_parameter(prefix_ + "use_urdf_to_filter");
      RCLCPP_DEBUG_STREAM(logger_, param.get_name() << ": " << param.get_type_name() << " = " << param.value_to_string());
      updated_params.use_urdf_to_filter = param.as_bool();


      updated_params.__stamp = clock_.now();
      update_internal_params(updated_params);
    }

    private:
      void update_internal_params(Params updated_params) {
        std::lock_guard<std::mutex> lock(mutex_);
        params_ = std::move(updated_params);
      }

      std::string prefix_;
      Params params_;
      rclcpp::Clock clock_;
      std::shared_ptr<rclcpp::node_interfaces::OnSetParametersCallbackHandle> handle_;
      std::shared_ptr<rclcpp::node_interfaces::NodeParametersInterface> parameters_interface_;

      // rclcpp::Logger cannot be default-constructed
      // so we must provide a initialization here even though
      // every one of our constructors initializes logger_
      rclcpp::Logger logger_ = rclcpp::get_logger("joint_trajectory_command_broadcaster");
      std::mutex mutable mutex_;
  };

} // namespace joint_trajectory_command_broadcaster
