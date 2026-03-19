import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# Get all CSV files in current folder (or change path)
file_paths = glob.glob("*.csv")

plt.figure(figsize=(8, 5))

for file in file_paths:
    df = pd.read_csv(file)

    # --- Detect column names automatically ---
    columns = [c.lower() for c in df.columns]

    if "timestamp" in columns:
        timestamp_col = df.columns[columns.index("timestamp")]
    elif "time" in columns:
        timestamp_col = df.columns[columns.index("time")]
    else:
        raise ValueError(f"No timestamp column found in {file}")

    if "mac" in columns:
        mac_col = df.columns[columns.index("mac")]
    elif "addr2" in columns:
        mac_col = df.columns[columns.index("addr2")]
    else:
        raise ValueError(f"No MAC column found in {file}")

    # --- Process data ---
    df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors='coerce')
    df = df.dropna(subset=[timestamp_col])
    df = df.sort_values(timestamp_col)

    # Normalize time per file
    start_time = df[timestamp_col].min()
    df["minutes_since_start"] = (df[timestamp_col] - start_time).dt.total_seconds() / 60

    # Compute cumulative unique MACs
    seen = set()
    cumulative = []

    for mac in df[mac_col]:
        seen.add(mac)
        cumulative.append(len(seen))

    df["cumulative_unique"] = cumulative

    # Use filename (without extension) as label
    label = os.path.splitext(os.path.basename(file))[0]

    # Plot
    plt.plot(df["minutes_since_start"], df["cumulative_unique"], linewidth=2, label=label)

# --- Final plot formatting ---
plt.xlabel("Time since start (minutes)")
plt.ylabel("Cumulative unique MAC addresses")
plt.title("Growth of unique MAC addresses across environments")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

# Save
plt.savefig("multi_environment_macs.png", dpi=300)

plt.show()