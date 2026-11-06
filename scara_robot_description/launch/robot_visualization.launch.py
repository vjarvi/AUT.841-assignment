import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    pkg_share = get_package_share_directory("scara_robot_description")

    robot_xacro_filepath = os.path.join(pkg_share, "urdf", "robot.urdf.xacro")
    robot_description = xacro.process_file(
        robot_xacro_filepath,
        mappings={
            ### Configure robot parameters
        },
    ).toprettyxml(indent="  ")

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description": robot_description}],
    )

    #    joint_state_publisher_gui = Node(
    #        package="joint_state_publisher_gui",
    #        executable="joint_state_publisher_gui",
    #        name="joint_state_publisher_gui",
    #    )

    rviz_file = os.path.join(pkg_share, "rviz", "visualize_robot.rviz")
    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["--display-config", rviz_file] if os.path.exists(rviz_file) else [],
    )

    return LaunchDescription(
        [
            robot_state_publisher,
            # joint_state_publisher_gui,
            rviz,
        ]
    )
