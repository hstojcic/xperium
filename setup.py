from setuptools import setup, find_packages

setup(
    name="xperium",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.24.0",
        "python-docx>=0.8.11",
        "numpy>=1.22.0",
        "pandas>=1.5.0",
        "matplotlib>=3.5.0",
        "openpyxl>=3.0.0",
        "pillow>=9.0.0",
        "plotly>=5.10.0",
        "scipy>=1.8.0",
    ],
    python_requires=">=3.9",
)
