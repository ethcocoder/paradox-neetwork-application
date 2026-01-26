# How to Publish Paradox to PyPI

You have asked to use **PyPI (Python Package Index)**. Since I am an AI, I cannot upload files to your account, but I have configured everything so you can do it in **3 steps**.

## Step 1: Create an Account
1.  Go to [https://pypi.org/account/register/](https://pypi.org/account/register/) and register.
2.  Go to **Account Settings** -> **API Tokens**.
3.  Create a new token (scope: "Entire account").
4.  Copy the token (it starts with `pypi-`).

## Step 2: Install Build Tools
Open your terminal and run:

```bash
pip install build twine
```

## Step 3: Build and Upload
Run these commands in the `paradoxlf` directory:

1.  **Build the package:**
    ```bash
    python -m build
    ```
    (This creates a `dist/` folder with `.tar.gz` and `.whl` files)

2.  **Upload to PyPI:**
    ```bash
    python -m twine upload dist/*
    ```

3.  **Authenticate:**
    *   **Username:** `__token__`
    *   **Password:** (Paste your `pypi-` token here)

## Success!
Once done, anyone in the world can install your software using:
```bash
pip install paradoxlf
```
