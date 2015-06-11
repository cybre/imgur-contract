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
msgFailed = "Upload failed, try again later."

# Auth
clientId = "c7544afd27262f4"
clientSecret = "c47da11193c858b91372599685736fa8d24635ec"

# Initialize Imgur
client = pyimgur.Imgur(client_id=clientId, client_secret=clientSecret)

# Notification icons
iconInfo = "help-info"
iconError = "error"
iconUpload = "go-up"


class ImgurUploader:
    def __init__(self, args):

        allowedTypes = ("jpeg", "jpg", "gif", "png", "apng", "tiff", "bmp", "pdf", "xcf")
        images = []

        # Initialize the notification daemon
        Notify.init(appName)
        self.notification = Notify.Notification.new("", "", "")

        if len(args) == 1:
            return
        else:
            for file in args:
                if file == args[0] or file == "":
                    continue
                type = imghdr.what(file)
                if not type:
                    self.notify(appName, file + " " + msgNotAnImage, iconError)
                    sys.exit()
                else:
                    if type not in allowedTypes:
                        self.notify(appName, type + " " + msgNotAllowed + file, iconError)
                        sys.exit()
                    else:
                        images.append(file)

        self.upload(images)

    def notify(self, messageOne, messageTwo, icon, timeout=30000):
        self.notification.update(messageOne, messageTwo, icon)
        self.notification.set_timeout(timeout)
        self.notification.show()

    def upload(self, images):
        self.notify(appName, msgUploading, iconInfo)
        ids = []
        numOfImages = len(images)
        currImage = 0

        for image in images:
            try:
                uploadedImages = client.upload_image(image)
            except:
                self.notify(appName, msgFailed, iconError)

            ids.append(uploadedImages.id)

            if numOfImages > 1:
                currImage += 1
                left = numOfImages - currImage
                msgProgress = str(currImage) + " out of " + str(numOfImages) + " images uploaded, " + str(left) + " left."
                self.notify(appName, msgProgress, iconUpload)

        if len(ids) > 1:
            album = client.create_album(images=ids)
            url = album.link
            self.notify(msgMultipleImages, msgClipboard, iconInfo, 3000)
        else:
            url = uploadedImages.link
            self.notify(msgOneImage, msgClipboard, iconInfo, 3000)

        self.setClipboard(url)

    def setClipboard(self, url):
        display = Gdk.Display.get_default()
        selection = Gdk.Atom.intern("CLIPBOARD", False)
        clipboard = Gtk.Clipboard.get_for_display(display, selection)
        clipboard.set_text(url, -1)
        clipboard.store()

if __name__ == '__main__':
    uploader = ImgurUploader(sys.argv)
