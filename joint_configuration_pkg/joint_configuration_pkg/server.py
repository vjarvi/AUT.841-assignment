import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from custom_msgs.srv import SetJointConfiguration
import math


class JointConfigurationServer(Node):
    """Receive joint configurations and publish validated joint states."""

    def __init__(self):
        super().__init__('joint_configuration_server')

        self.joint_names = ["joint_1", "joint_2", "joint_3",
                            "joint_4", "joint_5", "joint_6"]

        self.joint_limits = [(-math.pi/2, math.pi/2), (-math.pi/2, math.pi/2), (-math.pi, math.pi),
                            (-0.4, 0.3), (0.02, 0.12), (-0.12, -0.02)]

        # Home pose: centered arm, quill at zero, gripper fully open.
        self.initial_positions = [0.0, 0.0, 0.0, 0.0, 0.02, -0.02]

        self.publisher = self.create_publisher(JointState, '/joint_states', 10)
        self.srv = self.create_service(
            SetJointConfiguration,
            'set_joint_configuration',
            self.set_configuration_callback,
        )
        self.get_logger().info('Joint configuration server ready.')

    def set_configuration_callback(self, request, response):
        """Validate the entire request before publishing any joint values."""
        positions = list(request.positions)
        self.get_logger().info(f'Received joint positions: {positions}')

        # Validate each requested joint position against limist
        response.success = False
        joint_count = len(self.joint_limits)

        if len(positions) != joint_count: 
            response.message = f"Received incorrect amount of joint values, requires {joint_count}"
        else: 
            for i in range(joint_count):
                minimum, maximum = self.joint_limits[i][0], self.joint_limits[i][1]
                if minimum > positions[i] or maximum < positions[i]:
                    response.message = f"Received illegal configuration for joint {i + 1}, must be in range ({minimum}, {maximum})"
                    return response

        response.success = True
        response.message = "Joint configuration validated"
        self.publish_configuration(positions)
        
        return response

    def publish_configuration(self, positions):
        """Publish joint configuration to '/joint_states'."""
        joint_state = JointState()
        joint_state.header.stamp = self.get_clock().now().to_msg()
        joint_state.name = list(self.joint_names)
        joint_state.position = list(positions)
        self.publisher.publish(joint_state)


def main(args=None):
    rclpy.init(args=args)
    node = JointConfigurationServer()
    try:
         # Publish initial position immediately to update GUI
        node.publish_configuration(node.initial_positions)
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
