from setuptools import setup, Extension
import os

def getfiles(root):
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            yield os.path.relpath(os.path.join(dirpath, filename))

setup(
    name = "vatic_checker",
    author = "Jonathan Keane",
    author_email = "jkeane@gmail.com",
    description = "",
    license = "MIT",
    version = "0.2.5",
    classifiers = ['Development Status :: 1 - Planning',
                   'Intended Audience :: Developers'],
    scripts = ['scripts/checker'],
    packages = ["vatic_checker"],
    package_dir = {"": "src"},
    package_data={"": ["public/jquery-ui-1.12.1/*.js",
                       "public/jquery-ui-1.12.1/*.css",
                       "public/jquery-ui-1.12.1/external/jquery/*.js",
                       "public/jquery-ui-1.12.1/images/*.png",
                       "public/*.js",
                       "public/*.css",
                       "public/*.html"]},
    include_package_data=True,
    namespace_packages=["vatic_checker"],
    install_requires = ["setuptools", "SQLAlchemy", "wsgilog", "multiprocessing", "Pillow", "MySQL-python"],
    tests_require = ["pytest", "mock", "aclhemy-mock"]
)
