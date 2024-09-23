#!/usr/bin/env python

import os
from pathlib import Path
from setuptools import setup

if __name__ == "__main__":
    setup(install_requires=["openai>=1.46.1"])

    libDir = os.path.dirname(os.path.realpath(__file__))
    homeDir = Path.home()

    for prfl in ["bashrc","bash_profile","zshrc","bash_aliases"]:
        if os.path.isfile(f"{homeDir}/.{prfl}"):
            aliasStr = f"alias assistant='python {libDir}/assistant.py'"
            os.system(aliasStr)
            with open(f"{homeDir}/.{prfl}", "a") as current:
                current.write(f"\n# ChatGPT CLI assistant shortcut alias\n{aliasStr}")

