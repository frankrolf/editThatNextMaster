"""

    If you're editing masters or whatever
    and you want to switch to the same glyph in the other master
    and you spend a lot of time moving glyph windows around
    or you've had to divide your massive pixel real estate into small lots.

    Add this script to RF and wire it to a key command
    and then woosh woosh woosh cycle between the masters.
    The other script, "editThatNextMaster.py" wooshes the other direction.
    
    The order in which these scripts woosh through the fonts: alphabetically sorted filepath.
    
    With massive help from @typemytype
    @letterror
    20160918
    v5


"""

from AppKit import *
from mojo.UI import *
from mojo.roboFont import CurrentFont, CurrentGlyph, AllFonts


def getCurrentFontAndWindowFlavor():
    """ Try to find what type the current window is and which font belongs to it."""
    windows = [w for w in NSApp().orderedWindows() if w.isVisible()]
    skip = ["PreferencesWindow", "ScriptingWindow"]
    for window in windows:
        if hasattr(window, "windowName"):
            windowName = window.windowName()
            if windowName in skip:
                continue
            if hasattr(window, "document"):
                return window.document().font.path, windowName
    return None, None

def getGlyphWindowPosSize():
    w = CurrentGlyphWindow()
    if w is None:
        return
    x,y, width, height = w.window().getPosSize()
    settings = getGlyphViewDisplaySettings()
    view = w.getGlyphView()
    viewFrame = view.visibleRect()
    viewScale = w.getGlyphViewScale()
    return (x, y), (width, height), settings, viewFrame, viewScale

def setGlyphWindowPosSize(glyph, pos, size, animate=False, settings=None, viewFrame=None, viewScale=None, layerName=None):
    OpenGlyphWindow(glyph=glyph, newWindow=False)
    w = CurrentGlyphWindow()
    #help(w)
    view = w.getGlyphView()
    w.window().setPosSize((pos[0], pos[1], size[0], size[1]), animate=animate)
    if viewScale is not None:
        w.setGlyphViewScale(viewScale)
    if viewFrame is not None:
        view.scrollRectToVisible_(viewFrame)
    if settings is not None:
        setGlyphViewDisplaySettings(settings)
    if layerName is not None:
        w.setLayer(layerName, toToolbar=True)

def setSpaceCenterWindowPosSize(font):
    w = CurrentSpaceCenterWindow()
    posSize = w.window().getPosSize()
    c = w.getSpaceCenter()
    rawText = c.getRaw()
    prefix = c.getPre()
    suffix = c.getAfter()
    size = c.getPointSize()
    w = OpenSpaceCenter(font, newWindow=False)
    new = CurrentSpaceCenterWindow()
    new.window().setPosSize(posSize)
    w.setRaw(rawText)
    w.setPre(prefix)
    w.setAfter(suffix)
    w.setPointSize(size)

def getOtherMaster(nextFont=True):
    cf = CurrentFont()
    orderedFonts = []
    fonts = {}
    for f in AllFonts():
        if f.path is None:
            fontSortKey = id(f)
        else:
            fontSortKey = f.path
        fonts[fontSortKey]=f
    sortedPaths = fonts.keys()
    sortedPaths.sort()
    
    for i in range(len(sortedPaths)):
        if cf.path == fonts[sortedPaths[i]].path:
            prev = fonts[sortedPaths[i-1]]
            nxt = fonts[sortedPaths[(i+1)%len(sortedPaths)]]
            if nextFont:
                return nxt
            else:
                return prev

def switch(direction=1):
    currentPath, windowType = getCurrentFontAndWindowFlavor()
    nextMaster = getOtherMaster(direction==1)
    f = CurrentFont()
    if windowType == "FontWindow":
        fontWindow = CurrentFontWindow()
        selectedGlyphs = f.selection
        currentFontWindowQuery =  fontWindow.getGlyphCollection().getQuery()
        #help(fontWindow)
        selectedSmartList = fontWindow.fontOverview.views.smartList.getSelection()
        posSize = fontWindow.window().getPosSize()
        nextWindow = nextMaster.document().getMainWindow()
        nextMaster.selection = selectedGlyphs
        nextWindow.setPosSize(posSize)
        nextWindow.show()
        # set the selected smartlist
        fontWindow = CurrentFontWindow()
        fontWindow.fontOverview.views.smartList.setSelection(selectedSmartList)
        fontWindow.getGlyphCollection().setQuery(currentFontWindowQuery)    # sorts but does not fill it in the form
    elif windowType == "SpaceCenter":
        setSpaceCenterWindowPosSize(nextMaster)

    elif windowType == "GlyphWindow":
        g = CurrentGlyph()
        if g is not None:
            currentLayerName = g.layerName
            n = getOtherMaster(direction==1)
            if not g.name in n:
                NSBeep()
                return None
            nextGlyph = n[g.name]
            if nextGlyph is not None:
                rr = getGlyphWindowPosSize()
                if rr is not None:
                    p, s, settings, viewFrame, viewScale = rr
                    setGlyphWindowPosSize(nextGlyph, p, s, settings=settings, viewFrame=viewFrame, viewScale=viewScale, layerName=currentLayerName)

if __name__ == "__main__":
    switch(-1)
