#!/bin/bash
# GPU Monitoring Script for ExFrame Performance Analysis

echo "Starting GPU monitoring..."
echo "Press Ctrl+C to stop"
echo ""

# Check if nvidia-smi exists
if ! command -v nvidia-smi &> /dev/null; then
    echo "Error: nvidia-smi not found. Install NVIDIA drivers or run on GPU-enabled system."
    exit 1
fi

# Show header
echo "Timestamp | GPU Util | Mem Used/Total | Temp | Power | Processes"
echo "--------------------------------------------------------------------------"

# Monitor loop
while true; do
    timestamp=$(date +"%H:%M:%S")

    # Get GPU stats
    stats=$(nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw --format=csv,noheader,nounits)

    # Get running processes count
    procs=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l)

    # Parse stats
    util=$(echo $stats | cut -d',' -f1)
    mem_used=$(echo $stats | cut -d',' -f2)
    mem_total=$(echo $stats | cut -d',' -f3)
    temp=$(echo $stats | cut -d',' -f4)
    power=$(echo $stats | cut -d',' -f5)

    # Format output
    printf "%s | %3s%%     | %5sMB/%5sMB | %3s°C | %5sW | %d\n" \
        "$timestamp" "$util" "$mem_used" "$mem_total" "$temp" "$power" "$procs"

    sleep 1
done
