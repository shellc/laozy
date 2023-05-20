import os, glob
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

version = '0.1'

install_requires = [
    'pathlib',
    'uvicorn',
    'starlette',
    'fastapi',
    'SQLAlchemy',
    'databases',
    'alembic',
    'langchain',
    'openai',
    'chromadb'
]

setup(
    name='laozy',
    version=version,
    packages=find_packages(),
    package_data={
        'laozy': [],
        'migrations': ['**/*'],
    },
    include_package_data=True,
    data_files=[('templates', glob.glob('./templates/**', recursive=True)), ('static', glob.glob('./static/**', recursive=True))],
    scripts=['setup.py', './bin/laozy', 'requirements.txt'],
    install_requires = install_requires
)