# Utility Scripts

This repository contains utility scripts for various tasks.

## generate_gbsa_files.py

A Python script that automatically generates GBSA (Generalized Born Surface Area) input files in analysis subdirectories.

### Purpose

This script searches for all directories that contain a subdirectory named 'analysis' starting from the current directory. For each directory that has an 'analysis' subdirectory, it creates a new subdirectory inside it named 'gbsa' (if it doesn't already exist) and populates it with the required input files.

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

1. **pt-strip-Q94R.in** - Trajectory stripping input file
2. **pt-parmstrip_rec.in** - Parameter stripping for receptor
3. **pt-parmstrip_lig.in** - Parameter stripping for ligand
4. **pt-parmstrip_com.in** - Parameter stripping for complex
5. **MM-GBSA.sh** - SLURM batch script for running MM-GBSA calculations
6. **MM-GBSA.in** - MM-GBSA input configuration file

### Features

- **Recursive search**: Finds all 'analysis' directories from the current location
- **Automatic creation**: Creates 'gbsa' subdirectories as needed
- **Overwrite capability**: Overwrites existing files if 'gbsa' directory already exists
- **Logging**: Provides detailed output about created directories and files
- **Standard library only**: Uses only Python standard libraries (no external dependencies)

### Example Output

```
Starting GBSA file generation script...
Searching for 'analysis' directories from: /home/user/project
--------------------------------------------------------------------------------
Found 2 'analysis' directories:
  - /home/user/project/simulation1/analysis
  - /home/user/project/simulation2/analysis
--------------------------------------------------------------------------------

Processing: /home/user/project/simulation1/analysis
Created GBSA directory: /home/user/project/simulation1/analysis/gbsa
  Generated file: /home/user/project/simulation1/analysis/gbsa/pt-strip-Q94R.in
  Generated file: /home/user/project/simulation1/analysis/gbsa/pt-parmstrip_rec.in
  Generated file: /home/user/project/simulation1/analysis/gbsa/pt-parmstrip_lig.in
  Generated file: /home/user/project/simulation1/analysis/gbsa/pt-parmstrip_com.in
  Generated file: /home/user/project/simulation1/analysis/gbsa/MM-GBSA.sh
  Generated file: /home/user/project/simulation1/analysis/gbsa/MM-GBSA.in

Processing: /home/user/project/simulation2/analysis
Created GBSA directory: /home/user/project/simulation2/analysis/gbsa
  Generated file: /home/user/project/simulation2/analysis/gbsa/pt-strip-Q94R.in
  ...
--------------------------------------------------------------------------------
GBSA file generation completed successfully!
```

### Requirements

- Python 3.6 or higher
- No external dependencies required
