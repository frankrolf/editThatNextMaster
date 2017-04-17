# coding: utf-8

import subprocess
import vanilla
from AppKit import NSPasteboardTypeString, NSPasteboard

"""
   Little window that shows a list of the currently selected glyphs,
   with different format options, with spaces, commas, slashes, or as unicode.
   v 1 April 17 2017 

    ǺÆÐØÞĐĦĲĿŁŊŒŦǻßæðøþđħĳŀłŋœŧ

    Aringacute AE Eth Oslash Thorn Dcroat Hbar IJ Ldot Lslash Eng OE Tbar aringacute germandbls ae eth oslash thorn dcroat hbar ij ldot lslash eng oe tbar

    Aringacute, AE, Eth, Oslash, Thorn, Dcroat, Hbar, IJ, Ldot, Lslash, Eng, OE, Tbar, aringacute, germandbls, ae, eth, oslash, thorn, dcroat, hbar, ij, ldot, lslash, eng, oe, tbar

    /Aringacute/AE/Eth/Oslash/Thorn/Dcroat/Hbar/IJ/Ldot/Lslash/Eng/OE/Tbar/aringacute/germandbls/ae/eth/oslash/thorn/dcroat/hbar/ij/ldot/lslash/eng/oe/tbar


"""


        
class NameCopier(object):
    maxTitleLength = 20
    sampleText = ["Copy the names", "of selected glyphs", "in a couple of useful", "formats to the clipboard."]
    def __init__(self):
        self.w = vanilla.Window((170, 240), "Copier")
        self.w.l = vanilla.List((0,0,0,-120), self.sampleText)
        self.w.copyAsGlyphNames = vanilla.Button((2,-118,-2,20), "names", self.click, sizeStyle="small")
        self.w.copyAsGlyphNames.tag = "names"
        self.w.copyAsGlyphNamesComma = vanilla.Button((2,-98,-2,20), "quoted names + comma", self.click, sizeStyle="small")
        self.w.copyAsGlyphNamesComma.tag = "comma"
        self.w.copyAsSlashedNames = vanilla.Button((2,-78,-2,20), "slash + name", self.click, sizeStyle="small")
        self.w.copyAsSlashedNames.tag = "slash"
        self.w.copyAsUnicode = vanilla.Button((2,-58,-2,20), "Unicode text", self.click, sizeStyle="small")
        self.w.copyAsUnicode.tag = "unicode"
        self.w.copyAsFeatureGroup = vanilla.Button((2,-38,-2,20), "feature group", self.click, sizeStyle="small")
        self.w.copyAsFeatureGroup.tag = "feature"
        self.w.caption = vanilla.TextBox((5,-13,-5,20), "Copy selected names to clipboard", sizeStyle="mini")
        self.w.open()
        self.w.bind("became main", self.update)
        self.w.bind("became key", self.update)
        self.update()
    
    def update(self, sender=None):
        self.font = CurrentFont()
        names = self.font.selection
        if len(self.font.selection)==0:
            self.w.l.set(self.sampleText)
            self.w.copyAsGlyphNames.setTitle("names")
            self.w.copyAsGlyphNamesComma.setTitle("quoted names + comma")
            self.w.copyAsSlashedNames.setTitle("slashed names")
            self.w.copyAsUnicode.setTitle("Unicode text")
            self.w.copyAsFeatureGroup.setTitle("feature group")
        else:
            self.w.l.set(names)
            self.w.copyAsGlyphNames.setTitle(self._asTitle(self._asSpacedNames(names)))
            self.w.copyAsGlyphNamesComma.setTitle(self._asTitle(self._asQuotesAndCommasNames(names)))
            
            self.w.copyAsSlashedNames.setTitle(self._asTitle(self._asSlashedNames(names)))
            self.w.copyAsUnicode.setTitle(self._asTitle(self._asUnicodeText(names)))
            self.w.copyAsFeatureGroup.setTitle(self._asTitle(self._asFeatureGroup(names)))
        if len(names)==0:
            self.w.caption.set("No glyphs selected.")
        else:
            self.w.caption.set("Copy %d names"%(len(names)))
    
    def _asSpacedNames(self, names):
        return " ".join(names)

    def _asQuotesAndCommasNames(self, names):
        return ", ".join(["\"%s\""%s for s in names])
    
    def _asSlashedNames(self, names):
        return "/"+"/".join(names)

    def _asUnicodeText(self, names):
        return "/"+"/".join(names)

    def _asFeatureGroup(self, names):
        return "[%s]"%" ".join(names)
    
    def _asTitle(self, text):
        if len(text)<self.maxTitleLength:
            return text
        return text[:self.maxTitleLength]+u"…"
        
    def _asUnicodeText(self, names):
        text = ""
        for n in names:
            if self.font[n].unicode is not None:
                text += unichr(self.font[n].unicode)
        if not text:
            return "[no unicodes]"
        return text
        
    def click(self, sender):
        t = sender.tag
        f = CurrentFont()
        names = f.selection
        copyable = ""
        if t == "names":
            copyable = self._asSpacedNames(names)
        elif t == "comma":
            copyable = self._asQuotesAndCommasNames(names)
        elif t == "slash":
            copyable = self._asSlashedNames(names)
        elif t == "feature":
            copyable = self._asFeatureGroup(names)
        elif t == "unicode":
            copyable = self._asUnicodeText(names)
        self._toPasteBoard(copyable)
        self.w.caption.set("%d names to clipboard!"%(len(names)))

    def _toPasteBoard(self, text):
        pb = NSPasteboard.generalPasteboard()
        pb.clearContents()
        pb.declareTypes_owner_([
            NSPasteboardTypeString,
        ], None)
        pb.setString_forType_(text,  NSPasteboardTypeString)

if __name__ == "__main__":            
    n = NameCopier()
