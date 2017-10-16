# Supergenerator

because we can

# Run the bot

is as simple as: `./supergenerator.py`

# Python setup (macOS)
1. install\/update [homebrew](https://brew.sh/)
2. install python3: `$ brew install python3`

    **NOTE:** `python` points to system installation (tipycally 2.7.X), `python3` points to homebrew installation

3. configure virtual environment
    ```
    $ mkdir python_envs
    $ cd python_envs/
    $ python3 -m venv supergenerator
    # activate the env:
    $ source python_envs/supergenerator/bin/activate
    # deactivate the env:
    $ deactivate
    ```
    **NOTE:** `python --version` points to python3 and also does pip
4. install dependecies:
    ```
    $ source python_envs/supergenerator/bin/activate
    $ cd supergenerator_bot/
    $ pip install -r requirements.txt
    ```

##### Update requirements file:
In case other dependencies are added during development, to update the requirements file run:

`$ pip freeze > requirements.txt`
