from setuptools import setup
import os
from glob import glob

package_name = 'hex_gz'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Dodaj config
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        # Dodaj launch files
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        # Dodaj worlds
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.sdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@example.com',
    description='Hexapod Gazebo simulation package',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'initial_positions_publisher = hex_gz.initial_positions_publisher:main',
        ],
    },
)