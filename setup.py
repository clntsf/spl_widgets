import setuptools

# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

setuptools.setup(
    name="spl_widgets",
    version="1.7.2",
    author="Colin Simon-Fellowes",
    author_email="colin.tsf@gmail.com",
    description="Widgets for the Barnard Speech Perception Laboratory",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    url="https://github.com/clntsf/spl_widgets",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
    ],
    package_dir={"": "src"},
    packages=["spl_widgets", "spl_widgets.autoscorer", "spl_widgets.util"],
    install_requires=['pandas', 'tkinterdnd2-universal', 'openpyxl', 'lxml'],
    python_requires=">=3.8",
    entry_points='''
        [console_scripts]
        gorilla_clean=spl_widgets.gorilla_clean:main
        tuner=spl_widgets.tuner:main
        stk_swx=spl_widgets.stk_swx:main
        batch_tune=spl_widgets.batch_tune:main
        jukemake=spl_widgets.jukemake:main
        autoscorer=spl_widgets.autoscorer.autoscorer_gui:main
    ''',
    include_package_data=True,
    package_data={'': ['data/*']}
)
