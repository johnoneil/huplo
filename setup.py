from setuptools import setup

setup(name='huplo',
    version='0.1',
    description='Heads Up Presentation Layer. Simple tools to overlay data onto gstreamer video streams.',
    url='https://github.com/johnoneil/huplo',
    author='John O\'Neil',
    author_email='oneil.john@gmail.com',
    license='MIT',
    packages=['huplo'],
    install_requires=[
        'setuptools',
        #'pygst',
        #'pygtk',
        'twisted',
        #'dbus',
        #'cairo',
        #'pango',
        #'pycairo',
        #'pangocairo',
        'simplejson',
        'jsonpickle',
        'argparse'
      ],
      zip_safe=False)
