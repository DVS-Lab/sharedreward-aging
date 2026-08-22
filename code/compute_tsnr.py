#!/usr/bin/env python3
"""Execute the explicitly configured authoritative RF1 tSNR implementation."""
import os,runpy
from pathlib import Path
root=Path(os.environ.get('RF1_SHAREDREWARD_ROOT','/ZPOOL/data/projects/rf1-sra-sharedreward'))
tool=root/'code/compute_tsnr.py'
if not tool.is_file():raise SystemExit(f'ERROR: authoritative utility not found: {tool}')
runpy.run_path(str(tool),run_name='__main__')
