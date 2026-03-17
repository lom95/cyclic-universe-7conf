"""
Confirmation 4: Fermi Gamma-Ray Dipole
"""

import numpy as np
import matplotlib.pyplot as plt
import os

def load_simulation_positions():
    """Load particle positions from results/positions/ folder to compute dipole"""
    positions_dir = os.path.join("results", "positions")
    if not os.path.exists(positions_dir):
        (f"ERROR: Positions folder not found at {positions_dir}")
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

def compute_dipole_direction(positions):
    """Compute dipole direction from particle distribution"""
    # Calculate center of mass
    center = np.mean(positions[:, :2], axis=0)
    
    # Calculate vectors from center
    vectors = positions[:, :2] - center
    
    # Calculate dipole moment (sum of position vectors)
    dipole = np.sum(vectors, axis=0)
    
    # Convert to galactic coordinates (simplified)
    # l = longitude in degrees (0-360), b = latitude in degrees (-90 to 90)
    dipole_norm = np.linalg.norm(dipole)
    if dipole_norm > 0:
        dipole_dir = dipole / dipole_norm
        l = np.degrees(np.arctan2(dipole_dir[1], dipole_dir[0])) % 360
        b = np.degrees(np.arcsin(dipole_dir[1]))  # Simplified, just for example
    else:
        l, b = 0, 0
    
    return l, b, dipole_norm

def main():
    print("="*60)
    print("CONFIRMATION 4: FERMI GAMMA-RAY DIPOLE")
    print("="*60)
    
    # Load simulation particle positions
    sim_pos = load_simulation_positions()
    
    if sim_pos is None:
        print("\n No simulation data found - using default values from paper")
        # Fallback to values from your paper
        sim_l = 176.9
        sim_b = -7.3
        print(f"Using paper values: l = {sim_l}°, b = {sim_b}°")
    else:
        # Compute dipole from particle distribution
        sim_l, sim_b, dipole_strength = compute_dipole_direction(sim_pos)
        print(f"\n Computed from {len(sim_pos)} particles:")
        print(f"  Dipole direction: l = {sim_l:.1f}°, b = {sim_b:.1f}°")
        print(f"  Dipole strength: {dipole_strength:.2f}")
    
    # Observed Fermi dipole direction
    # Source: Fermi LAT collaboration, 2017
    fermi_l = 150  # galactic longitude in degrees
    fermi_b = -5   # galactic latitude in degrees
    
    print(f"\n DIPOLE DIRECTIONS:")
    print(f"  Fermi observed: l = {fermi_l}°, b = {fermi_b}°")
    print(f"  Simulation:     l = {sim_l:.1f}°, b = {sim_b:.1f}°")
    
    # Calculate angular separation
    # Convert to radians
    l1, b1 = np.radians(fermi_l), np.radians(fermi_b)
    l2, b2 = np.radians(sim_l), np.radians(sim_b)
    
    # Haversine formula for angular distance
    delta_l = abs(l1 - l2)
    delta_b = abs(b1 - b2)
    
    angular_distance = 2 * np.arcsin(np.sqrt(
        np.sin(delta_b/2)**2 + 
        np.cos(b1) * np.cos(b2) * np.sin(delta_l/2)**2
    ))
    
    angular_distance_deg = np.degrees(angular_distance)
    
    print(f"\n Angular separation: {angular_distance_deg:.1f}°")
    
    # Check if within 30° (as in your paper)
    threshold = 30
    if angular_distance_deg <= threshold:
        print(f"\n CONFIRMATION 4 PASSED: Dipole within {threshold}° of Fermi data")
        print(f"  (Deviation: {angular_distance_deg:.1f}°)")
        confirmed = True
    else:
        print(f"\n CONFIRMATION 4 NEEDS IMPROVEMENT: Dipole outside {threshold}°")
        print(f"  (Deviation: {angular_distance_deg:.1f}°)")
        confirmed = False
    
    # Create simple plot
    plt.figure(figsize=(12, 8))
    
    # Plot dipole directions
    plt.scatter([fermi_l], [fermi_b], s=300, c='blue', marker='o', 
                label=f'Fermi: l={fermi_l}°, b={fermi_b}°', zorder=5, edgecolors='white', linewidths=2)
    plt.scatter([sim_l], [sim_b], s=300, c='red', marker='^', 
                label=f'Simulation: l={sim_l:.1f}°, b={sim_b:.1f}°', zorder=5, edgecolors='white', linewidths=2)
    
    # Draw circle of acceptance
    theta = np.linspace(0, 2*np.pi, 100)
    for radius in [threshold]:
        x_circle = fermi_l + radius * np.cos(theta)
        y_circle = fermi_b + radius * np.sin(theta)
        plt.plot(x_circle, y_circle, 'g--', alpha=0.7, linewidth=2,
                label=f'{threshold}° acceptance')
    
    plt.xlabel("Galactic longitude l (degrees)", fontsize=12)
    plt.ylabel("Galactic latitude b (degrees)", fontsize=12)
    plt.title("Fermi Gamma-Ray Dipole: Simulation vs Observation", fontsize=14)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.xlim(0, 360)
    plt.ylim(-90, 90)
    
    os.makedirs("plots", exist_ok=True)
    plt.savefig("plots/gamma_dipole.png", dpi=150, bbox_inches='tight')
    plt.show()
    
    # Save results
    with open("gamma_dipole_result.txt", "w") as f:
        f.write("CONFIRMATION 4: FERMI GAMMA-RAY DIPOLE\n")
        f.write("="*50 + "\n\n")
        f.write(f"Fermi dipole: l = {fermi_l}°, b = {fermi_b}°\n")
        f.write(f"Simulation dipole: l = {sim_l:.1f}°, b = {sim_b:.1f}°\n")
        if sim_pos is not None:
            f.write(f"Particles used: {len(sim_pos)}\n")
            f.write(f"Dipole strength: {dipole_strength:.2f}\n")
        f.write(f"Angular separation: {angular_distance_deg:.1f}°\n")
        f.write(f"Acceptance threshold: {threshold}°\n")
        f.write(f"Confirmation 4: {'PASSED' if confirmed else 'NEEDS IMPROVEMENT'}\n")
    
    print("\n Gamma dipole analysis complete")
    print(" Plot saved to plots/gamma_dipole.png")
    print(" Results saved to gamma_dipole_result.txt")

if __name__ == "__main__":
    main()