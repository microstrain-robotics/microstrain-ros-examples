import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import LaunchConfigurationEquals, LaunchConfigurationNotEquals
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node, PushRosNamespace
from launch_ros.actions.node import ParameterFile

from ament_index_python.packages import get_package_share_directory

_PACKAGE_NAME = 'microstrain_ros_examples'

_CV7_INS_UBLOX_F9P_PARAMS_FILE = os.path.join(get_package_share_directory(_PACKAGE_NAME), 'config', 'cv7_ins_ublox_f9p.yml')

def generate_launch_description():

  launch_description = []

  arguments = [
    # MicroStrain parameters
    DeclareLaunchArgument('microstrain_port',     default_value='/dev/microstrain_main', description='The port that the CV7-INS is connected to'),
    DeclareLaunchArgument('microstrain_baudrate', default_value='115200',                description='The baudrate to open the port at'),

    # Ublox parameters
    DeclareLaunchArgument('ublox_f9p_port', default_value='/dev/ttyACM1', description='The port that the ublox F9P is connected to'),

    # NTRIP Client parameters
    DeclareLaunchArgument('ntrip',            default_value='false',        description='Whether or not to start an NTRIP client for differential corrections'),
    DeclareLaunchArgument('ntrip_host',       default_value='20.185.11.35', description='The host name or IP of the NTRIP caster you want to connect to'),
    DeclareLaunchArgument('ntrip_port',       default_value='2101',         description='The port of the NTRIP caster you want to connect to'),
    DeclareLaunchArgument('ntrip_mountpoint', default_value='VRS_RTCM3',    description='The mountpoint on the NTRIP caster you want to connec to'),
    DeclareLaunchArgument('ntrip_username',   default_value='user',         description='Username to use to authenticate with the NTRIP caster'),
    DeclareLaunchArgument('ntrip_password',   default_value='pass',         description='Password to use to authenticate with the NTRIP caster'),
    DeclareLaunchArgument('ntrip_ssl',        default_value='false',        description='Whether or not to connect using SSL to the NTRIP caster'),

    # Allow the includer to specify whatever parameter file they want
    DeclareLaunchArgument('params_file', default_value=_CV7_INS_UBLOX_F9P_PARAMS_FILE, description='Path to file that contains user defined parameters'),
  ]
  launch_description.extend(arguments)

  # MicroStrain node to run CV7-INS
  microstrain_node = Node(
    package    = "microstrain_inertial_driver",
    executable = "microstrain_inertial_driver_node",
    name       = "microstrain_inertial_driver",
    namespace  = '',
    output     = 'screen',
    parameters = [
      ParameterFile(LaunchConfiguration('params_file'), allow_substs=True),
    ]
  )
  launch_description.append(microstrain_node)

  # Ublox F9P node
  ublox_f9p_node = Node(
    package = 'ublox_gps',
    executable = 'ublox_gps_node',
    name = 'ublox_f9p',
    namespace = '',
    output = 'screen',
    remappings = [
      # Remap the fix and fix velocity topics so they will get sent to the CV7-INS
      ('fix', 'ext/llh_position'),
      ('fix_velocity', 'ext/velocity_enu'),

      # Some newer versions of the driver need to have the name of the node in the topic name
      ('ublox_f9p/fix', 'ext/llh_position'),
      ('ublox_f9p/fix_velocity', 'ext/velocity_enu'),

      # Looks like the RTCM topics are forced into the global namespace. Fix that here
      ('/rtcm', 'rtcm'),
    ],
    parameters = [
      ParameterFile(LaunchConfiguration('params_file'), allow_substs=True)
    ]
  )
  launch_description.append(ublox_f9p_node)

  # NTRIP Client node
  ntrip_node = Node(
    package    = 'ntrip_client',
    executable = 'ntrip_ros.py',
    name       = 'ntrip_client',
    namespace  = '',
    output     = 'screen',
    condition=LaunchConfigurationEquals('ntrip', 'true'),
    remappings = [
      # If using an F9P, we need to receive fix messages instead of nmea, so subscribe to the same topic as the CV7-INS
      ('fix', 'ext/llh_position'),
    ],
    parameters = [
      ParameterFile(LaunchConfiguration('params_file'), allow_substs=True),
    ]
  )
  launch_description.append(ntrip_node)

  return LaunchDescription(launch_description)
  

 
 
