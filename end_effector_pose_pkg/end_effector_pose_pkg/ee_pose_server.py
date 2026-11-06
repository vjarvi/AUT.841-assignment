import rclpy
from rclpy.node import Node
from rclpy.time import Time
from tf2_ros import Buffer, TransformListener, TransformException
from custom_msgs.srv import GetEndEffectorPose


class EndEffectorPoseServer(Node):
    """Return end-effector pose in the base frame via TF2"""

    def __init__(self):
        super().__init__("end_effector_pose_server")

        self.declare_parameter("base_frame", "base_link")
        self.declare_parameter("ee_frame", "tcp")

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.srv = self.create_service(
            GetEndEffectorPose,
            "get_end_effector_pose",
            self.get_pose_callback,
        )
        self.get_logger().info("End-effector Pose Server ready")

    def get_pose_callback(self, request, response):
        """Look up the latest base -> end-effector tf and return it"""
        base = self.get_parameter("base_frame").value
        ee = self.get_parameter("ee_frame").value

        try:
            # Time() = latest available tf
            tf = self.tf_buffer.lookup_transform(base, ee, Time())
        except TransformException as err:
            response.success = False
            response.message = f"Could not look up '{ee}' in '{base}': {err}."
            return response

        t = tf.transform.translation
        r = tf.transform.rotation
        response.pose.header = tf.header
        response.pose.pose.position.x = t.x
        response.pose.pose.position.y = t.y
        response.pose.pose.position.z = t.z
        response.pose.pose.orientation.x = r.x
        response.pose.pose.orientation.y = r.y
        response.pose.pose.orientation.z = r.z
        response.pose.pose.orientation.w = r.w
        response.success = True
        response.message = f"Pose of '{ee}' in '{base}'"
        return response


def main(args=None):
    rclpy.init(args=args)
    node = EndEffectorPoseServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
