from setuptools import setup, find_packages

setup(
    name='bob',
    version='2.0',
    packages=find_packages(),
    install_requires=[
        'psutil',
        'speedtest-cli',
        'pyserial',
    ],
    entry_points={
        'console_scripts': [
            'run-checker = bob.checker:run_checker',
            'run-updater = bob.updater:run_update',
            'run-main = bob.main_app:main_loop',
        ],
    },
)
