#!/usr/bin/python
import sys
import os
import inspect
from gi.repository import Gtk, Gdk, Notify
import imghdr

cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], "modules")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

import pyimgur

appName = "Imgur Uploader"

msgNotAnImage = "is not an image."
msgNotAllowed = "is not an allowed file type. Skipping."
msgUploading = "Uploading..."
msgOneImage = "Your image has been uploaded."
msgMultipleImages = "You images have been uploaded."
msgClipboard = "The link has been copied to your clipboard!"

# Auth
clientId = "c7544afd27262f4"
clientSecret = "c47da11193c858b91372599685736fa8d24635ec"

# Initialize Imgur
client = pyimgur.Imgur(client_id=clientId, client_secret=clientSecret)


class ImgurUploader:
    def __init__(self, args):

        allowedTypes = ("jpeg", "jpg", "gif", "png", "apng", "tiff", "bmp", "pdf", "xcf")
        images = []

        # Initialize the notification daemon
        Notify.init(appName)

        if len(args) == 1:
            return
        else:
            for file in args:
                if file == args[0] or file == "":
                    continue
                type = imghdr.what(file)
                if not type:
                    self.notify(appName, file + " " + msgNotAnImage)
                    sys.exit()
                else:
                    if type not in allowedTypes:
                        self.notify(appName, type + " " + msgNotAllowed + file)
                        sys.exit()
                    else:
                        images.append(file)

        self.upload(images)

    def notify(self, messageOne, messageTwo=None):
        notification = Notify.Notification.new(messageOne, messageTwo, 'info')
        notification.show()

    def upload(self, images):
        self.notify(appName, msgUploading)
        ids = []
        for image in images:
            uploadedImages = client.upload_image(image)
            ids.append(uploadedImages.id)
        if len(ids) > 1:
            album = client.create_album(images=ids)
            url = album.link
            self.notify(msgMultipleImages, msgClipboard)
        else:
            url = uploadedImages.link
            self.notify(msgOneImage, msgClipboard)
        self.setClipboard(url)

    def setClipboard(self, url):
        display = Gdk.Display.get_default()
        selection = Gdk.Atom.intern("CLIPBOARD", False)
        clipboard = Gtk.Clipboard.get_for_display(display, selection)
        clipboard.set_text(url, -1)
        clipboard.store()

if __name__ == '__main__':
    uploader = ImgurUploader(sys.argv)
