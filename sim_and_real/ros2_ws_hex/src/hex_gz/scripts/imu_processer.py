#!/usr/bin/env python3
 
"""
Description:
    This ROS 2 node subscribes to IMU sensor data and republishes it.
    It demonstrates ROS concepts such as node creation, subscribing to sensor_msgs/Imu
    and republishing processed data.
-------
Publishing Topics:
    /processed_imu - sensor_msgs/Imu (Processed IMU data)
-------
Subscription Topics:
    /imu/data - sensor_msgs/Imu (Raw IMU data from sensor)
-------
Date: May 14, 2025
"""

import rclpy  # Import the ROS 2 client library for Python
from rclpy.node import Node  # Import the Node class for creating ROS 2 nodes

from sensor_msgs.msg import Imu  # Import the IMU message type
from geometry_msgs.msg import Vector3  # For vector data types
import numpy as np  # For numerical operations
import transforms3d as tf3d  # Optional: for handling rotations if needed

class ImuProcessor(Node):
    """Create an IMU data processor node."""
 
    def __init__(self):
        """Initialize the node."""
 
        # Initialize the node with a name
        super().__init__('imu_processor')
 
        # Create a subscriber for IMU data
        self.imu_subscriber = self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            10)  # QoS profile with queue size 10
        
        # Create a publisher for processed IMU data
        self.imu_publisher = self.create_publisher(
            Imu,
            '/processed_imu',
            10)  # QoS profile with queue size 10
            
        # Initialize variables for tracking orientation, etc.
        self.orientation = None
        self.angular_velocity = None
        self.linear_acceleration = None
        
        # Log node startup
        self.get_logger().info('IMU Processor node has started')
 
    def imu_callback(self, msg):
        """Process incoming IMU data.
        
        Args:
            msg (sensor_msgs/Imu): The IMU message received from the sensor
        """
        # Store the latest IMU readings
        self.orientation = msg.orientation
        self.angular_velocity = msg.angular_velocity
        self.linear_acceleration = msg.linear_acceleration
        
        # Log a message indicating receipt of data
        self.get_logger().debug(f'Received IMU data - Linear acceleration: x={msg.linear_acceleration.x:.2f}, '
                              f'y={msg.linear_acceleration.y:.2f}, z={msg.linear_acceleration.z:.2f}')
        
        # Process the IMU data (example: applying a simple filter or transformation)
        processed_msg = self.process_imu_data(msg)
        
        # Publish the processed data
        self.imu_publisher.publish(processed_msg)
    
    def process_imu_data(self, msg):
        """Process the IMU data.
        
        This is where you would implement any filtering, calibration,
        or transformations needed for your specific application.
        
        Args:
            msg (sensor_msgs/Imu): The raw IMU message
            
        Returns:
            sensor_msgs/Imu: The processed IMU message
        """
        # Create a new IMU message for the processed data
        processed_msg = Imu()
        
        # Copy the header from the input message
        processed_msg.header = msg.header
        
        # Example processing: apply a simple low-pass filter to acceleration
        # In a real application, you might implement a Kalman filter or other more sophisticated processing
        
        # For this example, we'll just copy the data
        # In a real application, you would implement your specific processing here
        processed_msg.orientation = msg.orientation
        processed_msg.orientation_covariance = msg.orientation_covariance
        processed_msg.angular_velocity = msg.angular_velocity
        processed_msg.angular_velocity_covariance = msg.angular_velocity_covariance
        processed_msg.linear_acceleration = msg.linear_acceleration
        processed_msg.linear_acceleration_covariance = msg.linear_acceleration_covariance
        
        return processed_msg

def main(args=None):
    """Main function to start the ROS 2 node.
 
    Args:
        args (List, optional): Command-line arguments. Defaults to None.
    """

    # Initialize ROS 2 communication
    rclpy.init(args=args)
 
    # Create an instance of the ImuProcessor node
    imu_processor = ImuProcessor()
 
    # Keep the node running and processing events
    rclpy.spin(imu_processor)
 
    # Destroy the node explicitly
    imu_processor.destroy_node()
 
    # Shutdown ROS 2 communication
    rclpy.shutdown()
 
 
if __name__ == '__main__':
    # Execute the main function if the script is run directly
    main()