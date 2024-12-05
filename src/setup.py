from setuptools import setup, find_packages

setup(
    name="letta_roblox",
    version="0.2.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'letta-manage=letta_roblox.tools.manage_agents:main',
        ],
    },
    install_requires=[
        "requests>=2.31.0",
        "letta>=0.5.5"
    ],
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="A lightweight client for integrating Letta AI agents with Roblox NPCs",
    long_description=open("../README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/letta-roblox-client",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
) 