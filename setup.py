from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rascalrunner",
    version="0.2.0",
    author="nopcorn",
    author_email="",
    description="A red team tool to leverage Github workflows and self-hosted runners",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nopcorn/rascalrunner",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "GitPython==3.1.43",
        "PyGithub==2.4.0",
        "PyYAML==6.0.2",
        "Requests==2.32.4",
        "rich==13.9.4"
    ],
    entry_points={
        "console_scripts": [
            "rascalrunner=rascalrunner.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.7",
)