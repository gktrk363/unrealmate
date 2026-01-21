from setuptools import setup, find_packages

setup(
    name="unrealmate",
    version="0.1.5",
    packages=find_packages(),
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
        "toml>=0.10.2",
    ],
    entry_points={
        "console_scripts": [
            "unrealmate=unrealmate.cli:app",
        ],
    },
    python_requires=">=3.10",
    description="All-in-one CLI toolkit for Unreal Engine developers",
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