from pulp import LpMaximize, LpProblem, LpVariable, lpSum

bandwidth_budget_kbps = 15000

topics = {
    "/cmd_vel": (0.052, 5, 20),
    "/odom": (0.72, 10, 30),
    "/camera/camera_info": (0.38, 10, 30),
    "/camera/image_raw/compressed": (420.0, 5, 30),
    "/camera/image_raw": (6220.0, 2, 30),
    "/imu": (0.32, 50, 200),
    "/joint_state": (0.12, 2, 10),
    "/scan": (2.94, 2, 10),
    "/tf": (0.17, 2, 40),
}

# GUIDE FOR PRIORITY
# 1.0 = neutral

# >1.0 = important

# <1.0 = less important

priority_weights = {
    "/cmd_vel": 1.0,
    "/odom": 1.0,
    "/camera/camera_info": 0.5,
    "/camera/image_raw/compressed": 0.4,
    "/camera/image_raw": 0.2,
    "/imu": 1.5,
    "/joint_state": 0.8,
    "/scan": 1.2,
    "/tf": 1.0,
}

model = LpProblem("Weighted_Frequency_Allocation", LpMaximize)

#frequency variables with bounds
f = {
    t: LpVariable(f"freq_{t}", lowBound=min_f, upBound=max_f, cat="Continuous")
    for t, (size, min_f, max_f) in topics.items()
}

#maximize weighted total frequency
model += lpSum(priority_weights[t] * f[t] for t in topics), "Weighted_Total_Frequency"

#total bandwidth usage must be ≤ bandwidth budget
model += lpSum(f[t] * topics[t][0] for t in topics) <= bandwidth_budget_kbps, "Bandwidth_Constraint"

model.solve()

print("Status:", model.status)
total_bw = 0
for t in topics:
    freq = f[t].value()
    msg_size = topics[t][0]
    bw = freq * msg_size
    total_bw += bw
    print(f"{t}: {freq:.2f} Hz (priority {priority_weights[t]}) -> {bw:.2f} KB/s")

print(f"Total bandwidth used: {total_bw:.2f} KB/s")
