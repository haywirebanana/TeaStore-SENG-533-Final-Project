import subprocess
import pandas as pd
import time
import datetime
import threading
import matplotlib.pyplot as plt

# Output CSV file
output_file = "docker_stats.csv"

# Dictionary to store container data over time
data = {"Time": []}
containers = []
stop_flag = False  # Flag to stop monitoring

# Function to get docker stats
def get_docker_stats():
    global containers
    result = subprocess.run(
        ["docker", "stats", "--no-stream", "--format", "{{.Name}},{{.CPUPerc}},{{.MemUsage}}"],
        capture_output=True,
        text=True
    )
    
    lines = result.stdout.strip().split("\n")
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    if not containers:
        containers = [line.split(",")[0] for line in lines]
        for container in containers:
            data[f"{container} CPU (%)"] = []
            data[f"{container} Mem (MB)"] = []

    data["Time"].append(timestamp)

    for line in lines:
        parts = line.split(",")
        container_name = parts[0]
        cpu_usage = float(parts[1].replace("%", ""))
        mem_usage = float(parts[2].split("/")[0].strip().replace("MiB", "").replace("MB", "").replace("GiB", "").replace("GB", ""))

        data[f"{container_name} CPU (%)"].append(cpu_usage)
        data[f"{container_name} Mem (MB)"].append(mem_usage)

# Function to listen for user input
def wait_for_exit():
    global stop_flag
    input("Press Enter to stop monitoring...\n")
    stop_flag = True

# Start input listener thread
input_thread = threading.Thread(target=wait_for_exit, daemon=True)
input_thread.start()

print("Monitoring Docker stats... Press Enter to stop.")

# Monitor loop
try:
    while not stop_flag:
        get_docker_stats()
        time.sleep(1)

except KeyboardInterrupt:
    print("\nMonitoring stopped by user.")

# Convert data to DataFrame and save CSV
df = pd.DataFrame(data)
df.to_csv(output_file, index=False)
print(f"Saved Docker stats to {output_file}")

# Plot CPU and Memory usage for each container
plt.figure(figsize=(12, 6))
for container in containers:
    plt.plot(df["Time"], df[f"{container} CPU (%)"], label=f"{container} CPU (%)")

plt.xlabel("Time")
plt.ylabel("CPU Usage (%)")
plt.title("CPU Usage Over Time")
plt.xticks(rotation=45)
plt.legend()
plt.grid()
plt.savefig("docker_cpu_usage.png")


plt.figure(figsize=(12, 6))
for container in containers:
    plt.plot(df["Time"], df[f"{container} Mem (MB)"], label=f"{container} Mem (MB)")

plt.xlabel("Time")
plt.ylabel("Memory Usage (MB)")
plt.title("Memory Usage Over Time")
plt.xticks(rotation=45)
plt.legend()
plt.grid()
plt.savefig("docker_memory_usage.png")
