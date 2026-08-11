#!/bin/bash

# 1. Ask user for PID
read -p "Enter the Process ID (PID) to find its parent: " target_pid

# 2. Check if PID exists
if ! ps -p "$target_pid" > /dev/null; then
    echo "Error: PID $target_pid not found."
    exit 1
fi

# 3. Get the Parent PID (PPID)
ppid=$(ps -o ppid= -p "$target_pid" | tr -d ' ')

# Ensure we don't try to kill system init (PID 1)
if [[ "$ppid" -le 1 ]]; then
    echo "Error: The parent is PID $ppid (system/init). Refusing to kill."
    exit 1
fi

echo "The Parent PID of $target_pid is: $ppid"
read -p "Are you sure you want to kill PPID $ppid and all its children? (y/N): " confirm

if [[ "$confirm" =~ ^[Yy]$ ]]; then
    echo "Killing process tree for PPID $ppid..."
    
    # Use pkill with -P to kill children, or kill the process group
    # Note: pkill -P $ppid kills children. We also kill the parent itself.
    pkill -P "$ppid"
    kill -9 "$ppid"
    
    echo "Done."
else
    echo "Operation canceled."
fi
