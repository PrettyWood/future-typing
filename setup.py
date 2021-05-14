import distutils
import os.path

from setuptools import setup
from setuptools.command.install import install as _install

PTH = """\
try:
    import future_typing
except ImportError:
    pass
else:
    future_typing.register()
"""

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(THIS_DIR, "README.md")) as f:
    long_description = f.read()


class install(_install):
    def initialize_options(self):
        _install.initialize_options(self)
        # Use this prefix to get loaded as early as possible
        name = "aaaaaaa_" + self.distribution.metadata.name

        contents = "import sys; exec({!r})\n".format(PTH)
        self.extra_path = (name, contents)

    def finalize_options(self):
        _install.finalize_options(self)

        install_suffix = os.path.relpath(
            self.install_lib, self.install_libbase,
        )
        if install_suffix == ".":
            distutils.log.info("skipping install of .pth during easy-install")
        elif install_suffix == self.extra_path[1]:
            self.install_lib = self.install_libbase
            distutils.log.info(
                "will install .pth to '%s.pth'",
                os.path.join(self.install_lib, self.extra_path[0]),
            )
        else:
            raise AssertionError(
                "unexpected install_suffix",
                self.install_lib, self.install_libbase, install_suffix,
            )


setup(
    name="future_typing",
    version="0.4.1",
    description="Use generic type hints and new union syntax `|` with python 3.6+",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Typing :: Typed",
    ],
    author="Eric Jolibois",
    author_email="em.jolibois@gmail.com",
    url="https://github.com/PrettyWood/future-typing",
    license="MIT",
    cmdclass={"install": install},
    entry_points={
        "console_scripts": ['future_typing=future_typing.cli:cli'],
    },
    packages=["future_typing"],
    package_data={"future_typing": ["py.typed"]},
    python_requires=">=3.6",
    extras_require={
        "test": [
            "black == 21.5b1",
            "flake8 == 3.9.2",
            "isort == 5.8.0",
            "mypy == 0.812",
            "pytest == 6.2.4",
            "pytest-cov == 2.11.1",
            "typing_extensions == 3.10.0.0",
        ],
        "dev": [
            "pre-commit == 2.12.1"
        ],
    },
    zip_safe=True,
)
