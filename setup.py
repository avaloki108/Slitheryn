from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="slither-analyzer",
    description="Slither is a Solidity and Vyper static analysis framework written in Python 3.",
    url="https://github.com/crytic/slither",
    author="Trail of Bits",
    version="0.11.3",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "packaging",
        "prettytable>=3.10.2",
        "pycryptodome>=3.4.6",
        "crytic-compile>=0.3.9,<0.4.0",
        # "crytic-compile@git+https://github.com/crytic/crytic-compile.git@master#egg=crytic-compile",
        "web3>=7.10,<8",
        "eth-abi>=5.0.1",
        "eth-typing>=5.0.0",
        "eth-utils>=5.0.0",
    ],
    extras_require={
        "lint": [
            "black==22.3.0",
            "pylint==3.0.3",
        ],
        "test": [
            "pytest",
            "pytest-cov",
            "pytest-xdist",
            "deepdiff",
            "orderly-set==5.3.2",  # Temporary fix for https://github.com/seperman/deepdiff/issues/539
            "numpy",
            "coverage[toml]",
            "filelock",
            "pytest-insta",
        ],
        "doc": [
            "pdoc",
        ],
        "dev": [
            "slither-analyzer[lint,test,doc]",
            "openai",
        ],
    },
    license="AGPL-3.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "slitheryn = slither.__main__:main",
            "slitheryn-check-upgradeability = slither.tools.upgradeability.__main__:main",
            "slitheryn-find-paths = slither.tools.possible_paths.__main__:main",
            "slitheryn-simil = slither.tools.similarity.__main__:main",
            "slitheryn-flat = slither.tools.flattening.__main__:main",
            "slitheryn-format = slither.tools.slither_format.__main__:main",
            "slitheryn-check-erc = slither.tools.erc_conformance.__main__:main",
            "slitheryn-check-kspec = slither.tools.kspec_coverage.__main__:main",
            "slitheryn-prop = slither.tools.properties.__main__:main",
            "slitheryn-mutate = slither.tools.mutator.__main__:main",
            "slitheryn-read-storage = slither.tools.read_storage.__main__:main",
            "slitheryn-doctor = slither.tools.doctor.__main__:main",
            "slitheryn-documentation = slither.tools.documentation.__main__:main",
            "slitheryn-interface = slither.tools.interface.__main__:main",
        ]
    },
)
