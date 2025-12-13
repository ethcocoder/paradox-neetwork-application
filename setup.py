from setuptools import setup, find_packages

setup(
    name="paradoxlf",
    version="0.1.0",
    description="A latent memory and active inference engine for AI agents.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Natnael Ermiyas (Ethco Coders & Inotrade)",
    author_email="contact@ethcocoder.com",
    url="https://github.com/ethcocoder/paradoxlf",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "psutil>=5.8.0",
    ],
    extras_require={
        "gpu": ["torch>=1.10.0"],
        "viz": ["matplotlib", "scikit-learn"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.7',
)
