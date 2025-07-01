# setup.py (Final Version)
from setuptools import setup, find_packages
import os


# This function might need adjustment if requirements.txt is moved
# Assuming it's still in the original location for now.
def read_requirements():
    with open(os.path.join('clients', 'python', 'requirements.txt')) as req:
        return req.read().splitlines()


setup(
    name='kindo-message-client',
    version='0.3.0',  # Bump version for this major structural change
    author='kingsleywang1984',
    description='A Python client to send messages to an SQS queue.',

    # This will now correctly discover the 'kindo_message_client' package
    packages=find_packages(where='clients/python'),

    # The package root is still the 'clients/python' directory
    package_dir={'': 'clients/python'},

    # This tells setup to include files specified in MANIFEST.in
    include_package_data=True,

    install_requires=read_requirements(),

    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)