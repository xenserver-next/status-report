# Local Python Development setup on Ubuntu 20.04 / 22.04

For running the Unit tests and static analysis tools, use a relatively modern
Linux VM. Possible are Fedora37+, but the documentation here focuses on
Ubuntu20.04 and 22.04 as they are the defaults of WSL and hosts:

```bash
sudo apt update;sudo apt install software-properties-common python{2,3}
```

Ubuntu no longer packages `python2-pip`, so you have to install `pip2`
[this way](https://askubuntu.com/questions/1317353/how-can-i-find-an-older-version-of-pip-that-works-with-python-2-7):

```yml
curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py
python2 get-pip.py
rm ~/.local/bin/pip # To avoid it overriding your /usr/bin/pip for Python3
# Variant 1: Append to the PATH, safer as /usr/bin/pip is found first,
echo 'PATH="$PATH:~/.local/bin/pip"' >>~/.bash_aliases # but recommended is:
# Variant 2: Prepend to the PATH, so any updates you install that precedence:
echo 'PATH="~/.local/bin/pip:$PATH"' >>~/.bash_aliases
. ~/.bash_aliases
```

You can install specific Python versions using this PPA:

```bash
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get install -y python3.{8,11}{,-distutils}
```

Please refer to this document for additional options:\
https://github.com/xenserver/python-libs/blob/master/CONTRIBUTING.md

## Installing Packages to Run the Xen-Bugtool Test Environment

Install the libraries required by `xen-bugtool` with the following command:

```sh
# Install the libraries required to run `xen-bugtool` itself into your environment:
python2 -m pip install --user -r requirements.txt
```

The test framework itself can use Python2 or Python3.
Depending on the installed builds, you can install one or both:

```sh
# Install pytest and its depdendencies into your environment:
python2 -m pip install --user -r requirements-dev.txt # and/or:
python3 -m pip install --user -r requirements-dev.txt
```

## Additional analysis tools

You may want to install the static analysis tools in your user environment,
so you can run them manually too:

```bash
pip3 install mypy pylint pyright pytype
```
