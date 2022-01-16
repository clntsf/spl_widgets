import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spl_widgets",
    version="0.2.6",
    author="Colin Simon-Fellowes",
    author_email="colin.tsf@gmail.com",
    description="Widgets for the Barnard Speech Perception Laboratory",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/spl_widgets",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/spl_widgets/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=['pandas'],
    python_requires=">=3.6",
)
