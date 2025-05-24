import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt

#This script is used to plot bandwidth data and save it in a csv.
#python3 rosbag_plot_bandwidth.py --csv_dir /home/chalmers/ADIRFRuleElicitator/RosBagVisualizer/csv_output_path/testudo_csv --resolution 1000
MESSAGE_SIZES_BYTES = {
    "/cmd_vel_receive": 52,
    "/odom_receive": int(0.72 * 1024),
    "/camera/camera_info_receive": int(0.38 * 1024),
    "/camera/image_raw/compressed_receive": int(0.42 * 1024 * 1024),
    "/camera/image_raw_receive": int(6.22 * 1024 * 1024),
    "/imu_receive": int(0.32 * 1024),
    "/joint_states_receive": int(0.12 * 1024),
    "/scan_receive": int(2.94 * 1024),
    "/tf_receive": int(0.17 * 1024),
}

def guess_topic_from_filename(filename):
    base = os.path.basename(filename).replace('.csv', '').lower()
    if base.startswith("tb3_"):
        base = base[4:]
    for topic in MESSAGE_SIZES_BYTES:
        normalized_topic = topic.lower().strip('/').replace('/', '_')
        if normalized_topic == base:
            return topic
    alt_format = '/' + base.replace('_', '/')
    if alt_format in MESSAGE_SIZES_BYTES:
        return alt_format
    for topic in MESSAGE_SIZES_BYTES:
        if base.replace('_', '') in topic.replace('/', ''):
            return topic
    return None

def plot_bandwidth_only(csv_file, output_dir, time_bucket_ms):
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"  Failed to read {csv_file}: {e}")
        return

    timestamp_col = next((col for col in df.columns if 'timestamp' in col.lower()), None)
    if not timestamp_col or df.empty:
        print(f"  Skipping {csv_file} (missing timestamp or empty)")
        return

    try:
        df[timestamp_col] = pd.to_datetime(df[timestamp_col], unit='ns')
    except Exception as e:
        print(f"  Failed to parse timestamps in {csv_file}: {e}")
        return

    df = df.set_index(timestamp_col)
    bucket_str = f'{int(time_bucket_ms)}ms'
    freq_df = df.resample(bucket_str).size().rename("frequency")

    topic = guess_topic_from_filename(csv_file)
    if not topic or topic not in MESSAGE_SIZES_BYTES:
        print(f"  Unknown topic for {csv_file}, bandwidth not computed.")
        return

    message_size_bytes = MESSAGE_SIZES_BYTES[topic]
    bandwidth_kbps = (freq_df * message_size_bytes * 8) / 1000  # kbps

    plt.figure(figsize=(12, 5))
    plt.plot(bandwidth_kbps.index, bandwidth_kbps, label='Bandwidth (kbps)', color='orange')
    plt.title(f'Bandwidth: {os.path.basename(csv_file)}')
    plt.xlabel('Time')
    plt.ylabel(f'Bandwidth (kbps) per {bucket_str}')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    output_plot_file = os.path.join(output_dir, os.path.basename(csv_file).replace('.csv', '_bandwidth_only.png'))
    plt.savefig(output_plot_file)
    plt.close()

    bandwidth_kbps.to_csv(os.path.join(output_dir, os.path.basename(csv_file).replace('.csv', '_bandwidth_only.csv')))

def process_all_csvs(csv_dir, resolution_ms):
    output_dir = os.path.join(csv_dir, 'bandwidth_only')
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(csv_dir):
        if filename.endswith('.csv'):
            csv_file = os.path.join(csv_dir, filename)
            print(f"Processing: {filename}")
            plot_bandwidth_only(csv_file, output_dir, resolution_ms)

    print("\nAll plots and bandwidth data saved to:", output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot estimated bandwidth from CSVs with known message sizes.")
    parser.add_argument('--csv_dir', type=str, required=True, help='Path to folder containing CSV files.')
    parser.add_argument('--resolution', type=int, default=1000, help='Time bucket in milliseconds (default: 1000ms = 1s).')

    args = parser.parse_args()
    process_all_csvs(args.csv_dir, args.resolution)
