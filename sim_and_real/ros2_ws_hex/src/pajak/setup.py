from setuptools import find_packages, setup

package_name = 'pajak'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='milosz',
    maintainer_email='milosz.kaszubowski@onet.pl',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'my_node = pajak.my_node:main',
            'pajak_trajectory = pajak.pajak_trajectory:main',
            'test = pajak.test:main',
            'esp32_serial_commander = pajak.esp32_serial_commander:main',
            'walk_v1 = pajak.walk_v1:main',
            'wifi_conect = pajak.wifi_conect:main',
        ],
    },
)
