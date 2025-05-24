import os
import pandas as pd

def load_bandwidth_stats(folder):
    stats = {}
    for file in os.listdir(folder):
        if file.endswith('_bandwidth_only.csv'):
            topic = file.replace('_bandwidth_only.csv', '')
            df = pd.read_csv(os.path.join(folder, file), index_col=0)
            avg_bw = df.iloc[:, 0].mean()
            stats[topic] = avg_bw
    return stats

def compare_bandwidths(folder1, folder2):
    stats1 = load_bandwidth_stats(folder1)
    stats2 = load_bandwidth_stats(folder2)

    all_topics = sorted(set(stats1) | set(stats2))
    print(f"{'Topic':40} {'Default (kbps)':>20} {'SmartTestudo (kbps)':>20} {'Change (%)':>15}")
    print('-' * 95)

    for topic in all_topics:
        bw1 = stats1.get(topic, 0)
        bw2 = stats2.get(topic, 0)
        if bw1 == 0 and bw2 == 0:
            pct_change = 'N/A'
        elif bw1 == 0:
            pct_change = '∞'
        else:
            pct_change = f"{((bw2 - bw1) / bw1) * 100:.2f}"
        print(f"{topic:40} {bw1:20.2f} {bw2:20.2f} {pct_change:>15}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compare bandwidth stats between two folders.")
    parser.add_argument('--folder1', type=str, required=True, help='First bandwidth folder.')
    parser.add_argument('--folder2', type=str, required=True, help='Second bandwidth folder.')
    args = parser.parse_args()

    compare_bandwidths(args.folder1, args.folder2)

#python3 rosbag_table_bandwidth.py --folder1 /home/chalmers/ADIRFRuleElicitator/RosBagVisualizer/csv_output_path/default_csv/bandwidth_only --folder2 /home/chalmers/ADIRFRuleElicitator/RosBagVisualizer/csv_output_path/testudo_csv/bandwidth_only
