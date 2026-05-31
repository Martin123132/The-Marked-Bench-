from setuptools import setup, find_packages

setup(
    name="marked_bench",
    version="0.3.7",
    description="The Marked Bench contradiction-detection evaluation benchmark",
    author="Martin Ollett",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=["numpy"],
    entry_points={
        "console_scripts": [
            "marked-bench=marked_bench.benchmark_cli:main",
        ],
    },
)
