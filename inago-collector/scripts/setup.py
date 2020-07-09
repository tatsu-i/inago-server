from setuptools import setup, find_packages
import os

setup(
    name="collector",
    version=0.1,
    python_requires="~=3.5",
    description="trader",
    packages=find_packages(exclude="tests"),
    install_requires=["aio-pika==4.9.3", "pika==1.1.0"],
    extras_require={"test": ["pytest"]},
    scripts=["run.py"],
    include_package_data=True,
    zip_safe=False,
)
