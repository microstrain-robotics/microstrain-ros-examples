cmake_minimum_required(VERSION 3.8)
project(microstrain_ros_examples)

# find dependencies
find_package(ament_cmake REQUIRED)

## Mark other files for installation (e.g. launch and bag files, etc.)
install(DIRECTORY config launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
