import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="anki-sqlalchemy",
    version="0.0.1",
    author="Alex Riina",
    author_email="alex.riina@gmail.com",
    description="Utility package for interacting with the Anki database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['anki_sqlalchemy'],
    package_data={
        "": ["py.typed"],
    },
    install_requires=['sqlalchemy'],
    test_requires=['black', 'isort', 'flake8', 'mypy', 'sqlalchemy-stubs'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
