from setuptools import setup

setup(name='ImageCutter',
      version='0.1',
      description='FITS cut-out service in Python',
      url='https://github.com/jhoar/ImageCutter',
      author='John Hoar',
      author_email='johnhoar@yahoo.co.uk',
      license='BSD',
      packages=['ImageCutter'],
      install_requires=['fitsio'],
      zip_safe=False)
