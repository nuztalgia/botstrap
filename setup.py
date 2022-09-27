from setuptools import setup

setup(
    url="https://botstrap.readthedocs.io",
    project_urls={
        "Documentation": "https://botstrap.readthedocs.io/en/latest/api/",
        "Issue Tracker": "https://github.com/nuztalgia/botstrap/issues",
        "Source Code": "https://github.com/nuztalgia/botstrap",
    },
    install_requires=[
        "colorama >=0.4.5",
        "cryptography >=37.0.0",
    ],
    extras_require={
        "tests": [
            "pytest >=7.1.0",
            "tox >= 3.26.0",
        ],
    },
)
