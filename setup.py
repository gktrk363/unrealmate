from pathlib import Path
from setuptools import setup, find_packages

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="unrealmate",
    version="1.1.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
        "rich-click>=1.6.0",
        "toml>=0.10.2",
        "flask>=2.3.0",
    ],
    entry_points={
        "console_scripts": [
            "unrealmate=unrealmate.cli:app",
        ],
    },
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
        ],
    },
    python_requires=">=3.10",
    description="All-in-one CLI toolkit for Unreal Engine developers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="gktrk363",
    url="https://github.com/gktrk363/unrealmate",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)