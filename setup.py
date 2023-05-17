import os
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
]

setup(
    name='laozy',
    version=version,
    packages=find_packages(),
    package_data={
        'laozy': [],
        'migrations': ['**/*'],
    },
    #include_package_data=True,
    scripts=['setup.py', './bin/laozy', 'alembic.ini', 'requirements.txt'],
    install_requires = install_requires
)