import setuptools

# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

setuptools.setup(
    name="spl_widgets",
    version="0.4.3",
    author="Colin Simon-Fellowes",
    author_email="colin.tsf@gmail.com",
    description="Widgets for the Barnard Speech Perception Laboratory",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    url="https://github.com/ctsf1/spl_widgets",
    project_urls={
        "Changelog":"https://github.com/ctsf1/spl_widgets#changelog"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=['pandas'],
    python_requires=">=3.6",
    entry_points='''
        [console_scripts]
        lighttheme=spl_widgets:lighttheme_force
        gorilla_clean=spl_widgets.gorilla_clean:main
        tuner=spl_widgets.tuner:main
        stk_swx=spl_widgets.stk_swx:main
        widgets_help=spl_widgets.widgets_help:main
        rm_aliases=spl_widgets.clear_aliases:main
    '''
)
