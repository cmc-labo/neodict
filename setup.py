from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="neodict",
    version="0.1.0",
    author="NeoDict Contributors",
    author_email="neodict@example.com",
    description="自動更新型日本語新語辞書ライブラリ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cmc-labo/neodict",
    project_urls={
        "Bug Reports": "https://github.com/cmc-labo/neodict/issues",
        "Source": "https://github.com/cmc-labo/neodict",
        "Documentation": "https://github.com/cmc-labo/neodict#readme",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Natural Language :: Japanese",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "neodict=cli.commands:main",
        ],
    },
    package_data={
        "neodict": ["data/*.yaml", "data/*.json"],
    },
    include_package_data=True,
)
