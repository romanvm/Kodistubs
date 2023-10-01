from setuptools import setup

setup(
    packages=["xbmc", "xbmcaddon", "xbmcdrm", "xbmcgui", "xbmcplugin", "xbmcvfs"],
    package_data={
        "xbmc": ["py.typed"],
        "xbmcaddon": ["py.typed"],
        "xbmcdrm": ["py.typed"],
        "xbmcgui": ["py.typed"],
        "xbmcplugin": ["py.typed"],
        "xbmcvfs": ["py.typed"],
    }
)
