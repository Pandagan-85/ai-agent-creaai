try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

    def find_packages():
        """Simple replacement for setuptools.find_packages"""
        return ['interview_prep', 'interview_prep.utils', 'interview_prep.tools', 'interview_prep.config']

setup(
    name="interview_prep",
    version="0.1.0",
    description="AI Interview Preparation using CrewAI",
    author="Veronica Schembri",
    author_email="veronicaschembri@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "crewai>=0.118.0",
        "crewai-tools>=0.42.2",
        "python-dotenv>=1.1.0",
        "streamlit>=1.45.0",
        "pysqlite3-binary"
    ],
)
