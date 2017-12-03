from setuptools import setup, find_packages

requires = [
    'flask',
    'iso8601',
    'openprocurement_client',
    'pytz',
    'requests',
    'setuptools',
    'simplejson',
]
entry_points = {
    'console_scripts': [
    ]
}

setup(
    name='openprocurement.playground',
    version='0.2b1',
    description="Web console for openprocurement.api",
    long_description=open("README.md").read(),
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
    ],
    platforms=['posix'],
    keywords='openprocurement',
    author='Volodymyr Flonts',
    author_email='flyonts@gmail.com',
    url='https://github.com/openprocurement/openprocurement.playground',
    license='Apache License 2.0',
    packages=find_packages(),
    namespace_packages=['openprocurement'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    entry_points=entry_points
)
