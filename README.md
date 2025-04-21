# TOMOMAN Processing Pipeline
This repository contains the core script tomoman_run.py, designed for cryo-electron tomography (cryo-ET) tilt-series preprocessing using IMOD and MotionCor3.

# Overview
tomoman_run.py provides a semi-automated preprocessing pipeline that handles:

Motion correction

Tilt-series alignment

CTF estimation

Tomogram reconstruction

This script is tailored for use with the TOMOMAN framework and streamlines cryo-ET data preprocessing for downstream analysis.

# Requirements
Software dependencies (must be available in your terminal environment):
IMOD

MotionCor3

Ensure both are correctly installed and callable from your command line before running the script.

# Python
Python 3.7+

Recommended packages:

numpy

subprocess

argparse
