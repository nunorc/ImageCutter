from setuptools import setup

setup(name='ImageCutter',
      version='0.1',
      description='FITS cut-out service in Python',
      url='https://github.com/jhoar/ImageCutter',
      author='John Hoar',
      author_email='johnhoar@yahoo.co.uk',
      license='BSD',
      packages=['ImageCutter'],
      install_requires=[
	'astropy==2.0.2',
	'numpy==1.13.3',
	'fitsio==0.9.11',
	'typing==3.6.2'
      ],
      zip_safe=False)
