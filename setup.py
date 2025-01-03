import sys
from setuptools import setup, find_packages

if sys.version_info[0] < 3.10:
  print("ERROR: User is running a version of Python older than Python 3.10\nTo use FireWxPy, the user must be using Python 3.10 or newer.")

setup(
    use_scm_version=True
    name = "firewxpy",
    version = "1.2.1",
    packages = find_packages(),
    install_requires=[
        "matplotlib>=3.7",
        "protobuf>=3.20.3",
        "metpy>=1.5.1",
        "netcdf4>=1.7.1",
        "numpy>=1.24",
        "pandas>=2.2",
        "siphon>=0.10.0",
        "xarray>=2023.1.0",
        "pysolar>=0.11",
        "pygrib>=2.1.4",
        "cfgrib>=0.9.10.4",
        "cartopy>=0.21.0",
         "imageio>=2.34.0",
    ],
    author="Eric J. Drewitz",
    description="Provides automated weather graphics with a focus on fire weather.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown"

)
