# setup.py
from setuptools import setup, find_packages
import os

# Function to read the requirements.txt file
def read_requirements():
    with open(os.path.join('clients', 'python', 'requirements.txt')) as req:
        return req.read().splitlines()

setup(
    name='kindo-message-client',
    version='0.1.0',  # Start with an initial version
    author='kingsleywang1984', # Or your name/organization
    description='A Python client to send messages to an SQS queue.',
    packages=find_packages(where='clients/python'), # Tells setuptools to look for packages in this sub-directory
    package_dir={'': 'clients/python'}, # Specifies that the root package directory is 'clients/python'

    # This tells pip what other packages your module depends on.
    # It will automatically install them.
    install_requires=read_requirements(),

    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)