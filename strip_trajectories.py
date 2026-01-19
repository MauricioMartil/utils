#!/usr/bin/env python3
"""
Script to perform trajectory stripping using cpptraj for molecular dynamics analysis.

This script finds mutation directories containing MMGBSA files, generates cpptraj
input files to strip trajectories (frames 825-850), creates SLURM batch scripts,
and submits the jobs for processing. After stripping, it reports the total number
of frames in each trajectory.
"""

import os
import sys
import subprocess
import traceback
from pathlib import Path


def write_strip_traj(output_path, mutation, prmtop_file, input_nc_file, output_nc_file):
    """
    Write cpptraj input file for stripping trajectory frames 825-850.
    
    Args:
        output_path: Path where the cpptraj input file will be written
        mutation: The mutation name
        prmtop_file: Path to the topology file (prmtop)
        input_nc_file: Path to the input NetCDF trajectory file
        output_nc_file: Name of the output stripped NetCDF file
    
    Returns:
        Path to the created cpptraj input file
    """
    input_filename = output_path / f'strip_traj_{mutation}.in'
    
    content = f"""parm {prmtop_file}

trajin {input_nc_file} 825 850

autoimage origin
strip :WAT,K+

trajout {output_nc_file} netcdf
run
"""
    
    with open(input_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  Created cpptraj input file: {input_filename}")
    return input_filename


def write_strip_bash(output_path, mutation, cpptraj_input_file):
    """
    Write SLURM batch script for running cpptraj stripping job.
    
    Args:
        output_path: Path where the SLURM script will be written
        mutation: The mutation name
        cpptraj_input_file: Path to the cpptraj input file
    
    Returns:
        Path to the created SLURM script
    """
    script_filename = output_path / f'strip_traj_{mutation}.sh'
    
    content = f"""#!/bin/bash
#SBATCH --job-name=strip_{mutation}
#SBATCH --output=strip_{mutation}.out
#SBATCH --error=strip_{mutation}.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --partition=cisneros
#SBATCH --nodelist=g-02-04

module load amber/24-cuda
module list

echo "Starting trajectory stripping for {mutation}..."
echo "Input file: {cpptraj_input_file.name}"
echo "Working directory: $(pwd)"

cpptraj -i {cpptraj_input_file.name} > strip_{mutation}.log 2>&1

echo "Stripping completed!"
"""
    
    with open(script_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Make script executable
    script_filename.chmod(0o755)
    
    print(f"  Created SLURM batch script: {script_filename}")
    return script_filename


def submit_slurm_job(script_path):
    """
    Submit a SLURM job using sbatch.
    
    Args:
        script_path: Path to the SLURM batch script
    
    Returns:
        Tuple of (success: bool, job_id: str or error_message: str)
    """
    try:
        result = subprocess.run(
            ['sbatch', str(script_path)],
            capture_output=True,
            text=True,
            check=True,
            cwd=script_path.parent
        )
        
        # Extract job ID from output (format: "Submitted batch job 12345")
        output = result.stdout.strip()
        if 'Submitted batch job' in output:
            job_id = output.split()[-1]
            print(f"  Submitted SLURM job: {job_id}")
            return True, job_id
        else:
            print(f"  Unexpected sbatch output: {output}")
            return False, output
            
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to submit job: {e.stderr}"
        print(f"  ERROR: {error_msg}")
        return False, error_msg
    except FileNotFoundError:
        error_msg = "sbatch command not found. Are you on a SLURM cluster?"
        print(f"  WARNING: {error_msg}")
        return False, error_msg


def count_trajectory_frames(prmtop_file, nc_file):
    """
    Count the total number of frames in a NetCDF trajectory file using cpptraj.
    
    Args:
        prmtop_file: Path to the topology file (prmtop)
        nc_file: Path to the NetCDF trajectory file
    
    Returns:
        Integer number of frames, or None if unable to determine
    """
    # Create a temporary cpptraj input file to count frames
    temp_input = f"""parm {prmtop_file}
trajin {nc_file}
run
"""
    
    try:
        # Run cpptraj and capture output
        result = subprocess.run(
            ['cpptraj'],
            input=temp_input,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Parse output to find frame count
        # cpptraj typically outputs something like "Read 1000 frames"
        for line in result.stdout.split('\n'):
            if 'frames' in line.lower() and 'read' in line.lower():
                # Extract number from line
                words = line.split()
                for i, word in enumerate(words):
                    if word.lower() == 'read' and i + 1 < len(words):
                        try:
                            return int(words[i + 1])
                        except ValueError:
                            continue
        
        return None
        
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return None


def find_mutation_directories(start_path='.'):
    """
    Find all mutation directories that contain MMGBSA-related files.
    
    Looks for directories containing 'analysis/gbsa' subdirectories which
    typically contain MMGBSA input files and topology files.
    
    Args:
        start_path: The starting directory for the search (default: current directory)
    
    Returns:
        List of tuples (gbsa_path, mutation_name) where gbsa_path is the path
        to the gbsa directory and mutation_name is the parent directory name
    """
    mutation_dirs = []
    start_path = Path(start_path).resolve()
    
    # Walk through the directory tree looking for analysis/gbsa directories
    for root, dirs, files in os.walk(start_path):
        root_path = Path(root)
        
        # Check if this is an analysis directory containing gbsa
        if root_path.name == 'analysis' and 'gbsa' in dirs:
            gbsa_path = root_path / 'gbsa'
            parent_path = root_path.parent
            mutation_name = parent_path.name
            mutation_dirs.append((gbsa_path, mutation_name))
    
    return mutation_dirs


def find_trajectory_files(gbsa_path, mutation):
    """
    Find the prmtop and NetCDF trajectory files needed for stripping.
    
    Args:
        gbsa_path: Path to the gbsa directory
        mutation: The mutation name
    
    Returns:
        Tuple of (prmtop_file, nc_file) or (None, None) if not found
    """
    # Look for prmtop file - common patterns
    prmtop_patterns = [
        f'strip.1xjv_POT1_ssDNA-{mutation}_wat.prmtop',
        f'1xjv_POT1_ssDNA-{mutation}_wat.prmtop',
        f'{mutation}_wat.prmtop',
        'strip.*.prmtop',
        '*.prmtop'
    ]
    
    prmtop_file = None
    for pattern in prmtop_patterns:
        matches = list(gbsa_path.glob(pattern))
        if matches:
            prmtop_file = matches[0]
            break
    
    # Look for NetCDF trajectory file - common patterns
    nc_patterns = [
        f'1xjv_POT1_ssDNA-{mutation}_wat_imaged_*.nc',
        f'*{mutation}*.nc',
        '*.nc'
    ]
    
    nc_file = None
    for pattern in nc_patterns:
        matches = list(gbsa_path.glob(pattern))
        if matches:
            # Filter out the output file we'll create
            matches = [m for m in matches if 'AF-' not in m.name and ('gbsa' in m.name or 'imaged' in m.name)]
            if matches:
                nc_file = matches[0]
                break
    
    return prmtop_file, nc_file


def main():
    """
    Main function to execute the trajectory stripping script.
    """
    print("=" * 80)
    print("Trajectory Stripping Script")
    print("=" * 80)
    print(f"Searching for mutation directories from: {Path.cwd()}")
    print(f"Frame range to extract: 825-850 (inclusive)")
    print("-" * 80)
    
    # Find all mutation directories with MMGBSA files
    mutation_dirs = find_mutation_directories()
    
    if not mutation_dirs:
        print("No mutation directories with MMGBSA files found.")
        print("Looking for directories with 'analysis/gbsa' structure.")
        return 1
    
    print(f"Found {len(mutation_dirs)} mutation director{'y' if len(mutation_dirs) == 1 else 'ies'}:")
    for gbsa_path, mutation in mutation_dirs:
        print(f"  - {gbsa_path} (mutation: {mutation})")
    
    print("-" * 80)
    
    # Process each mutation directory
    successful_jobs = []
    failed_jobs = []
    frame_counts = {}
    
    for gbsa_path, mutation in mutation_dirs:
        print(f"\nProcessing mutation: {mutation}")
        print(f"  GBSA directory: {gbsa_path}")
        
        # Find required files
        prmtop_file, nc_file = find_trajectory_files(gbsa_path, mutation)
        
        if not prmtop_file:
            print(f"  ERROR: Could not find prmtop file in {gbsa_path}")
            failed_jobs.append((mutation, "prmtop file not found"))
            continue
        
        if not nc_file:
            print(f"  ERROR: Could not find NetCDF trajectory file in {gbsa_path}")
            failed_jobs.append((mutation, "trajectory file not found"))
            continue
        
        print(f"  Found topology file: {prmtop_file.name}")
        print(f"  Found trajectory file: {nc_file.name}")
        
        # Count frames in the trajectory
        frame_count = count_trajectory_frames(prmtop_file, nc_file)
        if frame_count:
            frame_counts[mutation] = frame_count
            print(f"  Trajectory contains {frame_count} frames")
        
        # Define output file name
        output_nc_file = f'AF-{mutation}_solv_gbsa_750.nc'
        
        # Create cpptraj input file
        cpptraj_input = write_strip_traj(
            gbsa_path,
            mutation,
            prmtop_file.name,
            nc_file.name,
            output_nc_file
        )
        
        # Create SLURM batch script
        slurm_script = write_strip_bash(gbsa_path, mutation, cpptraj_input)
        
        # Submit SLURM job
        success, job_info = submit_slurm_job(slurm_script)
        
        if success:
            successful_jobs.append((mutation, job_info))
            print(f"  ✓ Successfully set up stripping for {mutation}")
        else:
            failed_jobs.append((mutation, job_info))
            print(f"  ✗ Failed to submit job for {mutation}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if successful_jobs:
        print(f"\n✓ Successfully submitted {len(successful_jobs)} job(s):")
        for mutation, job_id in successful_jobs:
            print(f"  - {mutation}: Job ID {job_id}")
    
    if failed_jobs:
        print(f"\n✗ Failed to process {len(failed_jobs)} mutation(s):")
        for mutation, error in failed_jobs:
            print(f"  - {mutation}: {error}")
    
    # Print frame counts
    if frame_counts:
        print("\n" + "-" * 80)
        print("TRAJECTORY FRAME COUNTS")
        print("-" * 80)
        for mutation, count in frame_counts.items():
            print(f"  {mutation}: {count} total frames in trajectory")
    
    print("\n" + "=" * 80)
    print("Trajectory stripping script completed!")
    print("=" * 80)
    
    return 0 if not failed_jobs else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
