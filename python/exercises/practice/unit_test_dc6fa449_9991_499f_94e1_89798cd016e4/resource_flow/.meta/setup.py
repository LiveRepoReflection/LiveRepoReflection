from setuptools import setup, find_packages

setup(
    name='resource_flow',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'networkx>=2.5',
    ],
    python_requires='>=3.6',
)