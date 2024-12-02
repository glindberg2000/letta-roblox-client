from setuptools import setup, find_packages

setup(
    name="letta_roblox",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0"
    ],
    python_requires=">=3.8",
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
) 