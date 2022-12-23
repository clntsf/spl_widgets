import setuptools

# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

setuptools.setup(
    name="spl_widgets",
    version="0.8.1",
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
    python_requires=">=3.8",
    entry_points='''
        [console_scripts]
        lighttheme=spl_widgets:lighttheme_force
        rm_aliases=spl_widgets.clear_aliases:main
        gorilla_clean=spl_widgets.gorilla_clean:main
        tuner=spl_widgets.tuner:main
        stk_swx=spl_widgets.stk_swx:main
        batch_tune=spl_widgets.batch_tune:main
        jukemake=spl_widgets.jukemake:main
    '''
)
