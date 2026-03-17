"""
BAO analysis from particle coordinates
"""

import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.spatial.distance import pdist

# Conversion factor from simulation units to Mpc
# Adjust this based on your simulation scale
# BAO peak should be around 150 Mpc in real universe
SIMULATION_TO_MPC = 150.0 / 19039487842022736.0  # Your peak / real BAO

def load_positions():
    """Load particle coordinates from latest file"""
    positions_dir = os.path.join("results", "positions")
    if not os.path.exists(positions_dir):
        print("ERROR: Positions folder not found!")
        return None
    
    files = [f for f in os.listdir(positions_dir) if f.startswith("positions_cycle_")]
    if not files:
        print("ERROR: No positions_cycle_*.txt files found!")
        return None
    
    latest = sorted(files)[-1]
    filepath = os.path.join(positions_dir, latest)
    data = np.loadtxt(filepath, skiprows=1)
    print(f"Loaded {len(data)} particles from {latest}")
    return data

def compute_bao_peak(positions):
    """Compute BAO peak from particle distances"""
    # Take only x,y coordinates
    coords = positions[:, :2]
    
    # Compute all pairwise distances
    print("  Computing pairwise distances...")
    distances = pdist(coords)
    print(f"  Calculated {len(distances)} pairs")
    
    # Convert to Mpc
    distances_mpc = distances * SIMULATION_TO_MPC
    
    # Create histogram
    hist, bins = np.histogram(distances_mpc, bins=50)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    
    # Find peak (excluding first few bins)
    start_idx = 5
    peak_idx = start_idx + np.argmax(hist[start_idx:])
    peak_distance = bin_centers[peak_idx]
    
    return bin_centers, hist, peak_distance

def plot_bao(bin_centers, hist, peak_distance):
    """Plot BAO correlation"""
    plt.figure(figsize=(10, 6))
    plt.bar(bin_centers, hist, width=bin_centers[1]-bin_centers[0], 
            alpha=0.7, color='blue', edgecolor='black')
    plt.axvline(x=peak_distance, color='red', linestyle='--', 
                label=f'BAO peak: {peak_distance:.1f} Mpc')
    plt.axvline(x=150, color='green', linestyle=':', alpha=0.7,
                label='Expected BAO: 150 Mpc')
    plt.xlabel("Distance (Mpc)")
    plt.ylabel("Number of pairs")
    plt.title("BAO peak analysis")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig("plots/bao_peak.png", dpi=150)
    plt.show()

def main():
    print("="*60)
    print("BAO ANALYSIS")
    print("="*60)
    
    print(f"\nScale factor: {SIMULATION_TO_MPC:.2e} Mpc/simulation unit")
    
    # Load particle positions
    positions = load_positions()
    if positions is None:
        return
    
    # Compute BAO peak
    bin_centers, hist, peak_distance = compute_bao_peak(positions)
    print(f"\nBAO peak found at: {peak_distance:.1f} Mpc")
    
    # Check if close to expected value
    expected = 150.0
    diff = abs(peak_distance - expected)
    diff_percent = (diff / expected) * 100
    
    if diff_percent < 10:
        print(f" Good match! Within {diff_percent:.1f}% of expected BAO scale")
    else:
        print(f" Peak deviates by {diff_percent:.1f}% from expected 150 Mpc")
        print("  You may need to adjust SIMULATION_TO_MPC constant")
    
    # Plot results
    plot_bao(bin_centers, hist, peak_distance)
    
    # Save results
    with open("bao_result.txt", "w") as f:
        f.write(f"BAO peak: {peak_distance:.2f} Mpc\n")
        f.write(f"Expected: 150 Mpc\n")
        f.write(f"Difference: {diff:.2f} Mpc ({diff_percent:.1f}%)\n")
        f.write(f"Particles: {len(positions)}\n")
        f.write(f"Scale factor: {SIMULATION_TO_MPC:.2e}\n")
    
    print("\nBAO analysis complete")
    print("Plot saved to plots/bao_peak.png")
    print("Results saved to bao_result.txt")

if __name__ == "__main__":
    main()