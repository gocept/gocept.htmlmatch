from setuptools import setup, find_packages
import os.path


setup(
    name='gocept.htmlmatch',
    version='0.1dev',
    author='gocept gmbh & co. kg',
    author_email='mail@gocept.com',
    url='https://bitbucket.org/gocept/gocept.htmlmatch',
    description='testbrowser output matcher',
    long_description=open(os.path.join(
            'src', 'gocept', 'htmlmatch', 'README.txt')).read(),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=['setuptools'],
    zip_safe=False,
    license='ZPL 2.1')
