from distutils.core import setup

readme_content = open("README.md").read()

setup(  name = 'PyDAcq',
        version = '0.1.0',
        description = 'tools to run continous and threadsafe data acquisiton and display',
        author = 'Christoph Roedig',
        packages = [''],
        package_dir={'': 'src'},
        long_description=readme_content,
  )