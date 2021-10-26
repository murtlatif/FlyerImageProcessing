# Getting Started

This document will allow you to setup and run the program on your local machine.

## Python Setup

This project uses python version `3.9.7`. The program is not guaranteed to work using another version of python.

## Setup your Virtual Environment

You will likely want to create a virtual environment to keep this project isolated. If you want all of the packages to be global instead, you may skip this step, although this is not recommended!

You can create a virtual environment directly from python using `venv`.

```
python3 -m venv /venv/yourVenvName
```

You want to create your venv in a directory called `venv/` or otherwise outside of this project to make sure the files contents of your environment are not picked up by Git.

Activate your virtual environment by running the `activate` script found in the `Scripts` folder of your venv for Windows systems, or the `bin` folder for POSIX.

```
.\venv\yourVenvName\Scripts\activate
```

## Package Installation

To install all the necessary libraries, perform a `pip install` from the `requirements.txt` file in the root directory.

```
pip install -r requirements.txt
```

## Configuration Setup

To setup your environment configuration, you must create a `.env` file in the root directory. To do this, copy and paste the `.env.example` file, which will contain all the current keys for the dotenv configuration.

Set the values in the `.env` file as needed.

For more information on configuration, please read [the Configuration documentation](./Configuration.md).
