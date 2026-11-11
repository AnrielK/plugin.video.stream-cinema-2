import xbmcgui, xbmc

from resources.lib.utils.kodiutils import get_info


class CaptchaWindow(xbmcgui.WindowXMLDialog):

    def __init__(self, xmlFilename, scriptPath, *args, **kwargs):
        super(CaptchaWindow, self).__init__(xmlFilename, scriptPath)
        self.img = kwargs.get('captcha')
        title_text = kwargs.get('title_text')
        self.kbd = xbmc.Keyboard('', title_text, False)

    def onInit(self):
        self.getControl(101).setImage(self.img.encode('utf8'))

    def get(self):
        self.show()
        xbmc.sleep(500)
        self.kbd.doModal()
        if self.kbd.isConfirmed():
            text = self.kbd.getText()
            self.close()
            return text
        self.close()
        return False


def ask_for_captcha(img, title):
    solver = CaptchaWindow('captcha-image.xml', get_info('path'), 'default', captcha=img,
                           title_text=title)
    return solver.get()
