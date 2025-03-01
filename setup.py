from setuptools import setup, find_packages

setup(
    name="suno_downloader",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "aiohttp>=3.9.3",
        "aiofiles>=23.2.1",
        "beautifulsoup4>=4.12.3",
        "mutagen>=1.47.0",
        "playwright>=1.42.0",
        "tqdm>=4.66.2"
    ],
    extras_require={
        "test": [
            "pytest>=8.0.2",
            "pytest-asyncio>=0.23.5",
            "pytest-mock>=3.12.0"
        ]
    },
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to download songs from Suno.com",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/suno-downloader",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
