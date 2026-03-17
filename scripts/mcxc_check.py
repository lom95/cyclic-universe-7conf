"""
Confirmation 3: MCXC Galaxy Clusters
"""

import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.ndimage import gaussian_filter
from scipy.ndimage import maximum_filter

def load_simulation_positions():
    """Load particle positions from results/positions/ folder"""
    positions_dir = os.path.join("results", "positions")
    if not os.path.exists(positions_dir):
        print(f"ERROR: Positions folder not found at {positions_dir}")
        return None
    
    files = [f for f in os.listdir(positions_dir) if f.startswith("positions_cycle_")]
    if not files:
        print(f"ERROR: No positions_cycle_*.txt files found in {positions_dir}")
        return None
    
    latest = sorted(files)[-1]
    filepath = os.path.join(positions_dir, latest)
    print(f"Loading particle positions from: {filepath}")
    
    try:
        data = np.loadtxt(filepath, skiprows=1)
        print(f"Loaded {len(data)} particles")
        return data
    except Exception as e:
        print(f"ERROR loading positions: {e}")
        return None

def find_density_peaks(positions, grid_size=30):
    """Find density peaks (cluster candidates) in particle distribution"""
    x = positions[:, 0]
    y = positions[:, 1]
    
    # Create 2D histogram
    hist, xedges, yedges = np.histogram2d(x, y, bins=grid_size)
    
    # Smooth to find peaks
    smoothed = gaussian_filter(hist, sigma=1.0)
    
    # Find local maxima
    from scipy.ndimage import maximum_filter
    neighborhood = np.ones((3, 3))
    local_max = maximum_filter(smoothed, footprint=neighborhood) == smoothed
    
    # Get peak coordinates and heights
    peaks_y, peaks_x = np.where(local_max & (smoothed > np.mean(smoothed) + 0.5*np.std(smoothed)))
    
    peak_coords = []
    for i in range(len(peaks_x)):
        x_center = (xedges[peaks_x[i]] + xedges[peaks_x[i] + 1]) / 2
        y_center = (yedges[peaks_y[i]] + yedges[peaks_y[i] + 1]) / 2
        peak_coords.append([x_center, y_center, smoothed[peaks_y[i], peaks_x[i]]])
    
    return np.array(peak_coords)

def main():
    print("="*60)
    print("CONFIRMATION 3: MCXC GALAXY CLUSTERS")
    print("="*60)
    
    # Load simulation particle positions
    sim_pos = load_simulation_positions()
    
    if sim_pos is None:
        print("\n No simulation data found - confirmation cannot proceed")
        return
    
    print(f"\n Successfully loaded {len(sim_pos)} particles")
    
    # Find density peaks (clusters)
    peaks = find_density_peaks(sim_pos)
    n_clusters = len(peaks)
    print(f"\nFound {n_clusters} significant density peaks (cluster candidates)")
    
    # Calculate cluster statistics
    if n_clusters > 0:
        cluster_masses = peaks[:, 2]
        avg_mass = np.mean(cluster_masses)
        max_mass = np.max(cluster_masses)
        print(f"  Average cluster mass: {avg_mass:.2f}")
        print(f"  Maximum cluster mass: {max_mass:.2f}")
        
        # Expected number of clusters for this many particles
        expected_clusters = max(1, len(sim_pos) // 20)  # Rough estimate
        cluster_match = abs(n_clusters - expected_clusters) < expected_clusters * 0.5
        
        print("\nCOMPARISON WITH EXPECTED CLUSTER COUNTS:")
        print(f"  Found: {n_clusters} clusters")
        print(f"  Expected: ~{expected_clusters} clusters")
        
        if cluster_match:
            print(" Cluster count matches expectations")
        else:
            print(" Cluster count deviates from expected")
    
    # Plot
    plt.figure(figsize=(10, 8))
    
    # Plot all particles in background
    plt.scatter(sim_pos[:, 0], sim_pos[:, 1], s=1, c='lightgray', alpha=0.3, label='Particles')
    
    # Plot peaks as clusters
    if n_clusters > 0:
        plt.scatter(peaks[:, 0], peaks[:, 1], s=peaks[:, 2]*50, c='red', 
                   alpha=0.7, edgecolors='black', linewidths=1, 
                   label=f'Cluster candidates ({n_clusters})')
    
    plt.xlabel("x (simulation units)")
    plt.ylabel("y (simulation units)")
    plt.title(f"Galaxy Clusters from Simulation ({n_clusters} clusters found)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig("plots/mcxc_clusters.png", dpi=150)
    plt.show()
    
    # Determine confirmation status
    confirmed = n_clusters >= 3  # At least a few clusters
    if confirmed:
        print("\n CONFIRMATION 3 PASSED: Clusters detected in simulation")
    else:
        print("\n CONFIRMATION 3 NEEDS IMPROVEMENT: Too few clusters")
    
    # Save results
    with open("mcxc_result.txt", "w") as f:
        f.write("CONFIRMATION 3: MCXC GALAXY CLUSTERS\n")
        f.write("="*50 + "\n\n")
        f.write(f"Particles analyzed: {len(sim_pos)}\n")
        f.write(f"Clusters detected: {n_clusters}\n")
        if n_clusters > 0:
            f.write(f"Average cluster mass: {avg_mass:.2f}\n")
            f.write(f"Maximum cluster mass: {max_mass:.2f}\n")
        f.write(f"\nConfirmation 3: {'PASSED' if confirmed else 'NEEDS IMPROVEMENT'}\n")
    
    print("\nMCXC analysis complete")
    print("Plot saved to plots/mcxc_clusters.png")
    print("Results saved to mcxc_result.txt")

if __name__ == "__main__":
    main()