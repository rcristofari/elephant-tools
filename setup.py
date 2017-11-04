from setuptools import setup

setup(name='eletools',
      version='0.1',
      description='A set of tools to manage the Myanmar Elephant database',
      url='https://github.com/rcristofari/elephant-tools/',
      author='Robin Cristofari',
      author_email='r.cristofari@gmail.com',
      license='UTU',
      packages=['eletools'],
      install_requires=[
          'scipy',
          'numpy',
          'pymysql'
          'ete3',
          'PILLOW'
      ],
      zip_safe=False)
