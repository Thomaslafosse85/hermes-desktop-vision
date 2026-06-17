from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="hermes-desktop-vision",
    version="1.0.0",
    author="Thoma Lafosse & Gordias (starbottroopers)",
    description="Give your AI agent eyes and hands on Windows — Desktop, Browser & System control",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Thomaslafosse85/hermes-desktop-vision",
    packages=["hermes_desktop_vision"],
    python_requires=">=3.10",
    install_requires=[
        "easyocr>=1.7.0",
        "pyautogui>=0.9.54",
        "pillow>=10.0.0",
        "pygetwindow>=0.0.9",
        "numpy>=1.24.0",
    ],
    extras_require={
        "browser": [
            "websocket-client>=1.6.0",
        ],
        "yolo": [
            "ultralytics>=8.0.0",
            "opencv-python-headless>=4.8.0",
            "supervision>=0.20.0",
        ],
        "system": [
            "psutil>=5.9.0",
            "pyperclip>=1.8.0",
        ],
        "full": [
            "ultralytics>=8.0.0",
            "opencv-python-headless>=4.8.0",
            "supervision>=0.20.0",
            "websocket-client>=1.6.0",
            "psutil>=5.9.0",
            "pyperclip>=1.8.0",
            "screeninfo>=0.8.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
