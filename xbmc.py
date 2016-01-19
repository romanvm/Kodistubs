## @package xbmc
#  Various classes and functions to interact with XBMC.
#
"""
Various classes and functions to interact with Kodi.
"""

import xbmcgui as _xbmcgui

CAPTURE_FLAG_CONTINUOUS = 1
CAPTURE_FLAG_IMMEDIATELY = 2
CAPTURE_STATE_DONE = 3
CAPTURE_STATE_FAILED = 4
CAPTURE_STATE_WORKING = 0
DRIVE_NOT_READY = 1
ENGLISH_NAME = 2
ISO_639_1 = 0
ISO_639_2 = 1
LOGDEBUG = 0
LOGERROR = 4
LOGFATAL = 6
LOGINFO = 1
LOGNONE = 7
LOGNOTICE = 2
LOGSEVERE = 5
LOGWARNING = 3
PLAYER_CORE_AUTO = 0
PLAYER_CORE_DVDPLAYER = 1
PLAYER_CORE_MPLAYER = 2
PLAYER_CORE_PAPLAYER = 3
PLAYLIST_MUSIC = 0
PLAYLIST_VIDEO = 1
SERVER_AIRPLAYSERVER = 2
SERVER_EVENTSERVER = 6
SERVER_JSONRPCSERVER = 3
SERVER_UPNPRENDERER = 4
SERVER_UPNPSERVER = 5
SERVER_WEBSERVER = 1
SERVER_ZEROCONF = 7
TRAY_CLOSED_MEDIA_PRESENT = 96
TRAY_CLOSED_NO_MEDIA = 64
TRAY_OPEN = 16
__author__ = 'Team Kodi <http://kodi.tv>'
__credits__ = 'Team Kodi'
__date__ = 'Fri May 01 16:22:03 BST 2015'
__platform__ = 'ALL'
__version__ = '2.20.0'
abortRequested = False
"""Returns ``True`` if Kodi prepares to close itself"""


class Keyboard(object):
    """
    Creates a new Keyboard object with default text heading and hidden input flag if supplied.

    :param line: string - default text entry.
    :param heading: string - keyboard heading.
    :param hidden: boolean - True for hidden text entry.

    Example::

        kb = xbmc.Keyboard('default', 'heading', True)
        kb.setDefault('password') # optional
        kb.setHeading('Enter password') # optional
        kb.setHiddenInput(True) # optional
        kb.doModal()
        if (kb.isConfirmed()):
            text = kb.getText()
    """
    def __init__(self, line='', heading='', hidden=False):
        """
        Creates a new Keyboard object with default text heading and hidden input flag if supplied.

        line: string - default text entry.
        heading: string - keyboard heading.
        hidden: boolean - True for hidden text entry.

        Example:
            kb = xbmc.Keyboard('default', 'heading', True)
            kb.setDefault('password') # optional
            kb.setHeading('Enter password') # optional
            kb.setHiddenInput(True) # optional
            kb.doModal()
            if (kb.isConfirmed()):
                text = kb.getText()
        """
        pass

    def doModal(self, autoclose=0):
        """Show keyboard and wait for user action.

        :param autoclose: integer - milliseconds to autoclose dialog.

        .. note::
            autoclose = 0 - This disables autoclose

        Example::

            kb.doModal(30000)
        """
        pass

    def setDefault(self, line=''):
        """Set the default text entry.

        :param line: string - default text entry.

        Example::

            kb.setDefault('password')
        """
        pass

    def setHiddenInput(self, hidden=False):
        """Allows hidden text entry.

        :param hidden: boolean - ``True`` for hidden text entry.

        Example::

            kb.setHiddenInput(True)
        """
        pass

    def setHeading(self, heading):
        """Set the keyboard heading.

        :param heading: string - keyboard heading.

        Example::

            kb.setHeading('Enter password')
        """
        pass

    def getText(self):
        """Returns the user input as a string.

        :return: entered text

        .. note::
            This will always return the text entry even if you cancel the keyboard.
            Use the isConfirmed() method to check if user cancelled the keyboard.
        """
        return str()

    def isConfirmed(self):
        """Returns ``False`` if the user cancelled the input.

        :return: confirmed status

        example::

            if (kb.isConfirmed()):
                pass
        """
        return bool(1)


class Player(object):
    """
    Player()

    Creates a new Player with as default the xbmc music playlist.

    .. note:: currently Player class constructor does not take any parameters.
        Kodi automatically selects a necessary player.
    """
    def __init__(self):
        """
        Creates a new Player with as default the xbmc music playlist.
        """
        pass

    def play(self, item=None, listitem=None, windowed=False, statrpos=-1):
        """
        Play this item.

        :param item: [opt] string - filename, url or playlist.
        :param listitem: [opt] listitem - used with setInfo() to set different infolabels.
        :param windowed: [opt] bool - true=play video windowed, false=play users preference.(default)
        :param startpos: [opt] int - starting position when playing a playlist. Default = -1

        .. note:: If item is not given then the Player will try to play the current item
            in the current playlist.

        You can use the above as keywords for arguments and skip certain optional arguments.
        Once you use a keyword, all following arguments require the keyword.

        example::

            listitem = xbmcgui.ListItem('Ironman')
            listitem.setInfo('video', {'Title': 'Ironman', 'Genre': 'Science Fiction'})
            xbmc.Player().play(url, listitem, windowed)
            xbmc.Player().play(playlist, listitem, windowed, startpos)
        """
        pass

    def stop(self):
        """Stop playing."""
        pass

    def pause(self):
        """Pause playing."""
        pass

    def playnext(self):
        """Play next item in playlist."""
        pass

    def playprevious(self):
        """Play previous item in playlist."""
        pass

    def playselected(self, selected):
        """Play a certain item from the current playlist."""
        pass

    def onPlayBackStarted(self):
        """Will be called when xbmc starts playing a file."""
        pass

    def onPlayBackEnded(self):
        """Will be called when xbmc stops playing a file."""
        pass

    def onPlayBackStopped(self):
        """Will be called when user stops xbmc playing a file."""

    def onPlayBackPaused(self):
        """Will be called when user pauses a playing file."""
        pass

    def onPlayBackResumed(self):
        """Will be called when user resumes a paused file."""
        pass

    def onPlayBackSeek(self, time, seekOffset):
        """
        onPlayBackSeek method.

        :param time: integer - time to seek to.
        :param seekOffset: integer - ?.

        Will be called when user seeks to a time
        """
        pass

    def onPlayBackSeekChapter(self, chapter):
        """
        onPlayBackSeekChapter method.

        :param chapter: integer - chapter to seek to.

        Will be called when user performs a chapter seek
        """
        pass

    def onPlayBackSpeedChanged(self, speed):
        """
        onPlayBackSpeedChanged(speed) -- onPlayBackSpeedChanged method.

        :param speed: integer - current speed of player.

        .. note:: negative speed means player is rewinding, 1 is normal playback speed.

        Will be called when players speed changes. (eg. user FF/RW)
        """
        pass

    def onQueueNextItem(self):
        """
        onQueueNextItem method.

        Will be called when player requests next item
        """
        pass

    def isPlaying(self):
        """Returns ``True`` is xbmc is playing a file."""
        return bool(1)

    def isPlayingAudio(self):
        """Returns ``True`` is xbmc is playing an audio file."""
        return bool(1)

    def isPlayingVideo(self):
        """Returns ``True`` if xbmc is playing a video."""
        return bool(1)

    def getPlayingFile(self):
        """
        returns the current playing file as a string.

        .. note:: For LiveTV, returns a pvr:// url which is not translatable to an OS specific file or external url

        :raises: Exception, if player is not playing a file.
        """
        return str()

    def getVideoInfoTag(self):
        """Returns the VideoInfoTag of the current playing Movie.

        :raises: Exception: If player is not playing a file or current file is not a movie file.

        .. note:: This doesn't work yet, it's not tested.
        """
        return InfoTagVideo()

    def getMusicInfoTag(self):
        """Returns the MusicInfoTag of the current playing 'Song'.

        :raises: Exception: If player is not playing a file or current file is not a music file.
        """
        return InfoTagMusic()

    def getTotalTime(self):
        """Returns the total time of the current playing media in seconds.

        This is only accurate to the full second.

        :raises: Exception: If player is not playing a file.
        """
        return float()

    def getTime(self):
        """Returns the current time of the current playing media as fractional seconds.

        :raises: Exception: If player is not playing a file.
        """
        return float()

    def seekTime(self, pTime):
        """Seeks the specified amount of time as fractional seconds.

        The time specified is relative to the beginning of the currently playing media file.

        :raises: Exception: If player is not playing a file.
        """
        pass

    def setSubtitles(self, subtitleFile):
        """Set subtitle file and enable subtitles.

        :param subtitleFile: string or unicode - Path to subtitle.

        Example::

            setSubtitles('/path/to/subtitle/test.srt')
        """
        pass

    def getSubtitles(self):
        """Get subtitle stream name."""
        return str()

    def disableSubtitles(self):
        """Disable subtitles."""
        pass

    def getAvailableAudioStreams(self):
        """Get audio stream names."""
        return list()

    def getAvailableSubtitleStreams(self):
        """
        get Subtitle stream names
        """
        return list()

    def setAudioStream(self, iStream):
        """Set audio stream.

        :param iStream: int
        """
        pass

    def setSubtitleStream(self, iStream):
        """
        set Subtitle Stream

        :param iStream: int

        example::

            setSubtitleStream(1)
        """
        pass

    def showSubtitles(self, bVisible):
        """
        enable/disable subtitles

        :param bVisible: boolean - ``True`` for visible subtitles.

        example::

            xbmc.Player().showSubtitles(True)
        """
        pass


class PlayList(object):
    """Retrieve a reference from a valid xbmc playlist

    :param playlist: int - can be one of the next values:

    ::

        0: xbmc.PLAYLIST_MUSIC
        1: xbmc.PLAYLIST_VIDEO

    Use PlayList[int position] or __getitem__(int position) to get a PlayListItem.
    """
    def __init__(self, playList):
        """Retrieve a reference from a valid xbmc playlist

        playlist: int - can be one of the next values:

        ::

            0: xbmc.PLAYLIST_MUSIC
            1: xbmc.PLAYLIST_VIDEO

        Use PlayList[int position] or __getitem__(int position) to get a PlayListItem.
        """
        pass

    def __getitem__(self, item):
        """x.__getitem__(y) <==> x[y]"""
        return _xbmcgui.ListItem()

    def __len__(self):
        """x.__len__() <==> len(x)"""
        return int()

    def add(self, url, listitem=None, index=-1):
        """Adds a new file to the playlist.

        :param url: string or unicode - filename or url to add.
        :param listitem: listitem - used with setInfo() to set different infolabels.
        :param index: integer - position to add playlist item.

        Example::

            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            video = 'F:\\movies\\Ironman.mov'
            listitem = xbmcgui.ListItem('Ironman', thumbnailImage='F:\\movies\\Ironman.tbn')
            listitem.setInfo('video', {'Title': 'Ironman', 'Genre': 'Science Fiction'})
            playlist.add(url=video, listitem=listitem, index=7)
        """
        pass

    def load(self, filename):
        """Load a playlist.

        Clear current playlist and copy items from the file to this Playlist.
        filename can be like .pls or .m3u ...

        :param filename:
        :return: ``False`` if unable to load playlist, True otherwise.
        """
        return bool(1)

    def remove(self, filename):
        """Remove an item with this filename from the playlist.

        :param filename:
        """
        pass

    def clear(self):
        """Clear all items in the playlist."""
        pass

    def shuffle(self):
        """Shuffle the playlist."""
        pass

    def unshuffle(self):
        """Unshuffle the playlist."""
        pass

    def size(self):
        """Returns the total number of PlayListItems in this playlist."""
        return int()

    def getposition(self):
        """Returns the position of the current song in this playlist."""
        return int()

    def getPlayListId(self):
        """getPlayListId() --returns an integer."""
        return int()


class PlayListItem(object):
    """Creates a new PlaylistItem which can be added to a PlayList."""

    def getdescription(self):
        """Returns the description of this PlayListItem."""
        return str()

    def getduration(self):
        """Returns the duration of this PlayListItem."""
        return long()

    def getfilename(self):
        """Returns the filename of this PlayListItem."""
        return str()


class InfoTagMusic(object):
    """InfoTagMusic class"""
    def getURL(self):
        """Returns a string."""
        return str()

    def getTitle(self):
        """Returns a string."""
        return str()

    def getArtist(self):
        """Returns a string."""
        return str()

    def getAlbumArtist(self):
        """Returns a string."""
        return str()

    def getAlbum(self):
        """Returns a string."""
        return str()

    def getGenre(self):
        """Returns a string."""
        return str()

    def getDuration(self):
        """Returns an integer."""
        return int()

    def getTrack(self):
        """Returns an integer."""
        return int()

    def getDisc(self):
        """Returns an integer."""
        return int()

    def getTrackAndDisc(self):
        """Returns an integer."""
        return int()

    def getReleaseDate(self):
        """Returns a string."""
        return str()

    def getListeners(self):
        """Returns an integer."""
        return int()

    def getPlayCount(self):
        """Returns an integer."""
        return int()

    def getLastPlayed(self):
        """Returns a string."""
        return str()

    def getComment(self):
        """Returns a string."""
        return str()

    def getLyrics(self):
        """Returns a string."""
        return str()


class InfoTagVideo(object):
    """InfoTagVideo class"""
    def getDirector(self):
        """Returns a string."""
        return str()

    def getWritingCredits(self):
        """Returns a string."""
        return str()

    def getGenre(self):
        """Returns a string."""
        return str()

    def getTagLine(self):
        """Returns a string."""
        return str()

    def getPlotOutline(self):
        """Returns a string."""
        return str()

    def getPlot(self):
        """Returns a string."""
        return str()

    def getPictureURL(self):
        """Returns a string."""
        return str()

    def getTitle(self):
        """Returns a string."""
        return str()

    def getOriginalTitle(self):
        """Returns a string."""
        return str()

    def getVotes(self):
        """Returns a string."""
        return str()

    def getCast(self):
        """Returns a string."""
        return str()

    def getFile(self):
        """Returns a string."""
        return str()

    def getPath(self):
        """Returns a string."""
        return str()

    def getIMDBNumber(self):
        """Returns a string."""
        return str()

    def getYear(self):
        """Returns an integer."""
        return int()

    def getPremiered(self):
        """Returns a string."""
        return str()

    def getFirstAired(self):
        """Returns a string."""
        return str()

    def getRating(self):
        """Returns a float."""
        return float()

    def getPlayCount(self):
        """Returns an integer."""
        return int()

    def getLastPlayed(self):
        """Returns a string."""
        return str()


class Monitor(object):
    """
    Monitor class.

    Creates a new Monitor to notify addon about changes.
    """
    def onAbortRequested(self):
        """
        .. warning:: Deprecated!
        """
        pass

    def onDatabaseUpdated(self, database):
        """
        .. warning:: Deprecated!
        """
        pass

    def onScreensaverActivated(self):
        """
        onScreensaverActivated method.

        Will be called when screensaver kicks in
        """
        pass

    def onScreensaverDeactivated(self):
        """
        onScreensaverDeactivated method.

        Will be called when screensaver goes off
        """
        pass

    def onSettingsChanged(self):
        """
        onSettingsChanged method.

        Will be called when addon settings are changed
        """
        pass

    def onDatabaseScanStarted(self, database):
        """
        .. warning:: Deprecated!
        """
        pass

    def onNotification(self, sender, method, data):
        """
        onNotification method.

        :param sender: str - sender of the notification
        :param method: str - name of the notification
        :param data: str - JSON-encoded data of the notification

        Will be called when Kodi receives or sends a notification
        """
        pass

    def onCleanStarted(self, library):
        """
        onCleanStarted method.

        :param library: video/music as string

        Will be called when library clean has started
        and return video or music to indicate which library is being cleaned
        """
        pass

    def onCleanFinished(self, library):
        """
        onCleanFinished method.

        :param library: video/music as string

        Will be called when library clean has ended
        and return video or music to indicate which library has been cleaned
        """
        pass

    def onDPMSActivated(self):
        """
        onDPMSActivated method.

        Will be called when energysaving/DPMS gets active
        """
        pass

    def onDPMSDeactivated(self):
        """
        onDPMSDeactivated method.

        Will be called when energysaving/DPMS is turned off
        """
        pass

    def onScanFinished(self, library):
        """
        onScanFinished method.

        :param library: video/music as string

        Will be called when library scan has ended
        and return video or music to indicate which library has been scanned
        """
        pass

    def onScanStarted(self, library):
        """
        onScanStarted method.

        :param library: video/music as string

        Will be called when library scan has started
        and return video or music to indicate which library is being scanned
        """
        pass

    def waitForAbort(self, timeout=0):
        """
        Block until abort is requested, or until timeout occurs.

        If an abort requested have already been made, return immediately.
        Returns ``True`` when abort have been requested,
        ``False`` if a timeout is given and the operation times out.

        :param timeout: float - (optional) timeout in seconds. Default: no timeout.
        :return: bool
        """
        return bool(0)

    def abortRequested(self):
        """
        Returns ``True`` if abort has been requested.
        """
        return bool(0)


class RenderCapture(object):
    """RenerCapture class"""
    def capture(self, width, height, flags=0):
        """
        Issue capture request.

        :param width: Width capture image should be rendered to
        :param height: Height capture image should should be rendered to
        :param flags: Optional. Flags that control the capture processing.

        The value for 'flags' could be or'ed from the following constants:

        - ``xbmc.CAPTURE_FLAG_CONTINUOUS``: after a capture is done,
          issue a new capture request immediately
        - ``xbmc.CAPTURE_FLAG_IMMEDIATELY``: read out immediately whencapture() is called,
          this can cause a busy wait

        .. warning:: As of Kodi 17.x (Krypton) ``flags`` option will be depreciated.
        """
        pass

    def getAspectRatio(self):
        """
        :return: aspect ratio of currently displayed video as a float number.
        """
        return float()

    def getCaptureState(self):
        """
        :return: processing state of capture request.

        The returned value could be compared against the following constants::

        - ``xbmc.CAPTURE_STATE_WORKING``: Capture request in progress.
        - ``xbmc.CAPTURE_STATE_DONE``: Capture request done. The image could be retrieved withgetImage()
        - ``xbmc.CAPTURE_STATE_FAILED``: Capture request failed.

        .. warning:: Will be depreciated in Kodi 17.x (Krypton)
        """
        return int()

    def getHeight(self):
        """
        :return: height of captured image.
        """
        return int()

    def getImage(self, msecs=0):
        """
        Get image

        :param msecs: wait time in msec
        :return: captured image as a bytearray.

        .. note:: ``msec`` param will be added in Kodi 17.x (Krypton).

        The size of the image isgetWidth() * getHeight() * 4
        """
        return bytearray()

    def getImageFormat(self):
        """
        :return: format of captured image: 'BGRA' or 'RGBA'.

        .. note:: As of Kodi 17.x (Krypton) 'BRRA' will always be returned
        """
        return str()

    def getWidth(self):
        """
        :return: width of captured image.
        """
        return int()

    def waitForCaptureStateChangeEvent(self, msecs=0):
        """
        wait for capture state change event

        :param msecs: Milliseconds to wait. Waits forever if not specified.

        The method will return ``1`` if the Event was triggered. Otherwise it will return ``0``.
        """
        return int()


def audioResume():
    """
    Resume Audio engine.

    example::

        xbmc.audioResume()
    """
    pass


def audioSuspend():
    """
    Suspend Audio engine.

    example::

        xbmc.audioSuspend()
    """
    pass


def convertLanguage(language, format):
    """
    Returns the given language converted to the given format as a string.

    :param language: string either as name in English, two letter code (ISO 639-1),
        or three letter code (ISO 639-2/T(B)
    :param format: format of the returned language string:

    - ``xbmc.ISO_639_1``: two letter code as defined in ISO 639-1
    - ``xbmc.ISO_639_2``: three letter code as defined in ISO 639-2/T or ISO 639-2/B
    - ``xbmc.ENGLISH_NAME``: full language name in English (default)

    example::

        language = xbmc.convertLanguage(English, xbmc.ISO_639_2)
    """
    return str()


def enableNavSounds(yesNo):
    """
    Enables/Disables nav sounds

    :param yesNo: enable (``True``) or disable (``False``) nav sounds

    example::

        xbmc.enableNavSounds(True)
    """
    pass


def executeJSONRPC(jsonrpccommand):
    """
    Execute an JSONRPC command.

    :param jsonrpccommand: string - jsonrpc command to execute.

    List of commands: http://wiki.xbmc.org/?title=JSON-RPC_API

    example::

        response = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "JSONRPC.Introspect", "id": 1 }')
    """
    return str()


def executebuiltin(function, wait=False):
    """
    Execute a built in XBMC function.

    :param function: string - builtin function to execute.

    List of functions: http://wiki.xbmc.org/?title=List_of_Built_In_Functions

    example::

        xbmc.executebuiltin('XBMC.RunXBE(c:\avalaunch.xbe)')
    """
    pass


def executescript(script):
    """
    Execute a python script.

    :param script: string - script filename to execute.

    example::

        xbmc.executescript('special://home/scripts/update.py')
    """
    pass


def getCacheThumbName(path):
    """
    Returns a thumb cache filename.

    :param path: string or unicode -- path to file

    Example::

        thumb = xbmc.getCacheThumbName('f:\videos\movie.avi')
    """
    return str()


def getCleanMovieTitle(path, usefoldername=False):
    """
    Returns a clean movie title and year string if available.

    :param path: string or unicode - String to clean
    :param usefoldername: [opt] bool - use folder names (defaults to ``False``)

    example::

        title, year = xbmc.getCleanMovieTitle('/path/to/moviefolder/test.avi', True)
    """
    return tuple()


def getCondVisibility(condition):
    """
    Returns ``True`` (``1``) or ``False`` (``0``) as a ``bool``.

    :param condition: string - condition to check.

    List of Conditions: http://wiki.xbmc.org/?title=List_of_Boolean_Conditions

    .. note:: You can combine two (or more) of the above settings by using "+" as an ``AND`` operator,
        "|" as an ``OR`` operator, "!" as a ``NOT`` operator, and "[" and "]" to bracket expressions.

    example::

        visible = xbmc.getCondVisibility('[Control.IsVisible(41) + !Control.IsVisible(12)]')
    """
    return bool(1)


def getDVDState():
    """
    Returns the dvd state as an integer.

    return values are:

    - 1 : ``xbmc.DRIVE_NOT_READY``
    - 16 : ``xbmc.TRAY_OPEN``
    - 64 : ``xbmc.TRAY_CLOSED_NO_MEDIA``
    - 96 : ``xbmc.TRAY_CLOSED_MEDIA_PRESENT``

    example::

        dvdstate = xbmc.getDVDState()
    """
    return long()


def getFreeMem():
    """
    Returns the amount of free memory in MB as an integer.

    example::

        freemem = xbmc.getFreeMem()
    """
    return long()


def getGlobalIdleTime():
    """
    Returns the elapsed idle time in seconds as an integer.

    example::

        t = xbmc.getGlobalIdleTime()
    """
    return long()


def getIPAddress():
    """
    Returns the current ip address as a string.

    example::

        ip = xbmc.getIPAddress()
    """
    return str()


def getInfoImage(infotag):
    """
    Returns a filename including path to the InfoImage's thumbnail as a string.

    :param infotag: string - infotag for value you want returned.

    List of InfoTags: http://wiki.xbmc.org/?title=InfoLabels

    example::

        filename = xbmc.getInfoImage('Weather.Conditions')
    """
    return str()


def getInfoLabel(cLine):
    """
    Returns an InfoLabel as a string.

    :param cLine: string - infoTag for value you want returned.

    List of InfoTags: http://wiki.xbmc.org/?title=InfoLabels

    example::

        label = xbmc.getInfoLabel('Weather.Conditions')
    """
    return str()


def getLanguage(format=ENGLISH_NAME, region=False):
    """
    Returns the active language as a string.

    :param format: [opt] format of the returned language string

    - ``xbmc.ISO_639_1``: two letter code as defined in ISO 639-1
    - ``xbmc.ISO_639_2``: three letter code as defined in ISO 639-2/T or ISO 639-2/B
    - ``xbmc.ENGLISH_NAME``: full language name in English (default)

    :param region: [opt] append the region delimited by "-" of the language (setting)
        to the returned language string

    example::

        language = xbmc.getLanguage(xbmc.ENGLISH_NAME)
    """
    return str()


def getLocalizedString(id):
    """
    Returns a localized 'unicode string'.

    :param id: integer -- id# for string you want to localize.

    .. note:: See strings.po in language folders for which id you need for a string.

    example::

        locstr = xbmc.getLocalizedString(6)
    """
    return unicode()


def getRegion(id):
    """
    Returns your regions setting as a string for the specified id.

    :param id: string - id of setting to return

    .. note:: choices are (dateshort, datelong, time, meridiem, tempunit, speedunit)
        You can use the above as keywords for arguments.

    example::

        date_long_format = xbmc.getRegion('datelong')
    """
    return str()


def getSkinDir():
    """
    Returns the active skin directory as a string.

    .. note:: This is not the full path like ``'special://home/addons/skin.confluence'``,
        but only ``'skin.confluence'``.

    example::

        skindir = xbmc.getSkinDir()
    """
    return str()


def getSupportedMedia(mediaType):
    """
    Returns the supported file types for the specific media as a string.

    :param mediaType: string - media type

    .. note:: media type can be (video, music, picture).
        The return value is a pipe separated string of filetypes (eg. '.mov|.avi').

    You can use the above as keywords for arguments.

    example::

        mTypes = xbmc.getSupportedMedia('video')
    """
    return str()


def log(msg, level=LOGNOTICE):
    """
    Write a string to XBMC's log file and the debug window.

    :param msg: string - text to output.
    :param level: [opt] integer - log level to ouput at. (default=``LOGNOTICE``)

    .. note:: You can use the above as keywords for arguments and skip certain optional arguments.
        Once you use a keyword, all following arguments require the keyword.

    .. warning:: Starting from Kodi 16.0 (Jarvis) default level will be changed to ``LOGDEBUG``.

    Text is written to the log for the following conditions.

    - XBMC loglevel == -1 (NONE, nothing at all is logged)
    - XBMC loglevel == 0 (NORMAL, shows LOGNOTICE, LOGERROR, LOGSEVERE and LOGFATAL) * XBMC loglevel == 1
        (DEBUG, shows all)

    See pydocs for valid values for level.

    example::

        xbmc.log('This is a test string.', level=xbmc.LOGDEBUG)
    """
    pass


def makeLegalFilename(filename, fatX=True):
    """
    Returns a legal filename or path as a string.

    :param filename: string or unicode -- filename/path to make legal
    :param fatX: [opt] bool -- ``True`` = Xbox file system(Default)


    .. note: If fatX is ``True`` you should pass a full path.
        If fatX is ``False`` only pass the basename of the path.

    You can use the above as keywords for arguments and skip certain optional arguments.
    Once you use a keyword, all following arguments require the keyword.

    Example::

        filename = xbmc.makeLegalFilename('F: Age: The Meltdown.avi')
    """
    return str()


def playSFX(filename, useCached=True):
    """
    Plays a wav file by filename

    :param filename: string - filename of the wav file to play.
    :param useCached: [opt] bool - False = Dump any previously cached wav associated with filename

    example::

        xbmc.playSFX('special://xbmc/scripts/dingdong.wav')
        xbmc.playSFX('special://xbmc/scripts/dingdong.wav',False)
    """
    pass


def stopSFX():
    """
    Stops wav file

    example::

        xbmc.stopSFX()
    """
    pass


def restart():
    """
    Restart the htpc.

    example::

        xbmc.restart()
    """
    pass

def shutdown():
    """
    Shutdown the htpc.

    example::

        xbmc.shutdown()
    """
    pass


def skinHasImage(image):
    """
    Returns ``True`` if the image file exists in the skin.

    :param image: string - image filename

    .. note:: If the media resides in a subfolder include it.
        (eg. home-myfiles\home-myfiles2.png). You can use the above as keywords for arguments.

    example::

        exists = xbmc.skinHasImage('ButtonFocusedTexture.png')
    """
    return bool(1)


def sleep(timemillis):
    """
    Sleeps for 'time' msec.

    :param timemillis: integer - number of msec to sleep.

    .. note: This is useful if you have for example aPlayer class that is waiting
        for onPlayBackEnded() calls.

    :raises: TypeError, if time is not an integer.

    Example::

        xbmc.sleep(2000) # sleeps for 2 seconds
    """
    pass


def startServer(iTyp, bStart, bWait=False):
    """
    start or stop a server.

    :param iTyp: integer -- use SERVER_* constants
    :param bStart: bool -- start (True) or stop (False) a server
    :param bWait : [opt] bool -- wait on stop before returning (not supported by all servers)
    :return: bool -- ``True`` or ``False``


    Example::

        xbmc.startServer(xbmc.SERVER_AIRPLAYSERVER, False)
    """
    pass


def translatePath(path):
    """
    Returns the translated path.

    :param path: string or unicode - Path to format

    .. note: Only useful if you are coding for both Linux and Windows.

    Converts ``'special://masterprofile/script_data'`` -> ``'/home/user/XBMC/UserData/script_data'`` on Linux.

    Example::

        fpath = xbmc.translatePath('special://masterprofile/script_data')
    """
    return unicode()


def validatePath(path):
    """
    Returns the validated path.

    :param path: string or unicode - Path to format

    .. note:: Only useful if you are coding for both Linux and Windows for fixing slash problems.
        e.g. Corrects 'Z://something' -> 'Z:'

    Example::

        fpath = xbmc.validatePath(somepath)
    """
    return unicode()
