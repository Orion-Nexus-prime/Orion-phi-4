"""
Setup script for Orion Phi-4 Multi-Agent AI Trading System
"""
from setuptools import setup, find_packages

setup(
    name="orion-phi-4",
    version="1.0.0",
    packages=find_packages(where="."),
    package_dir={"": "."},
    python_requires=">=3.9",
)
