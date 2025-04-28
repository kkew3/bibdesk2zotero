from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='bibdesk2zotero',
    version='0.1.0',
    author='Kaiwen Wu',
    url='https://github.com/kkew3/bibdesk2zotero',
    description='Migration script from BibDesk to Zotero 7',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.9',
    install_requires = [
        'bibtexparser<2,>=1.4',
        'click<9,>=8.1',
        'loguru>=0.7',
    ],
    extras_require={
        'dev': [
            'pytest>=8.3',
        ],
    },
    package_dir={'': 'src'},
    packages=find_packages('src'),
    entry_points = {
        'console_scripts': [
            'bibdesk2zotero = bibdesk2zotero.bibdesk2zotero:main',
        ],
    },
)
