from setuptools import setup, find_packages

setup(
    name="ResearchTikPy",
    version="0.1.4",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "requests", "pandas" 
    ],
    author="Julian Hohner",
    author_email="daswaeldchen@gmail.com",
    description="Python API wrapper for the TikTok Research API",
    keywords=["TikTok API research", "tiktok", "python3", "api", "tiktok-api", "tiktok api", "tiktok_api", "research"],
    url="https://github.com/HohnerJulian/ResearchTikPy", 
)
