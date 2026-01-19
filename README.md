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
