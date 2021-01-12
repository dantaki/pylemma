from setuptools import setup
setup(
	name='analemma',
	version='0.0.1',
	url='https://github.com/dantaki/analemma',
	author='Danny Antaki',
	author_email='dantaki@ucsd.edu',
	packages=['analemma'],
	package_dir={'analemma': 'analemma/'},
	include_package_data=True,
	scripts= ['analemma/analemma']
)