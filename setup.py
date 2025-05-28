from setuptools import setup, find_packages

setup(
    name="stm_converter",
    version="0.1.0",
    author="himaj joshi",
    author_email="himajjoshi932@gmail.com",
    description="A Python package for converting c/c++ structs to ros messages",
    url="",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # add jinja
        "setuptools",
    ],
    package_data={
        "stm_converter": [
            "resources/jinja_templates/*.txt",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "stm_converter = stm_converter.main:main",
        ],
    },
)
