#!/usr/bin/python
from gi.repository import Gtk, Gdk, Notify
import sys
import os
import inspect
import imghdr

cmd_subfolder = os.path.realpath (os.path.abspath (os.path.join (os.path.split (inspect.getfile (inspect.currentframe ()))[0], "modules")))
if cmd_subfolder not in sys.path:
    sys.path.insert (0, cmd_subfolder)

import pyimgur

app_name = "Imgur Uploader"

msg_not_an_image        = "is not an image."
msg_not_allowed         = "is not an allowed file type. Skipping."
msg_uploading           = "Uploading..."
msg_one_image           = "Your image has been uploaded."
msg_multiple_images     = "You images have been uploaded."
msg_copied_to_clipboard = "The link has been copied to your clipboard!"
msg_upload_failed       = "Upload failed, try again later."

# Auth
client_id     = "c7544afd27262f4"
client_secret = "c47da11193c858b91372599685736fa8d24635ec"

# Initialize PyImgur
client = pyimgur.Imgur (client_id = client_id, client_secret = client_secret)

# Notification icons
icon_info   = "help-info"
icon_error  = "error"
icon_upload = "go-up"


class ImgurUploader:
    def __init__ (self, args):

        allowed_types = ("jpeg", "jpg", "gif", "png", "apng", "tiff", "pdf", "xcf")
        images = []

        # Initialize the notification daemon
        Notify.init (app_name)
        self.notification = Notify.Notification.new ("", "", "")

        if len (args) == 1:
            return "Missing file path"
        else:
            for file in args:
                if file == args[0] or file == "":
                    continue
                type = imghdr.what (file)
                if not type:
                    self.notify (app_name, "{} {}".format (file, msg_not_an_image), icon_error)
                    sys.exit ()
                else:
                    if type not in allowed_types:
                        self.notify (app_name, "{} {}\n{}".format (type, msg_not_allowed, file), icon_error)
                        sys.exit ()
                    else:
                        images.append (file)

        self.upload (images)

    def notify (self, notification_title, notification_body, icon, timeout=5000):
        try:
            self.notification.update (notification_title, notification_body, icon)
            self.notification.set_timeout (timeout)
            self.notification.show ()
        except:
            pass

    def upload (self, images):
        self.notify (app_name, msg_uploading, icon_info)
        imgur_ids = []
        number_of_images = len (images)
        current_image = 0

        for image in images:
            try:
                uploaded_images = client.upload_image (image)
            except:
                self.notify (app_name, msg_upload_failed, icon_error)

            imgur_ids.append (uploaded_images.id)

            if number_of_images > 1:
                current_image += 1
                left = number_of_images - current_image
                msg_progress = "{} out of {} images uploaded, {} left.".format (
                    str (current_image), str (number_of_images), str (left))
                self.notify (app_name, msg_progress, icon_upload)

        if len (imgur_ids) > 1:
            album = client.create_album (images = imgur_ids)
            url = album.link
            self.notify (msg_multiple_images, msg_copied_to_clipboard, icon_info, 3000)
        else:
            url = uploaded_images.link
            self.notify (msg_one_image, msg_copied_to_clipboard, icon_info, 3000)

        self.set_clipboard (url)

    def set_clipboard (self, url):
        display   = Gdk.Display.get_default ()
        selection = Gdk.Atom.intern ("CLIPBOARD", False)
        clipboard = Gtk.Clipboard.get_for_display (display, selection)
        clipboard.set_text (url, -1)
        clipboard.store ()

if __name__ == '__main__':
    uploader = ImgurUploader (sys.argv)
