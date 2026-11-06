from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    joint_configuration_server = Node(
        package="joint_configuration_pkg",
        executable="joint_configuration_server",
        name="joint_configuration_server",
        output="screen",
    )
    ee_pose_server = Node(
        package="end_effector_pose_pkg",
        executable="ee_pose_server",
        name="end_effector_pose_server",
        output="screen",
    )
    return LaunchDescription([joint_configuration_server, ee_pose_server])
