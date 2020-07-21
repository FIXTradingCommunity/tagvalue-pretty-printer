import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="tagvalueprettyprinter-ninadmohale", # Replace with your own username
    version="1.0.0",
    author="Ninad Mohale",
    author_email="nrmohale@mtu.edu",
    description="Tag value pretty printer for FIX messages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FIXTradingCommunity/tagvalue-pretty-printer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
	'python_world@git+https://github.com/ceddlyburge/python_world#egg=python_world-0.0.1',
]
)
