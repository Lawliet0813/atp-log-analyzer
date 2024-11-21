# visualization/core/themes.py

from typing import Dict, Any
from dataclasses import dataclass, field
import json
from pathlib import Path

@dataclass
class ThemeColors:
    """主題顏色配置"""
    background: str = "#2c3e50"
    foreground: str = "#ecf0f1"
    primary: str = "#3498db"
    secondary: str = "#2ecc71"
    warning: str = "#f1c40f"
    danger: str = "#e74c3c"
    success: str = "#2ecc71"
    info: str = "#3498db"
    border: str = "#bdc3c7"
    text: str = "#2c3e50"
    grid: str = "#34495e"

@dataclass
class ThemeFonts:
    """主題字型配置"""
    family: str = "Arial"
    sizes: Dict[str, int] = field(default_factory=lambda: {
        "small": 10,
        "normal": 12,
        "large": 14,
        "title": 16
    })

@dataclass
class ThemePlot:
    """繪圖相關配置"""
    line_width: int = 2
    grid_alpha: float = 0.3
    marker_size: int = 8
    padding: float = 0.1
    animation_duration: int = 200

@dataclass
class Theme:
    """完整主題配置"""
    name: str = "default"
    colors: ThemeColors = field(default_factory=ThemeColors)
    fonts: ThemeFonts = field(default_factory=ThemeFonts)
    plot: ThemePlot = field(default_factory=ThemePlot)

class ThemeManager:
    """主題管理器"""
    
    def __init__(self):
        self.themes: Dict[str, Theme] = {}
        self.current_theme: str = "default"
        self._load_builtin_themes()
        
    def _load_builtin_themes(self):
        """載入內建主題"""
        # 預設主題
        self.themes["default"] = Theme()
        
        # 暗色主題
        self.themes["dark"] = Theme(
            name="dark",
            colors=ThemeColors(
                background="#1a1a1a",
                foreground="#ffffff",
                primary="#3498db",
                secondary="#2ecc71",
                warning="#f1c40f",
                danger="#e74c3c",
                success="#2ecc71",
                info="#3498db",
                border="#333333",
                text="#ffffff",
                grid="#333333"
            )
        )
        
        # 高對比主題
        self.themes["contrast"] = Theme(
            name="contrast",
            colors=ThemeColors(
                background="#ffffff",
                foreground="#000000",
                primary="#0000ff",
                secondary="#00ff00",
                warning="#ffff00",
                danger="#ff0000",
                success="#00ff00",
                info="#0000ff",
                border="#000000",
                text="#000000",
                grid="#666666"
            )
        )
        
    def load_theme(self, name: str) -> Theme:
        """載入主題"""
        if name not in self.themes:
            raise ValueError(f"Theme '{name}' not found")
        self.current_theme = name
        return self.themes[name]
        
    def save_theme(self, theme: Theme):
        """儲存主題"""
        self.themes[theme.name] = theme
        
    def load_from_file(self, filepath: str):
        """從檔案載入主題"""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Theme file {filepath} not found")
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
                
            theme = Theme(
                name=theme_data.get('name', 'custom'),
                colors=ThemeColors(**theme_data.get('colors', {})),
                fonts=ThemeFonts(**theme_data.get('fonts', {})),
                plot=ThemePlot(**theme_data.get('plot', {}))
            )
            self.save_theme(theme)
            
        except Exception as e:
            raise ValueError(f"Failed to load theme: {str(e)}")
            
    def save_to_file(self, theme_name: str, filepath: str):
        """儲存主題到檔案"""
        if theme_name not in self.themes:
            raise ValueError(f"Theme '{theme_name}' not found")
            
        theme = self.themes[theme_name]
        theme_data = {
            'name': theme.name,
            'colors': {
                k: v for k, v in vars(theme.colors).items()
                if not k.startswith('_')
            },
            'fonts': {
                k: v for k, v in vars(theme.fonts).items()
                if not k.startswith('_')
            },
            'plot': {
                k: v for k, v in vars(theme.plot).items()
                if not k.startswith('_')
            }
        }
        
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(theme_data, f, indent=4)
            
    def get_theme_names(self) -> list:
        """獲取所有主題名稱"""
        return list(self.themes.keys())
        
    def get_current_theme(self) -> Theme:
        """獲取當前主題"""
        return self.themes[self.current_theme]
        
    def create_theme(self, name: str, **kwargs) -> Theme:
        """創建新主題"""
        if name in self.themes:
            raise ValueError(f"Theme '{name}' already exists")
            
        theme = Theme(name=name, **kwargs)
        self.save_theme(theme)
        return theme
