import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution, LaunchConfiguration
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessStart

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare



def generate_launch_description():


    # Include the robot_state_publisher launch file, provided by our own package. Force sim time to be enabled
    # !!! MAKE SURE YOU SET THE PACKAGE NAME CORRECTLY !!!

    package_name='firefighting_robot' #<--- CHANGE ME

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'false', 'use_ros2_control': 'true'}.items()
    )


    # Get URDF via xacro
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("firefighting_robot"), "urdf", "robot.urdf.xacro"]
            ),
            
        ]
    )

    

    robot_description = {"robot_description": robot_description_content}

    robot_controllers = PathJoinSubstitution(
        [
            FindPackageShare("firefighting_robot"),
            "config",
            "my_controllers.yaml",
        ]
    )

    controller_manager = Node(
       package="controller_manager",
        executable="ros2_control_node",
       parameters=[{"robot_description": robot_description},
                   robot_controllers]
    )

    diff_drive_spawner = Node(
       package="controller_manager",
        executable="spawner.py",
       arguments=["diff_cont", "--controller-manager", "/controller_manager"],
    )


    delayed_diff_drive_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[diff_drive_spawner],
        )
    )

    delayed_controller_manager = TimerAction(period=3.0, actions=[controller_manager])

    joint_broad_spawner = Node(
       package="controller_manager",
        executable="spawner.py",
       arguments=["joint_broad"],
    )


    delayed_joint_broad_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[joint_broad_spawner],
        )
    )

    # Code for delaying a node (I haven't tested how effective it is)
    # 
    # First add the below lines to imports
    
    #
    # Then add the following below the current diff_drive_spawner
    # 
    #
    # Replace the diff_drive_spawner in the final return with delayed_diff_drive_spawner


    # Launch them all!
    return LaunchDescription([
        rsp,
        delayed_controller_manager,
        delayed_diff_drive_spawner,
        delayed_joint_broad_spawner,
    ])