"""
Setup script for the Rankyx  FastAPI Boilerplate 
"""
import re
from pathlib import Path
from setuptools import setup, find_packages

# Get version from source
def get_version():
    content = (Path(__file__).parent / "main.py").read_text()
    version_match = re.search(r"version=\"([^\"]+)\"", content)
    if version_match:
        return version_match.group(1)
    return "0.1.0"  # Default version

# Read requirements
def get_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()

setup(
    name="rankyx-ai-engine",
    version=get_version(),
    description="A production-ready FastAPI application for AI processing",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/your-org/rankyx-ai-engine",
    packages=find_packages(),
    include_package_data=True,
    install_requires=get_requirements(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: FastAPI",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.10",
)
