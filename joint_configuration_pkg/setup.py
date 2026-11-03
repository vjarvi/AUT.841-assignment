from glob import glob
import os
from setuptools import find_packages, setup

package_name = 'joint_configuration_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='joona',
    maintainer_email='joona.maki-korte@tuni.fi', 
    description='Joint configuration service for SCARA robot',
    license='TODO: License declaration',
    entry_points={
        'console_scripts': [
            'joint_configuration_server = joint_configuration_pkg.server:main',
        ],
    },
)
