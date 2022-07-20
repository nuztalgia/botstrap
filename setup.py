from setuptools import setup

setup(
    url="https://github.com/nuztalgia/botstrap",
    project_urls={
        "Issue Tracker": "https://github.com/nuztalgia/botstrap/issues",
        "Source Code": "https://github.com/nuztalgia/botstrap",
    },
    install_requires=[
        "colorama >=0.4.5",
        "cryptography >=37.0.0",
    ],
    extras_require={
        "dev": [
            "pre-commit >=2.20.0",
            "setuptools >=61.0.0",
        ],
    },
)
