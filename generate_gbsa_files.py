#!/usr/bin/env python3
"""
Script to automatically generate GBSA input files in analysis subdirectories.

This script searches for all directories that contain a subdirectory named 'analysis'
starting from the current directory. For each directory that has an 'analysis' subdirectory,
it creates a new subdirectory inside it named 'gbsa' (if it doesn't already exist) and
populates it with the required input files.
"""

import os
import sys
from pathlib import Path


# File templates
FILE_TEMPLATES = {
    'pt-strip-Q94R.in': """parm ./strip.1xjv_POT1_ssDNA-Q94R_wat.prmtop

trajin 1xjv_POT1_ssDNA-Q94R_wat_imaged_26-1025.nc

autoimage origin
strip :WAT,K+

trajout 1xjv_POT1_ssDNA_Q94R_wat_MMPBSA_26-1025.nc netcdf
run
""",
    
    'pt-parmstrip_rec.in': """parm ./strip.1xjv_POT1_ssDNA-Q94R_wat.prmtop

parmstrip :WAT,K+
parmstrip :295-304

parmwrite out rec.prmtop

""",
    
    'pt-parmstrip_lig.in': """parm ./strip.1xjv_POT1_ssDNA-Q94R_wat.prmtop

parmstrip :WAT,K+
parmstrip :1-294

parmwrite out lig.prmtop

""",
    
    'pt-parmstrip_com.in': """parm ./strip.1xjv_POT1_ssDNA-Q94R_wat.prmtop

parmstrip :WAT,K+

parmwrite out com.prmtop

""",
    
    'MM-GBSA.sh': """#!/bin/bash
#SBATCH --job-name=mmpbsa
#SBATCH --output=mmpbsa.out       
#SBATCH --error=mmpbsa.err
#SBATCH --nodes=1
#SBATCH --mem=6G
#SBATCH --partition=cisneros
#SBATCH --nodelist=g-02-04

module load openmpi4/4.1.1
module load cuda/11.7.0
module load amber/24-cuda
module list

#cpptraj -i pt-strip.in > pt-strip.log
#cpptraj -i pt-parmstrip_com.in > pt-parmstrip_com.log
#cpptraj -i pt-parmstrip_tox.in > pt-parmstrip_tox.log
#cpptraj -i pt-parmstrip_anti.in > pt-parmstrip_anti.log

mpirun -np 1 MMPBSA.py.MPI -O -i MM-GBSA.in -o mmgbsa.dat -cp com.prmtop -rp rec.prmtop -lp lig.prmtop -y 1xjv_POT1_ssDNA_Q94R_wat_MMPBSA_26-1025.nc > mmgbsa.log

""",
    
    'MM-GBSA.in': """&general
   startframe=167500,
   endframe=177500,
   interval=1,
   receptor_mask=":1-294",
   ligand_mask=":295-304",
   verbose=1,
   keep_files=2,
   debug_printlevel=1,
   netcdf=1,
   use_sander=1
/
&gb
  igb=5, 
  saltcon=0.150,
/
"""
}


def find_analysis_directories(start_path='.'):
    """
    Find all directories that contain an 'analysis' subdirectory.
    
    Args:
        start_path: The starting directory for the search (default: current directory)
    
    Returns:
        List of Path objects representing directories containing 'analysis' subdirectory
    """
    analysis_dirs = []
    start_path = Path(start_path).resolve()
    
    # Walk through the directory tree
    for root, dirs, files in os.walk(start_path):
        if 'analysis' in dirs:
            analysis_path = Path(root) / 'analysis'
            analysis_dirs.append(analysis_path)
    
    return analysis_dirs


def create_gbsa_directory(analysis_path):
    """
    Create a 'gbsa' subdirectory inside the given 'analysis' directory.
    
    Args:
        analysis_path: Path to the 'analysis' directory
    
    Returns:
        Path object representing the created 'gbsa' directory
    """
    gbsa_path = analysis_path / 'gbsa'
    
    if gbsa_path.exists():
        print(f"GBSA directory already exists: {gbsa_path}")
    else:
        gbsa_path.mkdir(parents=True, exist_ok=True)
        print(f"Created GBSA directory: {gbsa_path}")
    
    return gbsa_path


def generate_files(gbsa_path):
    """
    Generate all required files in the 'gbsa' directory.
    
    Args:
        gbsa_path: Path to the 'gbsa' directory
    """
    for filename, content in FILE_TEMPLATES.items():
        file_path = gbsa_path / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Make shell script executable
        if filename.endswith('.sh'):
            file_path.chmod(0o755)
        
        print(f"  Generated file: {file_path}")


def main():
    """
    Main function to execute the script.
    """
    print("Starting GBSA file generation script...")
    print(f"Searching for 'analysis' directories from: {Path.cwd()}")
    print("-" * 80)
    
    # Find all 'analysis' directories
    analysis_dirs = find_analysis_directories()
    
    if not analysis_dirs:
        print("No 'analysis' directories found.")
        return 0
    
    print(f"Found {len(analysis_dirs)} 'analysis' director{'y' if len(analysis_dirs) == 1 else 'ies'}:")
    for analysis_path in analysis_dirs:
        print(f"  - {analysis_path}")
    
    print("-" * 80)
    
    # Process each 'analysis' directory
    for analysis_path in analysis_dirs:
        print(f"\nProcessing: {analysis_path}")
        
        # Create 'gbsa' subdirectory
        gbsa_path = create_gbsa_directory(analysis_path)
        
        # Generate files
        generate_files(gbsa_path)
    
    print("-" * 80)
    print("GBSA file generation completed successfully!")
    
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
