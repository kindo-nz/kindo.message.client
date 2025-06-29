# setup.py
from setuptools import setup, find_packages
import os


# Function to read the requirements.txt file
def read_requirements():
    with open(os.path.join('clients', 'python', 'requirements.txt')) as req:
        return req.read().splitlines()


setup(
    name='kindo-message-client',
    version='0.1.1',  # Good practice to increment the version after a fix
    author='kingsleywang1984',
    description='A Python client to send messages to an SQS queue.',

    # --- THIS IS THE CRITICAL FIX ---
    # Use 'py_modules' to explicitly list standalone .py files to include.
    py_modules=['producer', 'signer', 'config'],

    # You can still use find_packages if you have actual packages (like 'tests')
    packages=find_packages(where='clients/python'),

    # This tells setuptools that the root for the modules and packages is 'clients/python'
    package_dir={'': 'clients/python'},

    install_requires=read_requirements(),

    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)