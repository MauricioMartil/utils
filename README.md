# Utility Scripts

This repository contains utility scripts for various tasks.

## generate_gbsa_files.py

A Python script that automatically generates GBSA (Generalized Born Surface Area) input files in analysis subdirectories.

### Purpose

This script searches for all directories that contain a subdirectory named 'analysis' starting from the current directory. For each directory that has an 'analysis' subdirectory, it creates a new subdirectory inside it named 'gbsa' (if it doesn't already exist) and populates it with the required input files. The script automatically uses the parent directory name (e.g., "Q94R", "WT") as the mutation identifier in all generated files.

### Usage

```bash
cd /path/to/your/project
python3 generate_gbsa_files.py
```

Or make it executable and run directly:

```bash
chmod +x generate_gbsa_files.py
./generate_gbsa_files.py
```

### Generated Files

The script creates the following files in each `analysis/gbsa/` directory:

1. **pt-strip-{mutation}.in** - Trajectory stripping input file (e.g., pt-strip-Q94R.in)
2. **pt-parmstrip_rec.in** - Parameter stripping for receptor
3. **pt-parmstrip_lig.in** - Parameter stripping for ligand
4. **pt-parmstrip_com.in** - Parameter stripping for complex
5. **MM-GBSA.sh** - SLURM batch script for running MM-GBSA calculations (4 CPUs, 16GB RAM, oversubscribe enabled)
6. **MM-GBSA.in** - MM-GBSA input configuration file

Note: The `{mutation}` placeholder is replaced with the parent directory name (e.g., "Q94R", "WT", "A123B").

### Features

- **Recursive search**: Finds all 'analysis' directories from the current location
- **Automatic creation**: Creates 'gbsa' subdirectories as needed
- **Dynamic naming**: Uses parent directory name as mutation identifier in filenames and file content
- **Overwrite capability**: Overwrites existing files if 'gbsa' directory already exists
- **Logging**: Provides detailed output about created directories and files
- **Standard library only**: Uses only Python standard libraries (no external dependencies)
- **SLURM optimization**: Configured with 4 CPUs, 16GB RAM, and oversubscribe support

### Example Output

```
Starting GBSA file generation script...
Searching for 'analysis' directories from: /home/user/project
--------------------------------------------------------------------------------
Found 2 'analysis' directories:
  - /home/user/project/Q94R/analysis (mutation: Q94R)
  - /home/user/project/WT/analysis (mutation: WT)
--------------------------------------------------------------------------------

Processing: /home/user/project/Q94R/analysis (mutation: Q94R)
Created GBSA directory: /home/user/project/Q94R/analysis/gbsa
  Generated file: /home/user/project/Q94R/analysis/gbsa/pt-strip-Q94R.in
  Generated file: /home/user/project/Q94R/analysis/gbsa/pt-parmstrip_rec.in
  Generated file: /home/user/project/Q94R/analysis/gbsa/pt-parmstrip_lig.in
  Generated file: /home/user/project/Q94R/analysis/gbsa/pt-parmstrip_com.in
  Generated file: /home/user/project/Q94R/analysis/gbsa/MM-GBSA.sh
  Generated file: /home/user/project/Q94R/analysis/gbsa/MM-GBSA.in

Processing: /home/user/project/WT/analysis (mutation: WT)
Created GBSA directory: /home/user/project/WT/analysis/gbsa
  Generated file: /home/user/project/WT/analysis/gbsa/pt-strip-WT.in
  ...
--------------------------------------------------------------------------------
GBSA file generation completed successfully!
```

### Requirements

- Python 3.6 or higher
- No external dependencies required

## strip_trajectories.py

A Python script that performs trajectory stripping for molecular dynamics analysis using cpptraj.

### Purpose

This script searches for mutation directories containing MMGBSA files (specifically looking for `analysis/gbsa/` directories), locates the required topology (prmtop) and trajectory (NetCDF) files, and generates cpptraj input files along with SLURM batch scripts to strip specific frames (825-850) from the trajectories. The script also reports the total number of frames in each trajectory after the stripping process is complete.

### Usage

```bash
cd /path/to/your/project
python3 strip_trajectories.py
```

Or make it executable and run directly:

```bash
chmod +x strip_trajectories.py
./strip_trajectories.py
```

### Features

- **Automatic discovery**: Finds all mutation directories with MMGBSA structure (`analysis/gbsa/`)
- **File detection**: Automatically locates prmtop and NetCDF trajectory files
- **Frame extraction**: Strips frames 825-850 (inclusive) from trajectories
- **SLURM integration**: Generates and submits SLURM batch scripts for processing
- **Frame counting**: Reports total number of frames in each trajectory
- **Logging**: Provides detailed output about file creation and job submissions
- **Standard library only**: Uses only Python standard libraries (no external dependencies)
- **Error handling**: Gracefully handles missing files and failed submissions

### Generated Files

For each mutation, the script creates:

1. **strip_traj_{mutation}.in** - cpptraj input file for trajectory stripping
2. **strip_traj_{mutation}.sh** - SLURM batch script for job submission
3. **AF-{mutation}_solv_gbsa_750.nc** - Output stripped NetCDF file (created by cpptraj)
4. **strip_{mutation}.log** - cpptraj execution log
5. **strip_{mutation}.out** - SLURM stdout output
6. **strip_{mutation}.err** - SLURM stderr output

### Example Output

```
================================================================================
Trajectory Stripping Script
================================================================================
Searching for mutation directories from: /home/user/project
Frame range to extract: 825-850 (inclusive)
--------------------------------------------------------------------------------
Found 2 mutation directories:
  - /home/user/project/Q94R/analysis/gbsa (mutation: Q94R)
  - /home/user/project/WT/analysis/gbsa (mutation: WT)
--------------------------------------------------------------------------------

Processing mutation: Q94R
  GBSA directory: /home/user/project/Q94R/analysis/gbsa
  Found topology file: strip.1xjv_POT1_ssDNA-Q94R_wat.prmtop
  Found trajectory file: 1xjv_POT1_ssDNA-Q94R_wat_imaged_26-1025.nc
  Trajectory contains 1000 frames
  Created cpptraj input file: /home/user/project/Q94R/analysis/gbsa/strip_traj_Q94R.in
  Created SLURM batch script: /home/user/project/Q94R/analysis/gbsa/strip_traj_Q94R.sh
  Submitted SLURM job: 12345
  ✓ Successfully set up stripping for Q94R

Processing mutation: WT
  GBSA directory: /home/user/project/WT/analysis/gbsa
  Found topology file: strip.1xjv_POT1_ssDNA-WT_wat.prmtop
  Found trajectory file: 1xjv_POT1_ssDNA-WT_wat_imaged_26-1025.nc
  Trajectory contains 1000 frames
  Created cpptraj input file: /home/user/project/WT/analysis/gbsa/strip_traj_WT.in
  Created SLURM batch script: /home/user/project/WT/analysis/gbsa/strip_traj_WT.sh
  Submitted SLURM job: 12346
  ✓ Successfully set up stripping for WT

================================================================================
SUMMARY
================================================================================

✓ Successfully submitted 2 job(s):
  - Q94R: Job ID 12345
  - WT: Job ID 12346

--------------------------------------------------------------------------------
TRAJECTORY FRAME COUNTS
--------------------------------------------------------------------------------
  Q94R: 1000 total frames in trajectory
  WT: 1000 total frames in trajectory

================================================================================
Trajectory stripping script completed!
================================================================================
```

### Requirements

- Python 3.6 or higher
- cpptraj (from AmberTools) must be available for frame counting
- SLURM workload manager for job submission
- No external Python dependencies required
