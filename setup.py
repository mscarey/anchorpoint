import setuptools

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="anchorpoint",
    version="0.6.1",
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
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    packages=setuptools.find_packages(exclude=["tests"]),
    install_requires=["pydantic>=1.8.2"],
    python_requires=">=3.8",
)
