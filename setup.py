from setuptools import setup, find_packages

setup(
    name="letta-roblox-client",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "letta>=0.5.5",
        "requests>=2.31.0"
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0"
        ]
    }
)
