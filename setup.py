from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="jtrack",
    version="0.9",
    author="Rotem Reiss",
    author_email="reiss.r@gmail.com",
    description="Fast and effective integration to Jira.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rotemreiss/jTrack",
    packages=find_packages(exclude=['tests*']),
    install_requires=[
        "colorama",
        "atlassian_python_api",
        "win_unicode_console"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'jtrack=jtrack.main:interactive',
        ],
    },
)
