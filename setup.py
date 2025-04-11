from setuptools import setup, find_packages

setup(
    name="openaidy",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn==0.24.0",
        "python-dotenv==1.1.0",
        "pydantic",
        "openai",
        "google-generativeai",
        "mcp[cli]>=1.6.0",
    ],
)