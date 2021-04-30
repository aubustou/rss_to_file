from setuptools import setup

setup(
    name='rss_to_file',
    version='1.0',
    packages=[''],
    url='',
    license='MIT',
    author='Aubustou',
    author_email='survivalfr@yahoo.fr',
    description='Download files from a RSS flow',
    install_requires=[
        "selenium==3.141.0",
        "undetected-chromedriver",
        "beautifulsoup4==4.9.3",
    ]
)
