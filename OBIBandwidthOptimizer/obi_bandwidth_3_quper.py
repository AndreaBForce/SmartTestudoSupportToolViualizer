from pulp import LpMaximize, LpProblem, LpVariable, lpSum

bandwidth_budget_kbps = 275000  # Total bandwidth budget

#utility frequency breakpoints
topics = {
    "/cmd_vel": (0.052, [5, 10, 15, 18, 20]),
    "/odom": (0.72, [10, 15, 20, 25, 30]),
    "/camera/camera_info": (0.38, [10, 15, 20, 25, 30]),
    "/camera/image_raw/compressed": (420.0, [5, 10, 15, 20, 30]),
    "/camera/image_raw": (6220.0, [2, 5, 10, 15, 20]),
    "/imu": (0.32, [50, 75, 100, 150, 200]),
    "/joint_state": (0.12, [2, 4, 6, 8, 10]),
    "/scan": (2.94, [2, 4, 6, 8, 10]),
    "/tf": (0.17, [2, 10, 20, 30, 40]),
}

tiers = {
    "Unacceptable": 0,
    "Marginal": 1,
    "Acceptable": 2,
    "Desirable": 3,
    "Competitive": 4,
    "Excessive": 5,
}

desired_tiers = {
    "/cmd_vel": "Acceptable",
    "/odom": "Desirable",
    "/camera/camera_info": "Acceptable",
    "/camera/image_raw/compressed": "Marginal",
    "/camera/image_raw": "Acceptable",
    "/imu": "Competitive",
    "/joint_state": "Acceptable",
    "/scan": "Desirable",
    "/tf": "Acceptable",
}

model = LpProblem("Utility_Tier_Bandwidth_Allocation", LpMaximize)

f = {}
for t, (size, breakpoints) in topics.items():
    tier_index = tiers[desired_tiers[t]]
    
    if tier_index == 0:
        low = 0
        high = breakpoints[0]
    elif tier_index == 5:
        low = breakpoints[-1]
        high = breakpoints[-1] + 10 
    else:
        low = breakpoints[tier_index - 1]
        high = breakpoints[tier_index]

    f[t] = LpVariable(f"freq_{t}", lowBound=low, upBound=high, cat="Continuous")

model += lpSum(f[t] for t in topics), "Total_Frequency"

model += lpSum(f[t] * topics[t][0] for t in topics) <= bandwidth_budget_kbps, "Bandwidth_Constraint"

model.solve()

print("Status:", model.status)
total_bw = 0
for t in topics:
    freq = f[t].value()
    size = topics[t][0]
    bw = freq * size
    total_bw += bw
    print(f"{t}: {freq:.2f} Hz (desired tier: {desired_tiers[t]}) -> {bw:.2f} KB/s")

print(f"Total bandwidth used: {total_bw:.2f} KB/s")
