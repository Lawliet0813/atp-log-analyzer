from setuptools import setup, find_packages
import os
from pathlib import Path

# 讀取README檔案
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# 取得主要版本號
version = "1.0.0"

# 程式相依套件
requirements = [
    "PyQt6>=6.4.0",
    "pyqtgraph>=0.13.1",
    "numpy>=1.23.0",
    "pandas>=1.5.0",
    "openpyxl>=3.0.10",  # 用於Excel檔案處理
    "python-dateutil>=2.8.2",
    "pyinstaller>=5.6.2",  # 用於打包執行檔
]

# 開發用套件
dev_requirements = [
    "pytest>=7.2.0",
    "pytest-qt>=4.2.0",
    "pytest-cov>=4.0.0",
    "black>=22.10.0",     # 程式碼格式化
    "flake8>=5.0.4",      # 程式碼檢查
    "mypy>=0.991",        # 型別檢查
    "sphinx>=5.3.0",      # 文件產生
]

setup(
    name="atp-analyzer",
    version=version,
    author="TRA ATP Team",
    author_email="atp@tra.gov.tw",
    description="ATP行車紀錄分析系統",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tra/atp-analyzer",
    packages=find_packages(),
    
    # 程式進入點
    entry_points={
        "console_scripts": [
            "atp-analyzer=src.main:main",
        ],
    },
    
    # 安裝資料檔案
    package_data={
        "src": [
            "assets/icons/*.png",
            "assets/styles/*.qss",
            "assets/translations/*.qm",
            "config/*.json",
        ],
    },
    
    # 相依套件
    install_requires=requirements,
    
    # 開發用套件
    extras_require={
        "dev": dev_requirements,
    },
    
    # 分類資訊
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: Microsoft :: Windows",
        "Natural Language :: Chinese (Traditional)",
        "Environment :: X11 Applications :: Qt",
    ],
    
    # 專案資訊
    keywords="ATP, train, analysis, TRA",
    platforms=["win32", "win64"],
    python_requires=">=3.9",
    zip_safe=False,  # 不要壓縮套件
)

# PyInstaller設定
if os.environ.get("PYINSTALLER_BUILD"):
    import PyInstaller.__main__
    
    PyInstaller.__main__.run([
        "--name=ATP分析系統",
        "--onefile",                     # 打包成單一執行檔
        "--windowed",                    # Windows GUI應用程式
        "--icon=src/assets/icons/app.ico",  # 應用程式圖示
        "--add-data=src/assets;assets",  # 包含資源檔案
        "--add-data=src/config;config",  # 包含設定檔
        "--clean",                       # 清理暫存檔
        "src/main.py"                    # 主程式
    ])

# 打包指令範例
"""
# 開發環境安裝
pip install -e .[dev]

# 建立執行檔
python setup.py build

# 建立安裝檔
python setup.py bdist_wheel

# PyInstaller打包
set PYINSTALLER_BUILD=1
python setup.py build

# 執行測試
python -m pytest

# 產生文件
python setup.py build_sphinx
"""

# 相關檔案結構
"""
atp-analyzer/
├── src/
│   ├── assets/
│   │   ├── icons/
│   │   ├── styles/
│   │   └── translations/
│   ├── config/
│   ├── gui/
│   ├── analyzer/
│   ├── utils/
│   └── main.py
├── tests/
├── docs/
├── README.md
├── requirements.txt
└── setup.py
"""
