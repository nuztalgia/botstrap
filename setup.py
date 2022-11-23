from setuptools import setup

setup(
    url="https://github.com/nuztalgia/botstrap",
    project_urls={
        "Documentation": "https://botstrap.readthedocs.io",
        "Issue Tracker": "https://github.com/nuztalgia/botstrap/issues",
        "Source Code": "https://github.com/nuztalgia/botstrap/tree/main/botstrap",
    },
    install_requires=[
        "colorama >=0.4.6",
        "cryptography >=38.0.3",
    ],
    extras_require={
        "tests": [
            "pytest >=7.2.0",
            "pytest-cov >=4.0.0",
            "pytest-repeat >=0.9.1",
        ],
    },
)
