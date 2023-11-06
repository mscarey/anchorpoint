import setuptools

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="anchorpoint",
    version="0.8.2",
    author="Matt Carey",
    author_email="matt@authorityspoke.com",
    description="Text substring selectors for anchoring annotations",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/mscarey/anchorpoint",
    project_urls={
        "Bug Tracker": "https://github.com/mscarey/anchorpoint/issues",
        "Documentation": "https://anchorpoint.readthedocs.io/en/latest/",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: Free To Use But Restricted",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    packages=setuptools.find_packages(exclude=["tests"]),
    install_requires=["pydantic>=2.4.2", "python-ranges>=1.2.2"],
    python_requires=">=3.8",
)
