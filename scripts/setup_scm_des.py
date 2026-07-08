#!/usr/bin/env python3
"""
SCM-DES Setup Script

Sets up the environment for supply chain discrete event simulation.
Ensures CogSim is available and copies sample data files.
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run shell command and return result."""
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)


def setup_cogsim() -> bool:
    """Ensure CogSim is installed."""
    cogsim_path = Path("/home/ubuntu/cogsim")
    
    if cogsim_path.exists() and (cogsim_path / "cogsim" / "__init__.py").exists():
        print("✓ CogSim already installed")
        return True
    
    print("Setting up CogSim...")
    result = run_command("python /home/ubuntu/skills/cogsim-pml/scripts/setup_cogsim.py", check=False)
    
    if result.returncode == 0:
        print("✓ CogSim installed successfully")
        return True
    else:
        print(f"✗ CogSim setup failed: {result.stderr}")
        return False


def copy_sample_data(target_dir: str = ".") -> bool:
    """Copy sample SCM data files to target directory."""
    source_dir = Path("/home/ubuntu/worker-d-scm-extracted/wodog-main/ext/workerd-ext")
    target_path = Path(target_dir)
    
    files_to_copy = ["actors.json", "relationships.json"]
    
    for filename in files_to_copy:
        source_file = source_dir / filename
        target_file = target_path / filename
        
        if source_file.exists():
            if not target_file.exists():
                shutil.copy(source_file, target_file)
                print(f"✓ Copied {filename}")
            else:
                print(f"  {filename} already exists, skipping")
        else:
            print(f"✗ Source file not found: {source_file}")
            return False
    
    return True


def verify_installation() -> bool:
    """Verify the installation works."""
    verify_script = "import sys; sys.path.insert(0, '/home/ubuntu/cogsim'); from cogsim import SimulationEngine, Source, Sink, ResourcePool, ResourceTask; print('CogSim imports successful')"
    
    result = run_command(f'python3 -c "{verify_script}"', check=False)
    
    if result.returncode == 0:
        print("✓ Installation verified")
        return True
    else:
        print(f"✗ Verification failed: {result.stderr}")
        return False


def print_quick_start():
    """Print quick start guide."""
    print("""
SCM-DES Quick Start
===================

1. Ensure you have actors.json and relationships.json in your working directory
   (Sample files copied if not present)

2. Copy the simulation template:
   cp /home/ubuntu/skills/scm-des/templates/scm_simulation.py .

3. Run the simulation:
   python scm_simulation.py

4. Customize the SimulationConfig for your scenario:
   - simulation_time: Duration in minutes
   - capacity_scale: Scale all capacities up/down
   - time_scale: Speed up/slow down processing times

5. Modify actors.json and relationships.json for your supply chain topology

See /home/ubuntu/skills/scm-des/SKILL.md for detailed documentation.
""")


def main():
    """Run setup."""
    print("=" * 60)
    print("SCM-DES Setup")
    print("=" * 60)
    
    # Setup CogSim
    if not setup_cogsim():
        sys.exit(1)
    
    # Copy sample data
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    copy_sample_data(target)
    
    # Verify
    if not verify_installation():
        sys.exit(1)
    
    print_quick_start()


if __name__ == "__main__":
    main()
