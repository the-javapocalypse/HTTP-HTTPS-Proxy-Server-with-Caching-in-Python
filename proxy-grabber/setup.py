from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
      long_description = f.read()

setup(
      name='proxy-grabber',
      version='1.1.1',
      description='Simple http proxy grabber and checker',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/Ferluci/Proxy-Grabber',
      author='Anischenko Konstantin',
      author_email='anishenko00@gmail.com',
      classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Topic :: Software Development',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
      ],
      keywords='proxy grabber http proxy-grabber scrapper web',
      py_modules=["proxy_grabber"],
      install_requires=['requests>=2.20.0', 'beautifulsoup4>=4.6.0'],
)
