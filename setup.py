from setuptools import setup, find_packages

setup(
    name='mkdocs-gherkin-plugin',
    version="0.0.3",
    description="",
    author="Aleksandar KIRILOV",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'mkdocs.plugins': [
            'gherkin-plugin=mkdocs_gherkin_plugin:GherkinPlugin'
        ]
    }
)
