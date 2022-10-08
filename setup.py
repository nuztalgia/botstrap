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
        "cryptography >=38.0.0",
    ],
    extras_require={
        "tests": [
            "pytest >=7.1.0",
            "pytest-cov >=4.0.0",
            "pytest-repeat >=0.9.0",
        ],
    },
)
