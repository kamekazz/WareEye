# Contributing to WareEye

Thank you for your interest in helping improve WareEye! Contributions of all
sizes are welcome. This project is split into a Python server and client so most
changes will involve one or both of those components.

## Getting started

1. Fork the repository and clone your fork.
2. Install the dependencies for the part you want to work on:

   ```bash
   cd Server
   pip install -r requirements.txt
   ```

   and/or

   ```bash
   cd Client
   pip install -r requirements.txt
   ```

3. Run the applications to ensure they start correctly before making changes:

   ```bash
   python Server/app.py
   python Client/client.py
   ```

## Making changes

* Use Python 3.12 or newer.
* Keep code style consistent with the existing project (we use
  [black](https://black.readthedocs.io/) for formatting).
* Include docstrings and comments where helpful.
* If adding features or fixing bugs, consider adding tests if possible.

## Submitting a pull request

1. Create a new branch in your fork for each set of related changes.
2. Push the branch and open a pull request against the `main` branch of this
   repository.
3. Provide a clear description of what you changed and why.
4. Ensure `pip install -r requirements.txt` succeeds for both `Server` and
   `Client` before submitting.

We will review your pull request and work with you to get it merged. Thanks for
helping make WareEye better!
