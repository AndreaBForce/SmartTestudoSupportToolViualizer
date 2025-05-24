begin
    // Global default
    SetFrequency /odom 10
    SetFrequency /cmd_vel 7
    SetFrequency /scan 3
    SetFrequency /camera/camera_info 3
    SetFrequency /camera/image_raw 3
    SetFrequency /camera/image_raw/compressed 3
    SetFrequency /imu 10
    SetFrequency /joint_states 3
    SetFrequency /tf 10

    //security zone 2 - warehouse corridor
    If(
        CheckValue /odom pose_y < 5.4
        AND CheckValue /odom pose_y > 1
        AND CheckValue /odom pose_x > -13
        AND CheckValue /odom pose_x < 6
    ) Then 
        SetFrequency /odom 4
        SetFrequency /cmd_vel 4
        SetFrequency /scan 4
    //security zone 3 - scaffolding corridor 
    If(
        CheckValue /odom pose_y < 25.5
        AND CheckValue /odom pose_y > 6
        AND CheckValue /odom pose_x > -13
        AND CheckValue /odom pose_x < 6
    ) Then 
        SetFrequency /odom 10
        SetFrequency /cmd_vel 10 
        SetFrequency /scan 10
        SetFrequency /camera/image_raw/compressed 10
end