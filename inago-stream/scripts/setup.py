from setuptools import setup, find_packages
import os

setup(
    name="stream",
    version=0.1,
    python_requires="~=3.5",
    description="trader",
    packages=find_packages(exclude="tests"),
    extras_require={"test": ["pytest"]},
    scripts=["run.py"],
    include_package_data=True,
    zip_safe=False,
)
