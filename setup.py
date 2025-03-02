from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f.readlines() if not line.startswith("#")]

setup(
    name="mobius",
    version="2.0.0",
    author="Geoff Cunningham",
    author_email="geoff.cunningham@organicdrive.co.uk",
    description="A Python-based system for monitoring and controlling a vivarium for a python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GeoffC31415/Mobius_Automation",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.5",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest==7.3.1",
            "pytest-cov==4.1.0",
            "black==23.3.0",
            "isort==5.12.0",
            "mypy==1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mobius=mobius.main:main",
        ],
    },
)