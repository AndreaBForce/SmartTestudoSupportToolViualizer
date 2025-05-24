import os
import sqlite3
import csv

# === Database helpers ===

def connect(sqlite_file):
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    return conn, c

def close(conn):
    conn.close()

def getAllElements(cursor, table_name):
    cursor.execute(f'SELECT * FROM {table_name}')
    return cursor.fetchall()

def getAllTopics(cursor):
    topics = getAllElements(cursor, 'topics')
    return [(row[0], row[1]) for row in topics]  # id, name

def getTimestampsForTopic(cursor, topic_id):
    cursor.execute('SELECT timestamp FROM messages WHERE topic_id = ?', (topic_id,))
    return cursor.fetchall()

# === Main export function ===

def export_timestamps_to_csv(bag_path, output_dir, name_prefix="tb3"):
    os.makedirs(output_dir, exist_ok=True)

    conn, c = connect(bag_path)
    topics = getAllTopics(c)

    for topic_id, topic_name in topics:
        print(f"Exporting timestamps for: {topic_name}")

        try:
            rows = getTimestampsForTopic(c, topic_id)
        except Exception as e:
            print(f"  Could not read timestamps for {topic_name}: {e}")
            continue

        safe_topic_name = topic_name.replace('/', '_').strip('_')
        csv_path = os.path.join(output_dir, f"{name_prefix}_{safe_topic_name}.csv")

        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['timestamp'])

            for (timestamp,) in rows:
                writer.writerow([timestamp])

    close(conn)
    print("\nExport complete (timestamps only).")

# === Entry point ===

if __name__ == "__main__":
    bag_file_path = '/home/chalmers/ADIRFRuleElicitator/RosBagVisualizer/TB_default/TB_default_0.db3'
    output_directory = '/home/chalmers/ADIRFRuleElicitator/RosBagVisualizer/csv_output_path/default_csv'
    export_timestamps_to_csv(bag_file_path, output_directory)
