import sys
import time

import rclpy
from rclpy.node import Node
from rclpy.utilities import remove_ros_args
from custom_msgs.srv import SetJointConfiguration, GetEndEffectorPose

N_ARGS = 5  # j6 is a mimic of j5
SETTLE_TIME = 0.5
USAGE = (
    "Usage: ros2 run end_effector_pose_pkg scara_client "
    "<j1> <j2> <j3> <j4> <j5>\n"
    "   j1-j3: revolute [rad], j4: quill [m], j5: finger [m] (j6 is -j5)"
)


class ScaraClient(Node):
    """Set a joint configuration and request the end effector pose"""

    def __init__(self):
        super().__init__("scara_client")
        self.set_cli = self.create_client(
            SetJointConfiguration, "set_joint_configuration"
        )
        self.pose_cli = self.create_client(GetEndEffectorPose, "get_end_effector_pose")

    def servers_available(self, timeout=5.0):
        """Wait for both services, report if missing"""
        for cli in (self.set_cli, self.pose_cli):
            if not cli.wait_for_service(timeout_sec=timeout):
                self.get_logger().error(f"Service {cli.srv_name} not available")
                return False
        return True

    def call(self, client, request):
        """Call a service and wait for the result"""
        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        return future.result()


def parse_joints(argv):
    """Convert command line strings to a list of joint values"""
    if len(argv) != N_ARGS:
        raise ValueError(f"expected {N_ARGS} joint values, got {len(argv)}")
    try:
        values = [float(a) for a in argv]
    except ValueError:
        raise ValueError("all joint values must be numbers")
    return values + [-values[4]]


def main(args=None):
    rclpy.init(args=args)
    node = ScaraClient()
    log = node.get_logger()
    exit_code = 1

    try:
        try:
            positions = parse_joints(remove_ros_args(sys.argv)[1:])
        except ValueError as err:
            log.error(f"Invalid arguments: {err}")
            return exit_code

        if not node.servers_available():
            return exit_code

        # 1. set joint configuration
        req = SetJointConfiguration.Request()
        req.positions = positions
        res = node.call(node.set_cli, req)
        if res is None:
            log.error("Joint config service call failed")
            return exit_code
        if not res.success:
            log.error(f"Joint config rejected: {res.message}")
            return exit_code
        log.info(f"Joint configuration set: {res.message}")

        # 2. let tf catch up, then ask for the ee pose
        time.sleep(SETTLE_TIME)
        res = node.call(node.pose_cli, GetEndEffectorPose.Request())
        if res is None:
            log.error("End effector pose service call failed")
            return exit_code
        if not res.success:
            log.error(f"Pose request failed: {res.message}")
            return exit_code

        p = res.pose.pose.position
        q = res.pose.pose.orientation
        log.info(
            f"End-effector pose in '{res.pose.header.frame_id}':\n"
            f"  Position: x={p.x:.4f}, y={p.y:.4f}, z={p.z:.4f}\n"
            f"  Orientation: x={q.x:.4f}, y={q.y:.4f}, z={q.z:.4f}, w={q.w:.4f}"
        )
        exit_code = 0
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    return exit_code
