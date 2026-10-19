import setuptools

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="anchorpoint",
    version="0.9.0",
    author="Matt Carey",
    author_email="matt@authorityspoke.com",
    description="Text substring selectors for anchoring annotations",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    packages=setuptools.find_packages(exclude=["tests"]),
    python_requires=">=3.13",
)
