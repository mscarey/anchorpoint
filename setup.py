import setuptools
import anchorpoint

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="anchorpoint",
    version=anchorpoint.__version__,
    author="Matt Carey",
    author_email="matt@authorityspoke.com",
    description="Text substring selectors for anchoring annotations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mscarey/anchorpoint",
    packages=setuptools.find_packages(exclude=("tests",)),
    install_requires=["marshmallow"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Free To Use But Restricted",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
    python_requires=">=3.8",
    include_package_data=True,
)
