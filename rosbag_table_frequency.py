import os
import argparse
import pandas as pd

def compute_avg_frequency(csv_file, resolution_ms):
    try:
        df = pd.read_csv(csv_file)
        timestamp_col = next((col for col in df.columns if 'timestamp' in col.lower()), None)
        if not timestamp_col or df.empty:
            return None

        df[timestamp_col] = pd.to_datetime(df[timestamp_col], unit='ns')
        df.set_index(timestamp_col, inplace=True)
        bucket_str = f'{int(resolution_ms)}ms'
        freq_series = df.resample(bucket_str).size()
        return freq_series.mean()
    except:
        return None

def extract_frequencies(folder, resolution_ms):
    frequencies = {}
    for filename in os.listdir(folder):
        if filename.endswith('.csv'):
            filepath = os.path.join(folder, filename)
            topic_name = filename.replace('.csv', '')
            avg_freq = compute_avg_frequency(filepath, resolution_ms)
            if avg_freq is not None:
                frequencies[topic_name] = avg_freq
    return frequencies

def compare_frequencies(default_folder, smart_folder, resolution_ms):
    default_freqs = extract_frequencies(default_folder, resolution_ms)
    smart_freqs = extract_frequencies(smart_folder, resolution_ms)

    all_topics = sorted(set(default_freqs.keys()) | set(smart_freqs.keys()))
    rows = []

    for topic in all_topics:
        default_val = default_freqs.get(topic, 0)
        smart_val = smart_freqs.get(topic, 0)
        if default_val == 0 and smart_val == 0:
            change = 0
        elif default_val == 0:
            change = 100.0
        else:
            change = ((smart_val - default_val) / default_val) * 100

        rows.append((topic, f"{default_val:.2f}", f"{smart_val:.2f}", f"{change:+.2f}%"))

    return rows

def print_table(rows):
    header = f"{'Topic':<40} {'Default (Hz)':>12} {'SmartTestudo (Hz)':>20} {'Change (%)':>14}"
    divider = "-" * len(header)
    print(header)
    print(divider)
    for row in rows:
        print(f"{row[0]:<40} {row[1]:>12} {row[2]:>20} {row[3]:>14}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare average message frequencies from two ROS CSV folders.")
    parser.add_argument("--default_folder", type=str, required=True, help="Path to default CSV folder.")
    parser.add_argument("--smart_folder", type=str, required=True, help="Path to SmartTestudo CSV folder.")
    parser.add_argument("--resolution", type=int, default=1000, help="Time bucket in ms for resampling (default: 1000ms).")

    args = parser.parse_args()
    rows = compare_frequencies(args.default_folder, args.smart_folder, args.resolution)
    print_table(rows)

#python3 rosbag_table_frequency.py --default_folder /home/chalmers/ADIRFRuleElicitator/RosBagVisualizer/csv_output_path/default_csv --smart_folder /home/chalmers/ADIRFRuleElicitator/RosBagVisualizer/csv_output_path/testudo_csv --resolution 1000