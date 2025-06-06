#!/usr/bin/env python
"""
Demo script for the training process with reduced parameters for quick demonstration
"""

import os
import sys

# Override config values for demo
import config
config.CPUS = 4  # Reduce CPU usage for demo
config.selfplaygames = 10  # Reduce self-play games
config.SIM_NUMBER = 10  # Reduce MCTS simulations
config.EPOCHS = 1  # Reduce training epochs
config.tournamentloop = 1  # Reduce tournament games
config.max_iterations = 2  # Only 2 iterations for demo

print("=== Alpha Zero Training Demo ===")
print("Note: This is a demonstration with reduced parameters.")
print("Full training would use:")
print(f"- 40 CPUs (demo: {config.CPUS})")
print(f"- 400 self-play games (demo: {config.selfplaygames})")
print(f"- 30+ MCTS simulations (demo: {config.SIM_NUMBER})")
print(f"- 4 training epochs (demo: {config.EPOCHS})")
print(f"- 1000 iterations (demo: {config.max_iterations})")
print()

# Create data directory if it doesn't exist
if not os.path.exists('./data'):
    os.makedirs('./data')
    print("Created ./data directory for temporary game files")

# Import and run the main training loop
from Main import launch

print("\nStarting training demo...")
print("This will:")
print("1. Load the existing trained model")
print("2. Generate self-play games")
print("3. Try to improve the model")
print("4. Evaluate against previous version")
print()

try:
    launch()
except KeyboardInterrupt:
    print("\n\nTraining interrupted by user.")
except Exception as e:
    print(f"\n\nError during training: {e}")
    
print("\nDemo completed!")