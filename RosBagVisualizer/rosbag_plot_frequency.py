import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt

def plot_frequency(csv_file, output_dir, time_bucket_ms):
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"  Failed to read {csv_file}: {e}")
        return
    
    timestamp_col = next((col for col in df.columns if 'timestamp' in col.lower()), None)

    if not timestamp_col:
        print(f"  No timestamp column found in {csv_file}. Skipping.")
        return

    if df.empty:
        print(f"  Skipping {csv_file} (empty file)")
        return

    try:
        df[timestamp_col] = pd.to_datetime(df[timestamp_col], unit='ns')
    except Exception as e:
        print(f"  Failed to parse timestamps in {csv_file}: {e}")
        return

    df = df.set_index(timestamp_col)
    bucket_str = f'{int(time_bucket_ms)}ms'
    freq_df = df.resample(bucket_str).size().rename("frequency")

    plt.figure(figsize=(10, 4))
    plt.plot(freq_df.index, freq_df, label='Frequency')
    plt.title(f'Frequency Over Time ({os.path.basename(csv_file)})')
    plt.xlabel('Time')
    plt.ylabel(f'Messages per {bucket_str}')
    plt.grid(True)
    plt.tight_layout()

    output_file = os.path.join(output_dir, os.path.basename(csv_file).replace('.csv', '_freq.png'))
    plt.savefig(output_file)
    plt.close()

def process_all_csvs(csv_dir, resolution_ms):
    output_dir = os.path.join(csv_dir, 'frequency_plots')
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(csv_dir):
        if filename.endswith('.csv'):
            csv_file = os.path.join(csv_dir, filename)
            print(f"Processing: {filename}")
            plot_frequency(csv_file, output_dir, resolution_ms)

    print("\nAll plots complete. Saved to:", output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot message frequency from ROS2 bag CSVs.")
    parser.add_argument('--csv_dir', type=str, required=True, help='Path to folder containing CSV files.')
    parser.add_argument('--resolution', type=int, default=1000, help='Time bucket in milliseconds (default: 1000ms = 1s).')

    args = parser.parse_args()
    process_all_csvs(args.csv_dir, args.resolution)

#python3 rosbag_plot_frequency.py --csv_dir /home/chalmers/ADIRFRuleElicitator/RosBagVisualizer/csv_output_path/default_csv --resolution 1000