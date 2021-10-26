# Configuration

This document will explain how to use global configuration throughout the project.
There are two sources of configuration:

-   **Command-line arguments** (via argparse), and
-   **.env file configuration**

To create a configuration parameter, first you must decide whether it will be an _argument-based_ configuration or a _environment-based_ configuration.

---

## Argument-Based Configuration

Parameters that are highly variable and want to be changed more frequently often are found here.

### Creating Arguments

Here, you can add an argument by adding the following line in the `_add_arguments_to_parser` function in `config/argparse_config.py`.

```python
def _add_arguments_to_parser(self, parser):
    # ...
    # Add your argument here:
    parser.add_argument('-m', '--my-arg', type=int, help='My argument is used for foo.', default=10)
```

For more information on the **argparse** package, and how to write and use your argument, please visit [the argparse documentation](https://docs.python.org/3/library/argparse.html).

### Configuring Arguments

To set a value for your argument, use one of the flags you defined when creating your argument when running the script. The following command will run `your_python_file.py` with a value of 5 for `my_arg`.

```ps
python your_python_file.py --my-arg 5
```

### Reading Arguments

To read your argument, you must import the `Config` class. `Config` does not need to be instantiated in your script, you may simply access it as is.

You can retrieve your argument by accessing the `args` property of the `Config` class, like so:

```python
from config import Config

# Get the argument `--my-arg` defined above
my_arg = Config.args.my_arg
print(my_arg) # 5
```

> ⚠️ **Be careful!** If you're accessing an argument that does not exist, it will raise an `AttributeError`. If your argument is defined but was not given a value, it will take on the value `None`.

---

## Environment-Based Configuration

Configuration settings that are sensitive or remain static are often found here. Values such as API keys or directories are generally preferred to be in the `.env` file because it is not committed to the repository.

### Creating Environment Variables

To add a configuration variable, create a new key-value entry in the form of `KEY=VALUE` in the `.env` file at the root of your project (if you do not have this file, please follow the [Configuration Setup section of the GettingStarted documentation](./GettingStarted.md#configuration-setup)).

```.env
# ...
# Add your argument here:
MY_ARG=2
```

> 🙏 Please remember to update the `.env.example` file with your key and an example value if you are creating a new variable. Do not use any sensitive information in the sample value.

To learn more about the rules of the dotenv configuration, visit [the python-dotenv documentation](https://pypi.org/project/python-dotenv/).

### Reading Environment Variables

To read an environment variable, you import the `Config` class and access the `env` property. The variable itself can be accessed through dot accesses similar to the argument configurations.

The following example demonstrates how to read the `MY_ARG` variable I added above:

```python
from config import Config

# Read the MY_ARG environment variable
my_arg = Config.env.MY_ARG
print(my_arg) # '2'
```

> ⚠️ The variable is case-sensitive! Accessing an invalid variable will raise a `KeyError`.

> ℹ️ The values in the environment configuration are all of type `str`. In this case, `my_arg` has the value `"2"` instead of the integer `2`.
