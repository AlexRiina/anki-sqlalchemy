import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="anki-sqlalchemy",
    version="0.1.5",
    author="Alex Riina",
    author_email="alex.riina@gmail.com",
    description="Clean python interface for interacting with Anki's database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AlexRiina/anki-sqlalchemy",
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
