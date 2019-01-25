# coding: utf-8
# This file is generated from Kodi source code and post-edited
# to correct code style and docstrings formatting.
# License: GPL v.3 <https://www.gnu.org/licenses/gpl-3.0.en.html>
"""
General functions on Kodi

Offers classes and functions that provide
information about the media currently playing and that allow manipulation of
the media player (such as starting a new song). You can also find system
information using the functions available in this library.
"""
from typing import Union, List, Tuple

__kodistubs__ = True

int_type = Union[int, long]
str_type = Union[str, unicode]

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


class InfoTagMusic(object):
    """
    Kodi's music info tag class

    To get music info tag data of currently played source.

    Info tag load is only be possible from present player class.

    Example::

        tag = xbmc.Player().getMusicInfoTag()
        
        title = tag.getTitle()
        url   = tag.getURL()
    """
    
    def __init__(self):
        # type: () -> None
        pass
    
    def getDbId(self):
        # type: () -> int
        """
        Get identification number of tag in database

        :return: [integer] database id.

        New function added. 
        """
        return 0
    
    def getURL(self):
        # type: () -> str
        """
        Returns url of source as string from music info tag. 

        :return: [string] Url of source
        """
        return ""
    
    def getTitle(self):
        # type: () -> str
        """
        Returns the title from music as string on info tag. 

        :return: [string] Music title
        """
        return ""
    
    def getMediaType(self):
        # type: () -> str
        """
        Get the media type of the music item. 

        :return: [string] media type

        Available strings about media type for music:

        ======= ==============================
        String  Description                   
        ======= ==============================
        artist  If it is defined as an artist 
        album   If it is defined as an album  
        song    If it is defined as a song    
        ======= ==============================

        New function added. 
        """
        return ""
    
    def getArtist(self):
        # type: () -> str
        """
        Returns the artist from music as string if present. 

        :return: [string] Music artist
        """
        return ""
    
    def getAlbum(self):
        # type: () -> str
        """
        Returns the album from music tag as string if present. 

        :return: [string] Music album name
        """
        return ""
    
    def getAlbumArtist(self):
        # type: () -> str
        """
        Returns the album artist from music tag as string if present.

        :return: [string] Music album artist name
        """
        return ""
    
    def getGenre(self):
        # type: () -> str
        """
        Returns the genre name from music tag as string if present. 

        :return: [string] Genre name
        """
        return ""
    
    def getDuration(self):
        # type: () -> int
        """
        Returns the duration of music as integer from info tag. 

        :return: [integer] Duration
        """
        return 0
    
    def getRating(self):
        # type: () -> int
        """
        Returns the scraped rating as integer. 

        :return: [integer] Rating
        """
        return 0
    
    def getUserRating(self):
        # type: () -> int
        """
        Returns the user rating as integer (-1 if not existing) 

        :return: [integer] User rating
        """
        return 0
    
    def getTrack(self):
        # type: () -> int
        """
        Returns the track number (if present) from music info tag as integer. 

        :return: [integer] Track number
        """
        return 0
    
    def getDisc(self):
        # type: () -> int
        """
        Returns the disk number (if present) from music info tag as integer. 

        :return: [integer] Disc number
        """
        return 0
    
    def getReleaseDate(self):
        # type: () -> str
        """
        Returns the release date as string from music info tag (if present). 

        :return: [string] Release date
        """
        return ""
    
    def getListeners(self):
        # type: () -> int
        """
        Returns the listeners as integer from music info tag. 

        :return: [integer] Listeners
        """
        return 0
    
    def getPlayCount(self):
        # type: () -> int
        """
        Returns the number of carried out playbacks. 

        :return: [integer] Playback count
        """
        return 0
    
    def getLastPlayed(self):
        # type: () -> str
        """
        Returns last played time as string from music info tag. 

        :return: [string] Last played date / time on tag
        """
        return ""
    
    def getComment(self):
        # type: () -> str
        """
        Returns comment as string from music info tag. 

        :return: [string] Comment on tag
        """
        return ""
    
    def getLyrics(self):
        # type: () -> str
        """
        Returns a string from lyrics. 

        :return: [string] Lyrics on tag
        """
        return ""
    

class InfoTagRadioRDS(object):
    """
    Kodi's radio RDS info tag class

    To get radio RDS info tag data of currently played PVR radio channel source.

    Info tag load is only be possible from present player class.
    Also is all the data variable from radio channels and not known on beginning
    of radio receiving.

    Example::

        tag = xbmc.Player().getRadioRDSInfoTag()
        
        title  = tag.getTitle()
        artist = tag.getArtist()
    """
    
    def __init__(self):
        # type: () -> None
        pass
    
    def getTitle(self):
        # type: () -> str
        """
        Title of the item on the air; i.e. song title. 

        :return: Title 
        """
        return ""
    
    def getBand(self):
        # type: () -> str
        """
        Band of the item on air. 

        :return: Band 
        """
        return ""
    
    def getArtist(self):
        # type: () -> str
        """
        Artist of the item on air. 

        :return: Artist 
        """
        return ""
    
    def getComposer(self):
        # type: () -> str
        """
        Get the Composer of the music. 

        :return: Composer 
        """
        return ""
    
    def getConductor(self):
        # type: () -> str
        """
        Get the Conductor of the Band. 

        :return: Conductor 
        """
        return ""
    
    def getAlbum(self):
        # type: () -> str
        """
        Album of item on air. 

        :return: Album name 
        """
        return ""
    
    def getComment(self):
        # type: () -> str
        """
        Get Comment text from channel. 

        :return: Comment 
        """
        return ""
    
    def getAlbumTrackNumber(self):
        # type: () -> int
        """
        Get the album track number of currently sended music. 

        :return: Track Number 
        """
        return 0
    
    def getInfoNews(self):
        # type: () -> str
        """
        Get News informations. 

        :return: News Information 
        """
        return ""
    
    def getInfoNewsLocal(self):
        # type: () -> str
        """
        Get Local news informations. 

        :return: Local News Information 
        """
        return ""
    
    def getInfoSport(self):
        # type: () -> str
        """
        Get Sport informations. 

        :return: Sport Information 
        """
        return ""
    
    def getInfoStock(self):
        # type: () -> str
        """
        Get Stock informations. 

        :return: Stock Information 
        """
        return ""
    
    def getInfoWeather(self):
        # type: () -> str
        """
        Get Weather informations. 

        :return: Weather Information 
        """
        return ""
    
    def getInfoHoroscope(self):
        # type: () -> str
        """
        Get Horoscope informations. 

        :return: Horoscope Information 
        """
        return ""
    
    def getInfoCinema(self):
        # type: () -> str
        """
        Get Cinema informations. 

        :return: Cinema Information 
        """
        return ""
    
    def getInfoLottery(self):
        # type: () -> str
        """
        Get Lottery informations. 

        :return: Lottery Information 
        """
        return ""
    
    def getInfoOther(self):
        # type: () -> str
        """
        Get other informations. 

        :return: Other Information 
        """
        return ""
    
    def getEditorialStaff(self):
        # type: () -> str
        """
        Get Editorial Staff names. 

        :return: Editorial Staff 
        """
        return ""
    
    def getProgStation(self):
        # type: () -> str
        """
        Name describing station. 

        :return: Program Station 
        """
        return ""
    
    def getProgStyle(self):
        # type: () -> str
        """
        The the radio channel style currently used. 

        :return: Program Style 
        """
        return ""
    
    def getProgHost(self):
        # type: () -> str
        """
        Host of current radio show. 

        :return: Program Host 
        """
        return ""
    
    def getProgWebsite(self):
        # type: () -> str
        """
        Link to URL (web page) for radio station homepage. 

        :return: Program Website 
        """
        return ""
    
    def getProgNow(self):
        # type: () -> str
        """
        Current radio program show. 

        :return: Program Now 
        """
        return ""
    
    def getProgNext(self):
        # type: () -> str
        """
        Next program show. 

        :return: Program Next 
        """
        return ""
    
    def getPhoneHotline(self):
        # type: () -> str
        """
        Telephone number of the radio station's hotline. 

        :return: Phone Hotline 
        """
        return ""
    
    def getEMailHotline(self):
        # type: () -> str
        """
        Email address of the radio station's studio. 

        :return: EMail Hotline 
        """
        return ""
    
    def getPhoneStudio(self):
        # type: () -> str
        """
        Telephone number of the radio station's studio. 

        :return: Phone Studio 
        """
        return ""
    
    def getEMailStudio(self):
        # type: () -> str
        """
        Email address of radio station studio. 

        :return: EMail Studio 
        """
        return ""
    
    def getSMSStudio(self):
        # type: () -> str
        """
        SMS (Text Messaging) number for studio. 

        :return: SMS Studio 
        """
        return ""
    

class InfoTagVideo(object):
    """
    Kodi's video info tag class

    To get video info tag data of currently played source.

    Info tag load is only be possible from present player class.

    Example::

        tag = xbmc.Player().getVideoInfoTag()
        
        title = tag.getTitle()
        file  = tag.getFile()
    """
    
    def __init__(self):
        # type: () -> None
        pass
    
    def getDbId(self):
        # type: () -> int
        """
        Get identification number of tag in database 

        :return: [integer] database id

        New function added. 
        """
        return 0
    
    def getDirector(self):
        # type: () -> str
        """
        Get film director who has made the film (if present). 

        :return: [string] Film director name.
        """
        return ""
    
    def getWritingCredits(self):
        # type: () -> str
        """
        Get the writing credits if present from video info tag. 

        :return: [string] Writing credits
        """
        return ""
    
    def getGenre(self):
        # type: () -> str
        """
        To get the Video Genre if available. 

        :return: [string] Genre name
        """
        return ""
    
    def getTagLine(self):
        # type: () -> str
        """
        Get video tag line if available. 

        :return: [string] Video tag line
        """
        return ""
    
    def getPlotOutline(self):
        # type: () -> str
        """
        Get the outline plot of the video if present. 

        :return: [string] Outline plot
        """
        return ""
    
    def getPlot(self):
        # type: () -> str
        """
        Get the plot of the video if present. 

        :return: [string] Plot
        """
        return ""
    
    def getPictureURL(self):
        # type: () -> str
        """
        Get a picture URL of the video to show as screenshot. 

        :return: [string] Picture URL
        """
        return ""
    
    def getTitle(self):
        # type: () -> str
        """
        Get the video title. 

        :return: [string] Video title
        """
        return ""
    
    def getTVShowTitle(self):
        # type: () -> str
        """
        Get the video TV show title. 

        :return: [string] TV show title

        New function added. 
        """
        return ""
    
    def getMediaType(self):
        # type: () -> str
        """
        Get the media type of the video. 

        :return: [string] media type

        Available strings about media type for video:

        =========== =====================================
        String      Description                          
        =========== =====================================
        video       For normal video                     
        set         For a selection of video             
        musicvideo  To define it as music video          
        movie       To define it as normal movie         
        tvshow      If this is it defined as tvshow      
        season      The type is used as a series season  
        episode     The type is used as a series episode 
        =========== =====================================

        New function added. 
        """
        return ""
    
    def getVotes(self):
        # type: () -> str
        """
        Get the video votes if available from video info tag. 

        :return: [string] Votes
        """
        return ""
    
    def getCast(self):
        # type: () -> str
        """
        To get the cast of the video when available. 

        :return: [string] Video casts
        """
        return ""
    
    def getFile(self):
        # type: () -> str
        """
        To get the video file name. 

        :return: [string] File name
        """
        return ""
    
    def getPath(self):
        # type: () -> str
        """
        To get the path where the video is stored. 

        :return: [string] Path
        """
        return ""
    
    def getIMDBNumber(self):
        # type: () -> str
        """
        To get the IMDb number of the video (if present). 

        :return: [string] IMDb number
        """
        return ""
    
    def getSeason(self):
        # type: () -> int
        """
        To get season number of a series 

        :return: [integer] season number

        New function added. 
        """
        return 0
    
    def getEpisode(self):
        # type: () -> int
        """
        To get episode number of a series 

        :return: [integer] episode number

        New function added. 
        """
        return 0
    
    def getYear(self):
        # type: () -> int
        """
        Get production year of video if present. 

        :return: [integer] Production Year
        """
        return 0
    
    def getRating(self):
        # type: () -> float
        """
        Get the video rating if present as float (double where supported). 

        :return: [float] The rating of the video
        """
        return 0.0
    
    def getUserRating(self):
        # type: () -> int
        """
        Get the user rating if present as integer. 

        :return: [integer] The user rating of the video
        """
        return 0
    
    def getPlayCount(self):
        # type: () -> int
        """
        To get the number of plays of the video. 

        :return: [integer] Play Count
        """
        return 0
    
    def getLastPlayed(self):
        # type: () -> str
        """
        Get the last played date / time as string. 

        :return: [string] Last played date / time
        """
        return ""
    
    def getOriginalTitle(self):
        # type: () -> str
        """
        To get the original title of the video. 

        :return: [string] Original title
        """
        return ""
    
    def getPremiered(self):
        # type: () -> str
        """
        To get premiered date of the video, if available. 

        :return: [string]
        """
        return ""
    
    def getFirstAired(self):
        # type: () -> str
        """
        Returns first aired date as string from info tag. 

        :return: [string] First aired date
        """
        return ""
    
    def getTrailer(self):
        # type: () -> str
        """
        To get the path where the trailer is stored. 

        :return: [string] Trailer path

        New function added. 
        """
        return ""
    
    def getArtist(self):
        # type: () -> List[str]
        """
        To get the artist name (for musicvideos) 

        :return: List[str] Artist name

        New function added. 
        """
        return [""]
    
    def getAlbum(self):
        # type: () -> str
        """
        To get the album name (for musicvideos) 

        :return: [string] Album name

        New function added. 
        """
        return ""
    
    def getTrack(self):
        # type: () -> int
        """
        To get the track number (for musicvideos) 

        :return: [int] Track number

        New function added. 
        """
        return 0
    
    def getDuration(self):
        # type: () -> int
        """
        To get the duration 

        :return: [unsigned int] Duration

        New function added. 
        """
        return 0
    

class Keyboard(object):
    """
    Kodi's keyboard class

    Creates a new Keyboard object with default text heading and hidden input
    flag if supplied.

    :param default: : [opt] string - default text entry. 
    :param heading: : [opt] string - keyboard heading. 
    :param hidden: : [opt] boolean - True for hidden text entry.

    Example::

        kb = xbmc.Keyboard('default', 'heading', True)
        kb.setDefault('password') # optional
        kb.setHeading('Enter password') # optional
        kb.setHiddenInput(True) # optional
        kb.doModal()
        if kb.isConfirmed():
            text = kb.getText()
    """
    
    def __init__(self, line="", heading="", hidden=False):
        # type: (str_type, str_type, bool) -> None
        pass
    
    def doModal(self, autoclose=0):
        # type: (int) -> None
        """
        Show keyboard and wait for user action. 

        :param autoclose: [opt] integer - milliseconds to autoclose dialog.
            default=do not autoclose)

        Example::

            kb.doModal(30000)
        """
        pass
    
    def setDefault(self, line=""):
        # type: (str_type) -> None
        """
        Set the default text entry. 

        :param line: string - default text entry.

        Example::

            kb.setDefault('password')
        """
        pass
    
    def setHiddenInput(self, hidden=False):
        # type: (bool) -> None
        """
        Allows hidden text entry. 

        :param hidden: boolean - True for hidden text entry.

        Example::

            kb.setHiddenInput(True)
        """
        pass
    
    def setHeading(self, heading):
        # type: (str_type) -> None
        """
        Set the keyboard heading. 

        :param heading: string - keyboard heading.

        Example::

            kb.setHeading('Enter password')
        """
        pass
    
    def getText(self):
        # type: () -> str
        """
        Returns the user input as a string. 

        This will always return the text entry even if you cancel the keyboard.
        Use the isConfirmed() method to check if user cancelled the keyboard.

        :return: get the in keyboard entered text

        Example::

            text = kb.getText()
        """
        return ""
    
    def isConfirmed(self):
        # type: () -> bool
        """
        Returns False if the user cancelled the input. 

        :return: true if confirmed, if cancelled false 

        Example::

            if kb.isConfirmed():
                ...
        """
        return True
    

class Monitor(object):
    """
    Kodi's monitor class

    Creates a new monitor to notify addon about changes.
    """
    
    def __init__(self):
        # type: () -> None
        pass
    
    def onSettingsChanged(self):
        # type: () -> None
        """
        onSettingsChanged method. 

        Will be called when addon settings are changed 
        """
        pass
    
    def onScreensaverActivated(self):
        # type: () -> None
        """
        onScreensaverActivated method. 

        Will be called when screensaver kicks in 
        """
        pass
    
    def onScreensaverDeactivated(self):
        # type: () -> None
        """
        onScreensaverDeactivated method. 

        Will be called when screensaver goes off 
        """
        pass
    
    def onDPMSActivated(self):
        # type: () -> None
        """
        onDPMSActivated method. 

        Will be called when energysaving/DPMS gets active 
        """
        pass
    
    def onDPMSDeactivated(self):
        # type: () -> None
        """
        onDPMSDeactivated method. 

        Will be called when energysaving/DPMS is turned off 
        """
        pass
    
    def onScanStarted(self, library):
        # type: (str_type) -> None
        """
        onScanStarted method. 

        :param library: Video / music as string

        Will be called when library clean has ended and return video or music
        to indicate which library is being scanned

        New function added.
        """
        pass
    
    def onScanFinished(self, library):
        # type: (str_type) -> None
        """
        onScanFinished method. 

        :param library: Video / music as string

        Will be called when library clean has ended and return video or music
        to indicate which library has been scanned

        New function added.
        """
        pass
    
    def onDatabaseScanStarted(self, database):
        # type: (str_type) -> None
        """
        .. warning:: Deprecated. Use **onScanStarted()**.
        """
        pass
    
    def onDatabaseUpdated(self, database):
        # type: (str_type) -> None
        """
        .. warning:: Deprecated. Use **onScanFinished()**.
        """
        pass
    
    def onCleanStarted(self, library):
        # type: (str_type) -> None
        """
        onCleanStarted method.

        :param library: Video / music as string

        Will be called when library clean has ended and return video or music
        to indicate which library has been cleaned

        New function added.
        """
        pass
    
    def onCleanFinished(self, library):
        # type: (str_type) -> None
        """
        onCleanFinished method. 

        :param library: Video / music as string

        Will be called when library clean has ended and return video or music
        to indicate which library has been finished

        New function added.
        """
        pass
    
    def onAbortRequested(self):
        # type: () -> None
        """
        .. warning::
            Deprecated. Use **waitForAbort()** to be notified about this event.
        """
        pass
    
    def onNotification(self, sender, method, data):
        # type: (str_type, str_type, str_type) -> None
        """
        onNotification method. 

        :param sender: Sender of the notification 
        :param method: Name of the notification 
        :param data: JSON-encoded data of the notification

        Will be called when Kodi receives or sends a notification

        New function added.
        """
        pass
    
    def waitForAbort(self, timeout=-1):
        # type: (float) -> bool
        """
        Wait for Abort 

        Block until abort is requested, or until timeout occurs. If an abort
        requested have already been made, return immediately.

        :param timeout: [opt] float - timeout in seconds. Default: no timeout.
        :return: True when abort have been requested,
            False if a timeout is given and the operation times out.

        New function added. 
        """
        return True
    
    def abortRequested(self):
        # type: () -> bool
        """
        Returns True if abort has been requested. 

        :return: True if requested

        New function added. 
        """
        return True
    

class Player(object):
    """
    Kodi's player

    To become and create the class to play something.

    Example::

        xbmc.Player().play(url, listitem, windowed)
    """
    
    def __init__(self, playerCore=0):
        # type: (int) -> None
        pass
    
    def play(self, item="", listitem=None, windowed=False, startpos=-1):
        # type: (Union[str_type, PlayList], 'xbmcgui.ListItem', bool, int) -> None
        """
        Play a item.

        :param item: [opt] string - filename, url or playlist 
        :param listitem: [opt] listitem - used with setInfo() to set different
            infolabels.
        :param windowed: [opt] bool - true=play video windowed,
            false=play users preference.(default)
        :param startpos: [opt] int - starting position when playing a playlist.
            Default = -1

        If item is not given then the Player will try to play the current item
        in the current playlist. You can use the above as keywords for arguments
        and skip certain optional arguments. Once you use a keyword,
        all following arguments require the keyword.

        Example::

            listitem = xbmcgui.ListItem('Ironman')
            listitem.setInfo('video', {'Title': 'Ironman', 'Genre': 'Science Fiction'})
            xbmc.Player().play(url, listitem, windowed)
            xbmc.Player().play(playlist, listitem, windowed, startpos)
        """
        pass
    
    def stop(self):
        # type: () -> None
        """
        Stop playing. 
        """
        pass
    
    def pause(self):
        # type: () -> None
        """
        Pause or resume playing if already paused. 
        """
        pass
    
    def playnext(self):
        # type: () -> None
        """
        Play next item in playlist. 
        """
        pass
    
    def playprevious(self):
        # type: () -> None
        """
        Play previous item in playlist. 
        """
        pass
    
    def playselected(self, selected):
        # type: (int) -> None
        """
        Play a certain item from the current playlist. 

        :param selected: Integer - Item to select 
        """
        pass
    
    def isPlaying(self):
        # type: () -> bool
        """
        Check Kodi is playing something. 

        :return: True if Kodi is playing a file. 
        """
        return True
    
    def isPlayingAudio(self):
        # type: () -> bool
        """
        Check for playing audio. 

        :return: True if Kodi is playing an audio file. 
        """
        return True
    
    def isPlayingVideo(self):
        # type: () -> bool
        """
        Check for playing video. 

        :return: True if Kodi is playing a video. 
        """
        return True
    
    def isPlayingRDS(self):
        # type: () -> bool
        """
        Check for playing radio data system (RDS). 

        :return: True if kodi is playing a radio data system (RDS). 
        """
        return True
    
    def isExternalPlayer(self):
        # type: () -> bool
        """
        Check for external player. 

        :return: True if kodi is playing using an external player.

        New function added. 
        """
        return True
    
    def getPlayingFile(self):
        # type: () -> str
        """
        Returns the current playing file as a string. 

        For LiveTV, returns a ``pvr://`` url which is not translatable to
        an OS specific file or external url.

        :return: Playing filename
        :raises Exception: If player is not playing a file. 
        """
        return ""
    
    def getTime(self):
        # type: () -> float
        """
        Get playing time. 

        Returns the current time of the current playing media as fractional seconds.

        :return: Current time as fractional seconds
        :raises Exception: If player is not playing a file. 
        """
        return 0.0
    
    def seekTime(self, seekTime):
        # type: (float) -> None
        """
        Seek time. 

        Seeks the specified amount of time as fractional seconds. The time
        specified is relative to the beginning of the currently
        playing media file.

        :param seekTime: Time to seek as fractional seconds 
        :raises Exception: If player is not playing a file. 
        """
        pass
    
    def setSubtitles(self, subtitleFile):
        # type: (str) -> None
        """
        Set subtitle file and enable subtitles. 

        :param subtitleFile: File to use as source of subtitles
        """
        pass
    
    def showSubtitles(self, bVisible):
        # type: (bool) -> None
        """
        Enable / disable subtitles. 

        :param visible: [boolean] True for visible subtitles.

        Example::

            xbmc.Player().showSubtitles(True)
        """
        pass
    
    def getSubtitles(self):
        # type: () -> str
        """
        Get subtitle stream name. 

        :return: Stream name 
        """
        return ""
    
    def getAvailableSubtitleStreams(self):
        # type: () -> List[str]
        """
        Get Subtitle stream names. 

        :return: List of subtitle streams as name 
        """
        return [""]
    
    def setSubtitleStream(self, iStream):
        # type: (int) -> None
        """
        Set Subtitle Stream. 

        :param iStream: [int] Subtitle stream to select for play

        Example::

            xbmc.Player().setSubtitleStream(1)
        """
        pass
    
    def updateInfoTag(self, item):
        # type: ('xbmcgui.ListItem') -> None
        """
        Update info labels for currently playing item. 

        :param item: ListItem with new info
        :raises Exception: If player is not playing a file

        New function added.

        Example::

            item = xbmcgui.ListItem()
            item.setPath(xbmc.Player().getPlayingFile())
            item.setInfo('music', {'title' : 'foo', 'artist' : 'bar'})
            xbmc.Player().updateInfoTag(item)
        """
        pass
    
    def getVideoInfoTag(self):
        # type: () -> InfoTagVideo
        """
        To get video info tag. 

        Returns the VideoInfoTag of the current playing Movie.

        :return: Video info tag
        :raises Exception: If player is not playing a file or current file
            is not a movie file.
        """
        return InfoTagVideo()
    
    def getMusicInfoTag(self):
        # type: () -> InfoTagMusic
        """
        To get music info tag. 

        Returns the MusicInfoTag of the current playing 'Song'.

        :return: Music info tag
        :raises Exception: If player is not playing a file or current file
            is not a music file.
        """
        return InfoTagMusic()
    
    def getRadioRDSInfoTag(self):
        # type: () -> InfoTagRadioRDS
        """
        To get Radio RDS info tag 

        Returns the RadioRDSInfoTag of the current playing 'Radio Song if. present'.

        :return: Radio RDS info tag
        :raises Exception: If player is not playing a file or current file
            is not a rds file.
        """
        return InfoTagRadioRDS()
    
    def getTotalTime(self):
        # type: () -> float
        """
        To get total playing time. 

        Returns the total time of the current playing media in seconds.
        This is only accurate to the full second.

        :return: Total time of the current playing media
        :raises Exception: If player is not playing a file. 
        """
        return 0.0
    
    def getAvailableAudioStreams(self):
        # type: () -> List[str]
        """
        Get Audio stream names 

        :return: List of audio streams as name 
        """
        return [""]
    
    def setAudioStream(self, iStream):
        # type: (int) -> None
        """
        Set Audio Stream. 

        :param iStream: [int] Audio stream to select for play

        Example::

            xbmc.Player().setAudioStream(1)
        """
        pass
    
    def getAvailableVideoStreams(self):
        # type: () -> List[str]
        """
        Get Video stream names 

        :return: List of video streams as name 
        """
        return [""]
    
    def setVideoStream(self, iStream):
        # type: (int) -> None
        """
        Set Video Stream. 

        :param iStream: [int] Video stream to select for play

        Example::

            xbmc.Player().setVideoStream(1)
        """
        pass

    def onPlayBackStarted(self):
        # type: () -> None
        """
        onPlayBackStarted method.

        Will be called when Kodi player starts. Video or audio might not be
        available at this point. Use onAVStarted() instead if you need to detect
        if Kodi is actually playing a media file (i.e, if a stream is available)
        """
        pass

    def onAVStarted(self):
        # type: () -> None
        """
        onAVStarted method.

        Will be called when Kodi has a video or audiostream.

        New function added.
        """
        pass

    def onAVChange(self):
        # type: () -> None
        """
        onAVChange method.

        Will be called when Kodi has a video, audio or subtitle stream.
        Also happens when the stream changes.

        New function added.
        """
        pass

    def onPlayBackEnded(self):
        # type: () -> None
        """
        onPlayBackEnded method.

        Will be called when Kodi stops playing a file.
        """
        pass

    def onPlayBackStopped(self):
        # type: () -> None
        """
        onPlayBackStopped method.

        Will be called when user stops Kodi playing a file.
        """
        pass

    def onPlayBackError(self):
        # type: () -> None
        """
        onPlayBackError method.

        Will be called when playback stops due to an error.
        """
        pass

    def onPlayBackPaused(self):
        # type: () -> None
        """
        onPlayBackPaused method.

        Will be called when user pauses a playing file.
        """
        pass

    def onPlayBackResumed(self):
        # type: () -> None
        """
        onPlayBackResumed method.

        Will be called when user resumes a paused file.
        """
        pass

    def onQueueNextItem(self):
        # type: () -> None
        """
        onQueueNextItem method.

        Will be called when user queues the next item.
        """
        pass

    def onPlayBackSpeedChanged(self, speed):
        # type: (int) -> None
        """
        onPlayBackSpeedChanged method.

        Will be called when players speed changes (eg. user FF/RW).

        :param speed: [integer] Current speed of player

        Negative speed means player is rewinding, 1 is normal playback speed.
        """
        pass

    def onPlayBackSeek(self, time, seekOffset):
        # type: (int, int) -> None
        """
        onPlayBackSeek method.

        Will be called when user seeks to a time.

        :param time: [integer] Time to seek to
        :param seekOffset: [integer] ?
        """
        pass

    def onPlayBackSeekChapter(self, chapter):
        # type: (int) -> None
        """
        onPlayBackSeekChapter method.

        Will be called when user performs a chapter seek.

        :param chapter: [integer] Chapter to seek to
        """
        pass


class PlayList(object):
    """
    Kodi's Play List class.


    To create and edit a playlist which can be handled by the player.

    :param playList: [integer] To define the stream type

    ====== ==================== ====================================
    Value  Integer String       Description                         
    ====== ==================== ====================================
    0      xbmc.PLAYLIST_MUSIC  Playlist for music files or streams 
    1      xbmc.PLAYLIST_VIDEO  Playlist for video files or streams 
    ====== ==================== ====================================

    Example::

        play=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    """
    
    def __init__(self, playList):
        # type: (int) -> None
        pass
    
    def getPlayListId(self):
        # f() -> int
        """
        Get the PlayList Identifier 

        :return: Id as an integer. 
        """
        return 0
    
    def add(self, url, listitem=None, index=-1):
        # type: (str_type, 'xbmcgui.ListItem', int) -> None
        """
        Adds a new file to the playlist. 

        :param url: string or unicode - filename or url to add. 
        :param listitem: [opt] listitem - used with setInfo() to set different
            infolabels.
        :param index: [opt] integer - position to add playlist item. (default=end)

        You can use the above as keywords for arguments and skip certain optional
        arguments. Once you use a keyword, all following arguments require
        the keyword.

        Example::

            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            video = 'F:\\movies\\Ironman.mov'
            listitem = xbmcgui.ListItem('Ironman', thumbnailImage='F:\\movies\\Ironman.tbn')
            listitem.setInfo('video', {'Title': 'Ironman', 'Genre': 'Science Fiction'})
            playlist.add(url=video, listitem=listitem, index=7)n
        """
        pass
    
    def load(self, filename):
        # type: (str) -> bool
        """
        Load a playlist. 

        Clear current playlist and copy items from the file to this Playlist
        filename can be like .pls or .m3u

        :param filename: File with list to play inside 
        :return: False if unable to load playlist 
        """
        return True
    
    def remove(self, filename):
        # type: (str) -> None
        """
        Remove an item with this filename from the playlist. 

        :param filename: The file to remove from list. 
        """
        pass
    
    def clear(self):
        # type: () -> None
        """
        Clear all items in the playlist. 
        """
        pass
    
    def size(self):
        # type: () -> int
        """
        Returns the total number of PlayListItems in this playlist. 

        :return: Amount of playlist entries. 
        """
        return 0
    
    def shuffle(self):
        # type: () -> None
        """
        Shuffle the playlist. 
        """
        pass
    
    def unshuffle(self):
        # type: () -> None
        """
        Unshuffle the playlist. 
        """
        pass
    
    def getposition(self):
        # type: () -> int
        """
        Returns the position of the current song in this playlist. 

        :return: Position of the current song 
        """
        return 0
    

class RenderCapture(object):
    """
    Kodi's render capture.
    """
    
    def __init__(self):
        # type: () -> None
        pass
    
    def getWidth(self):
        # type: () -> int
        """
        Get width 

        To get width of captured image as set during RenderCapture.capture().
        Returns 0 prior to calling capture.

        :return: Width or 0 prior to calling capture 
        """
        return 0
    
    def getHeight(self):
        # type: () -> int
        """
        Get height 

        To get height of captured image as set during RenderCapture.capture().
        Returns 0 prior to calling capture.

        :return: height or 0 prior to calling capture 
        """
        return 0
    
    def getAspectRatio(self):
        # type: () -> float
        """
        Get aspect ratio of currently displayed video. 

        :return: Aspect ratio 

        This may be called prior to calling RenderCapture.capture(). 
        """
        return 0.0
    
    def getImageFormat(self):
        # type: () -> str
        """
        Get image format 

        :return: Format of captured image: 'BGRA'

        Image will now always be returned in BGRA 
        """
        return ""
    
    def getImage(self, msecs=0):
        # type: (int) -> bytearray
        """
        Returns captured image as a bytearray. 

        :param msecs: [opt] Milliseconds to wait. Waits 1000ms if not specified 
        :return: Captured image as a bytearray

        The size of the image is m_width * m_height * 4

        Added the option to specify wait time in msec. 
        """
        return bytearray()
    
    def capture(self, width, height):
        # type: (int, int) -> None
        """
        Issue capture request. 

        :param width: Width capture image should be rendered to 
        :param height: Height capture image should should be rendered to

        Removed the option to pass **flags**
        """
        pass


def log(msg, level=LOGDEBUG):
    # type: (str, int) -> None
    """
    Write a string to Kodi's log file and the debug window. 

    :param msg: string - text to output. 
    :param level: [opt] integer - log level to output at. (default=LOGDEBUG)

    ================ ===========================================================
    Value:           Description:
    ================ ===========================================================
    xbmc.LOGDEBUG    In depth information about the status of Kodi.
                     This information can pretty much only be deciphered by
                     a developer or long time Kodi power user.
    xbmc.LOGINFO     Something has happened. It's not a problem, we just thought
                     you might want to know. Fairly excessive output that most
                     people won't care about.
    xbmc.LOGNOTICE   Similar to INFO but the average Joe might want to know
                     about these events. This level and above are logged by
                     default.
    xbmc.LOGWARNING  Something potentially bad has happened. If Kodi did
                     something you didn't expect, this is probably why.
                     Watch for errors to follow.
    xbmc.LOGERROR    This event is bad. Something has failed. You likely noticed
                     problems with the application be it skin artifacts, failure
                     of playback a crash, etc.
    xbmc.LOGFATAL    We're screwed. Kodi is about to crash.
    ================ ===========================================================

    You can use the above as keywords for arguments and skip certain optional
    arguments. Once you use a keyword, all following arguments require
    the keyword.

    Text is written to the log for the following conditions.loglevel == -1
    (NONE, nothing at all is logged)

    loglevel == 0 (NORMAL, shows LOGNOTICE, LOGERROR, LOGSEVERE and LOGFATAL)

    loglevel == 1 (DEBUG, shows all) See pydocs for valid values for level.

    Default level changed from LOGNOTICE to LOGDEBUG

    Example::

        xbmc.log(msg='This is a test string.', level=xbmc.LOGDEBUG);
    """
    pass


def shutdown():
    # type: () -> None
    """
    Shutdown the htpc. 

    Example::

        xbmc.shutdown()
    """
    pass


def restart():
    # type: () -> None
    """
    Restart the htpc. 

    Example::

        xbmc.restart()
    """
    pass


def executescript(script):
    # type: (str) -> None
    """
    Execute a python script. 

    :param script: string - script filename to execute.

    Example::

        xbmc.executescript('special://home/scripts/update.py')
    """
    pass


def executebuiltin(function, wait=False):
    # type: (str, bool) -> None
    """
    Execute a built in Kodi function. 

    :param function: string - builtin function to execute.

    List of functions - <http://kodi.wiki/view/List_of_Built_In_Functions>

    Example::

        xbmc.executebuiltin('Skin.SetString(abc,def)')
    """
    pass


def executeJSONRPC(jsonrpccommand):
    # type: (str) -> str
    """
    Execute an JSONRPC command. 

    :param jsonrpccommand: string - jsonrpc command to execute. 
    :return: jsonrpc return string

    List of commands - <https://kodi.wiki/view/JSON-RPC_API/v9>

    Example::

        response = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "JSONRPC.Introspect", "id": 1 }')
    """
    return ""


def sleep(timemillis):
    # type: (int_type) -> None
    """
    Sleeps for 'time' msec. 

    :param time: integer - number of msec to sleep.
    :raises TypeError: If time is not an integer.

    This is useful if you have for example a Player class that is waiting for
    onPlayBackEnded() calls.

    Example::

        xbmc.sleep(2000) # sleeps for 2 seconds
    """
    pass


def getLocalizedString(id):
    # type: (int) -> unicode
    """
    Get a localized 'unicode string'. 

    :param id: integer - id# for string you want to localize. 
    :return: Localized 'unicode string'

    See strings.xml in  ``\language\{yourlanguage}\``
    for which id you need for a string.

    Example::

        locstr = xbmc.getLocalizedString(6)
    """
    return u""


def getSkinDir():
    # type: () -> str
    """
    Get the active skin directory. 

    :return: The active skin directory as a string

    This is not the full path like 'special://home/addons/MediaCenter', but
    only 'MediaCenter'.

    Example::

        skindir = xbmc.getSkinDir()
    """
    return ""


def getLanguage(format=ENGLISH_NAME, region=False):
    # type: (int, bool) -> str
    """
    Get the active language. 

    :param format: [opt] format of the returned language string

    ================== ===========================================================
    Value              Description                                                
    ================== ===========================================================
    xbmc.ISO_639_1     Two letter code as defined in ISO 639-1                    
    xbmc.ISO_639_2     Three letter code as defined in ISO 639-2/T or ISO 639-2/B 
    xbmc.ENGLISH_NAME  Full language name in English (default)                    
    ================== ===========================================================

    :param region: [opt] append the region delimited by "-" of the language
        (setting) to the returned language string
    :return: The active language as a string

    Added new options **format** and **region**.

    Example::

        language = xbmc.getLanguage(xbmc.ENGLISH_NAME)
    """
    return ""


def getIPAddress():
    # type: () -> str
    """
    Get the current ip address. 

    :return: The current ip address as a string

    Example::

        ip = xbmc.getIPAddress()
    """
    return ""


def getDVDState():
    # type: () -> long
    """
    Returns the dvd state as an integer. 

    :return: Values for state are:

    ====== ===============================
    Value  Name                           
    ====== ===============================
    1      xbmc.DRIVE_NOT_READY           
    16     xbmc.TRAY_OPEN                 
    64     xbmc.TRAY_CLOSED_NO_MEDIA      
    96     xbmc.TRAY_CLOSED_MEDIA_PRESENT 
    ====== ===============================

    Example::

        dvdstate = xbmc.getDVDState()
    """
    return 0L


def getFreeMem():
    # type: () -> long
    """
    Get amount of free memory in MB. 

    :return: The amount of free memory in MB as an integer

    Example::

        freemem = xbmc.getFreeMem()
    """
    return 0L


def getInfoLabel(cLine):
    # type: (str) -> str
    """
    Get a info label 

    :param infotag: string - infoTag for value you want returned. 
    :return: InfoLabel as a string

    List of InfoTags -- <http://kodi.wiki/view/InfoLabels>

    Example::

        label = xbmc.getInfoLabel('Weather.Conditions')
    """
    return ""


def getInfoImage(infotag):
    # type: (str) -> str
    """
    Get filename including path to the InfoImage's thumbnail. 

    :param infotag: string - infotag for value you want returned 
    :return: Filename including path to the InfoImage's thumbnail as a string

    List of InfoTags -- <http://kodi.wiki/view/InfoLabels>

    Example::

        filename = xbmc.getInfoImage('Weather.Conditions')
    """
    return ""


def playSFX(filename, useCached=True):
    # type: (str, bool) -> None
    """
    Plays a wav file by filename 

    :param filename: string - filename of the wav file to play 
    :param useCached: [opt] bool - False = Dump any previously cached
        wav associated with filename

    Added new option **useCached**.

    Example::

        xbmc.playSFX('special://xbmc/scripts/dingdong.wav')
        xbmc.playSFX('special://xbmc/scripts/dingdong.wav',False)
    """
    pass


def stopSFX():
    # type: () -> None
    """
    Stops wav file 

    New function added.

    Example::

        xbmc.stopSFX()
    """
    pass


def enableNavSounds(yesNo):
    # type: (bool) -> None
    """
    Enables/Disables nav sounds 

    :param yesNo: integer - enable (True) or disable (False) nav sounds

    Example::

        xbmc.enableNavSounds(True)
    """
    pass


def getCondVisibility(condition):
    # type: (str) -> bool
    """
    Get visibility conditions 

    :param condition: string - condition to check 
    :return: True (1) or False (0) as a bool

    List of Conditions -- <http://kodi.wiki/view/List_of_Boolean_Conditions>

    You can combine two (or more) of the above settings by using **"+"**
    as an AND operator, **"|"** as an OR operator, **"!"** as a NOT operator,
    and **"["** and **"]"** to bracket expressions.

    Example::

        visible = xbmc.getCondVisibility('[Control.IsVisible(41) + !Control.IsVisible(12)]')
    """
    return True


def getGlobalIdleTime():
    # type: () -> int
    """
    Get the elapsed idle time in seconds. 

    :return: Elapsed idle time in seconds as an integer

    Example::

        t = xbmc.getGlobalIdleTime()
    """
    return 0


def getCacheThumbName(path):
    # type: (str_type) -> str
    """
    Get thumb cache filename. 

    :param path: string or unicode - path to file 
    :return: Thumb cache filename

    Example::

        thumb = xbmc.getCacheThumbName('f:\\videos\\movie.avi')
    """
    return ""


def makeLegalFilename(filename, fatX=True):
    # type: (str_type, bool) -> str
    """
    Returns a legal filename or path as a string.

    :param filename: string or unicode - filename/path to make legal 
    :param fatX: [opt] bool - True=Xbox file system(Default) 
    :return: Legal filename or path as a string

    If fatX is true you should pass a full path. If fatX is false only pass
    the basename of the path. You can use the above as keywords for arguments
    and skip certain optional arguments. Once you use a keyword, all following
    arguments require the keyword.

    Example::

        filename = xbmc.makeLegalFilename('F:\\Trailers\\Ice Age: The Meltdown.avi')
    """
    return ""


def translatePath(path):
    # type: (str_type) -> str
    """
    Returns the translated path. 

    :param path: string or unicode - Path to format 
    :return: Translated path

    Only useful if you are coding for both Linux and Windows. e.g.
    converts ``'special://masterprofile/script_data'`` ->
    ``'/home/user/XBMC/UserData/script_data'`` on Linux.

    Example::

        fpath = xbmc.translatePath('special://masterprofile/script_data')
    """
    return ""


def getCleanMovieTitle(path, usefoldername=False):
    # type: (str_type, bool) -> Tuple[str, str]
    """
    Get clean movie title and year string if available. 

    :param path: string or unicode - String to clean 
    :param usefoldername: [opt] bool - use folder names (defaults to false) 
    :return: Clean movie title and year string if available.

    Example::

        title, year = xbmc.getCleanMovieTitle('/path/to/moviefolder/test.avi', True)
    """
    return "", ""


def validatePath(path):
    # type: (str_type) -> str
    """
    Returns the validated path. 

    :param path: string or unicode - Path to format 
    :return: Validated path

    Only useful if you are coding for both Linux and Windows for fixing slash
    problems. e.g. Corrects ``'Z://something'`` -> ``'Z:'``

    Example::

        fpath = xbmc.validatePath(somepath)
    """
    return ""


def getRegion(id):
    # type: (str) -> str
    """
    Returns your regions setting as a string for the specified id. 

    :param id: string - id of setting to return 
    :return: Region setting

    choices are (dateshort, datelong, time, meridiem, tempunit, speedunit)
    You can use the above as keywords for arguments.

    Example::

        date_long_format = xbmc.getRegion('datelong')
    """
    return ""


def getSupportedMedia(mediaType):
    # type: (str) -> str
    """
    Get the supported file types for the specific media. 

    :param media: string - media type 
    :return: Supported file types for the specific media as a string

    Media type can be (video, music, picture). The return value is a pipe
    separated string of filetypes (eg. '.mov|.avi'). You can use the above
    as keywords for arguments.

    Example::

        mTypes = xbmc.getSupportedMedia('video')
    """
    return ""


def skinHasImage(image):
    # type: (str) -> bool
    """
    Check skin for presence of Image. 

    :param image: string - image filename 
    :return: True if the image file exists in the skin

    If the media resides in a subfolder include it.
    (eg. home-myfiles\home-myfiles2.png). You can use the above as keywords
    for arguments.

    Example::

        exists = xbmc.skinHasImage('ButtonFocusedTexture.png')
    """
    return True


def startServer(iTyp, bStart, bWait=False):
    # type: (int, bool, bool) -> bool
    """
    Start or stop a server. 

    :param typ: integer - use SERVER_* constantsUsed format of the returned
        language string

    ========================== =================================================
    Value                      Description                                                           
    ========================== =================================================
    xbmc.SERVER_WEBSERVER      To control Kodi's builtin webserver                                    
    xbmc.SERVER_AIRPLAYSERVER  AirPlay is a proprietary protocol stack/suite
                               developed by Apple Inc.
    xbmc.SERVER_JSONRPCSERVER  Control JSON-RPC HTTP/TCP socket-based interface                       
    xbmc.SERVER_UPNPRENDERER   UPnP client (aka UPnP renderer)                                        
    xbmc.SERVER_UPNPSERVER     Control built-in UPnP A/V media server
                               (UPnP-server)
    xbmc.SERVER_EVENTSERVER    Set eventServer part that accepts remote device
                               input on all platforms
    xbmc.SERVER_ZEROCONF       Control Kodi's Avahi Zeroconf                                          
    ========================== =================================================

    :param bStart: bool - start (True) or stop (False) a server 
    :param bWait: [opt] bool - wait on stop before returning
        (not supported by all servers)
    :return: bool - True or False

    Example::

        xbmc.startServer(xbmc.SERVER_AIRPLAYSERVER, False)
    """
    return True


def audioSuspend():
    # type: () -> None
    """
    Suspend Audio engine. 

    Example::

        xbmc.audioSuspend()
    """
    pass


def audioResume():
    # type: () -> None
    """
    Resume Audio engine. 

    Example::

        xbmc.audioResume()
    """
    pass


def getUserAgent():
    # type: () -> str
    """
    Returns Kodi's HTTP UserAgent string

    :return: HTTP user agent

    Example::

        xbmc.getUserAgent()

    example output:
    ``'Kodi/17.0-ALPHA1 (X11; Linux x86_64) Ubuntu/15.10 App_Bitness/64 Version/17.0-ALPHA1-Git:2015-12-23-5770d28'``
    """
    return ""


def convertLanguage(language, format):
    # type: (str, int) -> str
    """
    Returns the given language converted to the given format as a string.

    :param language: string either as name in English, two letter code
        (ISO 639-1), or three letter code (ISO 639-2/T(B)
    :param format: format of the returned language string

    ================== ==========================================================
    Value              Description
    ================== ==========================================================
    xbmc.ISO_639_1     Two letter code as defined in ISO 639-1                    
    xbmc.ISO_639_2     Three letter code as defined in ISO 639-2/T or ISO 639-2/B
    xbmc.ENGLISH_NAME  Full language name in English (default)
    ================== ==========================================================

    :return: Converted Language string

    New function added.

    Example::

        language = xbmc.convertLanguage(English, xbmc.ISO_639_2)
    """
    return ""
