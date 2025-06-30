#!/usr/bin/env python3
"""
Setup script for TrackMate SPT Analyzer GUI
==========================================

Installation script for the TrackMate SPT Analyzer GUI application.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="trackmate-spt-analyzer",
    version="1.0.0",
    author="Saskia Sanders, Bosse Lab, Medizinische Hochschule Hannover",
    author_email="",  # Add email if available
    description="A GUI application for analyzing TrackMate XML files for Single Particle Tracking (SPT) analysis",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="",  # Add repository URL if available
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Image Processing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "trackmate-spt-analyzer=trackmate_spt_analyzer.gui.app:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="trackmate, single particle tracking, SPT, microscopy, analysis, GUI",
    project_urls={
        "Bug Reports": "",  # Add issue tracker URL if available
        "Source": "",       # Add source code URL if available
    },
) 