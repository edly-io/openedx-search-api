from setuptools import setup


def load_requirements(*requirements_paths):
    """
    Load all requirements from the specified requirements files.
    Returns:
        list: Requirements file relative path strings
    """
    requirements = set()
    for path in requirements_paths:
        requirements.update(
            line.split('#')[0].strip()
            for line in open(path, encoding='utf-8').readlines()  # pylint: disable=consider-using-with
            if is_requirement(line.strip())
        )
    return list(requirements)


def is_requirement(line):
    """
    Return True if the requirement line is a package requirement.
    Returns:
        bool: True if the line is not blank, a comment, a URL, or an included file
    """
    return line and not line.startswith(('-r', '#', '-e', 'git+', '-c'))


setup(
    name='openedx-search',
    version='0.0.0',
    packages=[
        'openedx_search_api',
        'openedx_search_api.drivers',
        'openedx_search_api.migrations',
    ],
    install_requires=load_requirements('requirements/base.in'),
    url='https://github.com/qasimgulzar/django-search',
    license='',
    author='qasimgulzar',
    author_email='qasim.khokhar52@gmail.com',
    description=''
)
