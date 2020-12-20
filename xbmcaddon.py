# This file is generated from Kodi source code and post-edited
# to correct code style and docstrings formatting.
# License: GPL v.3 <https://www.gnu.org/licenses/gpl-3.0.en.html>
"""
**Kodi's addon class**
"""
from typing import Optional

__kodistubs__ = True


class Addon:
    """
    **Kodi's addon class.**

    Offers classes and functions that manipulate the add-on settings, information
    and localization.

    Creates a new AddOn class.

    :param id: [opt] string - id of the addon as specified inaddon.xml

    .. note::
        Specifying the addon id is not needed.  Important however is that
        the addon folder has the same name as the AddOn id provided
        inaddon.xml.  You can optionally specify the addon id from another
        installed addon to retrieve settings from it.

    @python_v13 **id** is optional as it will be auto detected for this
    add-on instance.

    Example::

        ..
        self.Addon = xbmcaddon.Addon()
        self.Addon = xbmcaddon.Addon('script.foo.bar')
        ..
    """
    
    def __init__(self, id: Optional[str] = None) -> None:
        pass
    
    def getLocalizedString(self, id: int) -> str:
        """
        Returns an addon's localized 'string'.

        :param id: integer - id# for string you want to localize.
        :return: Localized 'string'

        @python_v13 **id** is optional as it will be auto detected for this
        add-on instance.

        Example::

            ..
            locstr = self.Addon.getLocalizedString(32000)
            ..
        """
        return ""
    
    def getSetting(self, id: str) -> str:
        """
        Returns the value of a setting as string.

        :param id: string - id of the setting that the module needs to access.
        :return: Setting as a string

        @python_v13 **id** is optional as it will be auto detected for this
        add-on instance.

        Example::

            ..
            apikey = self.Addon.getSetting('apikey')
            ..
        """
        return ""
    
    def getSettingBool(self, id: str) -> bool:
        """
        Returns the value of a setting as a boolean.

        :param id: string - id of the setting that the module needs to access.
        :return: Setting as a boolean

        @python_v18 New function added.

        Example::

            ..
            enabled = self.Addon.getSettingBool('enabled')
            ..
        """
        return True
    
    def getSettingInt(self, id: str) -> int:
        """
        Returns the value of a setting as an integer.

        :param id: string - id of the setting that the module needs to access.
        :return: Setting as an integer

        @python_v18 New function added.

        Example::

            ..
            max = self.Addon.getSettingInt('max')
            ..
        """
        return 0
    
    def getSettingNumber(self, id: str) -> float:
        """
        Returns the value of a setting as a floating point number.

        :param id: string - id of the setting that the module needs to access.
        :return: Setting as a floating point number

        @python_v18 New function added.

        Example::

            ..
            max = self.Addon.getSettingNumber('max')
            ..
        """
        return 0.0
    
    def getSettingString(self, id: str) -> str:
        """
        Returns the value of a setting as a string.

        :param id: string - id of the setting that the module needs to access.
        :return: Setting as a string

        @python_v18 New function added.

        Example::

            ..
            apikey = self.Addon.getSettingString('apikey')
            ..
        """
        return ""
    
    def setSetting(self, id: str, value: str) -> None:
        """
        Sets a script setting.

        :param id: string - id of the setting that the module needs to access.
        :param value: string - value of the setting.

        .. note::
            You can use the above as keywords for arguments.

        @python_v13 **id** is optional as it will be auto detected for this
        add-on instance.

        Example::

            ..
            self.Addon.setSetting(id='username', value='teamkodi')
            ..
        """
        pass
    
    def setSettingBool(self, id: str, value: bool) -> bool:
        """
        Sets a script setting.

        :param id: string - id of the setting that the module needs to access.
        :param value: boolean - value of the setting.
        :return: True if the value of the setting was set, false otherwise

        .. note::
            You can use the above as keywords for arguments.

        @python_v18 New function added.

        Example::

            ..
            self.Addon.setSettingBool(id='enabled', value=True)
            ..
        """
        return True
    
    def setSettingInt(self, id: str, value: int) -> bool:
        """
        Sets a script setting.

        :param id: string - id of the setting that the module needs to access.
        :param value: integer - value of the setting.
        :return: True if the value of the setting was set, false otherwise

        .. note::
            You can use the above as keywords for arguments.

        @python_v18 New function added.

        Example::

            ..
            self.Addon.setSettingInt(id='max', value=5)
            ..
        """
        return True
    
    def setSettingNumber(self, id: str, value: float) -> bool:
        """
        Sets a script setting.

        :param id: string - id of the setting that the module needs to access.
        :param value: float - value of the setting.
        :return: True if the value of the setting was set, false otherwise

        .. note::
            You can use the above as keywords for arguments.

        @python_v18 New function added.

        Example::

            ..
            self.Addon.setSettingNumber(id='max', value=5.5)
            ..
        """
        return True
    
    def setSettingString(self, id: str, value: str) -> bool:
        """
        Sets a script setting.

        :param id: string - id of the setting that the module needs to access.
        :param value: string or unicode - value of the setting.
        :return: True if the value of the setting was set, false otherwise

        .. note::
            You can use the above as keywords for arguments.

        @python_v18 New function added.

        Example::

            ..
            self.Addon.setSettingString(id='username', value='teamkodi')
            ..
        """
        return True
    
    def openSettings(self) -> None:
        """
        Opens this scripts settings dialog.

        Example::

            ..
            self.Addon.openSettings()
            ..
        """
        pass
    
    def getAddonInfo(self, id: str) -> str:
        """
        Returns the value of an addon property as a string.

        :param id: string - id of the property that the module needs to access.

        Choices for the property are

        ====== ========= =========== ========== 
        author changelog description disclaimer 
        fanart icon      id          name       
        path   profile   stars       summary    
        type   version                          
        ====== ========= =========== ========== 

        :return: AddOn property as a string

        Example::

            ..
            version = self.Addon.getAddonInfo('version')
            ..
        """
        return ""
