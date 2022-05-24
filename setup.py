from setuptools import setup, find_packages

setup(name='perform_metrics',
      version='0.1',
      description='Measures of Circuit Performance',
      url='',
      author='Anastasia Deckard & Tessa Johnson',
      author_email='anastasia.deckard@geomdata.com & tessa.johnson@geomdata.com',
      license='MIT',
      packages=find_packages('src'),
      package_dir={'':'src'},
      zip_safe=False)
