from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='huplo',
    version='0.1',
    description='Overlay text on a gstreamer video via dbus and cairo/pango.',
    long_description = readme(),
	classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Multimedia :: Video :: Display',
      ],
    keywords = 'gstreamer video text overlay python telemetry hud cairo dbus pycairo pango',
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
    scripts=[
	'bin/huplo-animated-irc-client',
	'bin/huplo-set-list',
	'bin/huplo-set-ticker',
	'bin/huplo-irc-client',
	'bin/huplo-set-text',
	'bin/huplo-view-stream',
	],
      zip_safe=False)
