#!/usr/bin/python
from gi.repository import Gtk, Gdk, Notify
import sys
import imghdr
sys.path.append("./modules/")
import pyimgur

app_name = "Imgur Uploader"

msg_not_an_image = "is not an image. Skipping."
msg_not_allowed = "is not an allowed file type. Skipping."
msg_one_image = "Your image has been uploaded."
msg_multiple_images = "You images have been uploaded."
msg_clipboard = "The link has been copied to your clipboard!"
msg_upload_failed = "Upload failed, try again later."
msg_ommited = " files were ommited."

# Auth
client_id = "c7544afd27262f4"
client_secret = "c47da11193c858b91372599685736fa8d24635ec"

# Initialize PyImgur
client = pyimgur.Imgur(client_id=client_id, client_secret=client_secret)

# Notification icons
icon_info = "help-info"
icon_error = "error"
icon_upload = "go-up"


class ImgurUploader:

    def __init__(self, args):
        # Initialize the notification daemon
        Notify.init(app_name)
        self.notification = Notify.Notification.new("", "", "")

        allowed_types = (
            "jpeg", "jpg", "gif", "png", "apng", "tiff", "pdf", "xcf")
        images = []
        ommited = 0

        if len(args) == 1:
            sys.exit("Missing file path")

        for file in args:
            # Skip first argument (script name)
            if file == args[0] or file == "":
                continue

            type = imghdr.what(file)

            # Check if the file is an image
            if not type:
                if len(args) > 2:
                    print "{} {}".format(file, msg_not_an_image)
                    ommited += 1
                    continue
                else:
                    self.notify(
                        app_name, "{} {}".format(
                            file, msg_not_an_image), icon_error, False)
                    sys.exit("{} {}".format(file, msg_not_an_image))

            # Check if the image is an allowed type
            if type not in allowed_types:
                if len(args) > 2:
                    print "{}: {} {}".format(file, type, msg_not_allowed)
                    ommited += 1
                    continue
                else:
                    self.notify(app_name, "{} {}\n{}".format(
                        type, msg_not_allowed, file), icon_error, False)
                    sys.exit("{}: {} {}".format(file, type, msg_not_allowed))

            images.append(file)

        if ommited != 0:
            if len(args) - 1 == ommited:
                self.notify(
                    app_name, "All files were ommited.", icon_error, False)
                sys.exit("All files were ommited.")

        self.upload(images, ommited)

    def notify(self, notification_title, notification_body, icon, new,
               timeout=5000):
        if new:
            Notify.Notification.new(
                notification_title, notification_body, icon).show()
            pass
        self.notification.update(notification_title, notification_body, icon)
        self.notification.set_timeout(timeout)
        try:
            self.notification.show()
        except:
            print "Unable to show notification."
            pass

    def upload(self, images, ommited):
        if ommited > 0:
            msg_uploading = "Uploading {} images, {} ommited".format(
                len(images), ommited)
        else:
            msg_uploading = "Uploading {} images".format(len(images))
        self.notify(app_name, msg_uploading, icon_info, False, 3000)
        imgur_ids = []
        number_of_images = len(images)
        current_image = 0

        for image in images:
            try:
                uploaded_images = client.upload_image(image)
            except:
                self.notify(app_name, msg_upload_failed, icon_error)

            imgur_ids.append(uploaded_images.id)

            if number_of_images > 1:
                current_image += 1
                left = number_of_images - current_image
                msg_progress = "{} out of {} images uploaded, {} left.".format(
                    str(current_image), str(number_of_images), str(left))
                self.notify(app_name, msg_progress, icon_upload, False)

        if len(imgur_ids) > 1:
            album = client.create_album(images=imgur_ids)
            url = album.link
            self.notify(
                msg_multiple_images, msg_clipboard, icon_info, False, 3000)
        else:
            url = uploaded_images.link
            self.notify(
                msg_one_image, msg_clipboard, icon_info, False, 3000)

        self.set_clipboard(url)

    def set_clipboard(self, url):
        display = Gdk.Display.get_default()
        selection = Gdk.Atom.intern("CLIPBOARD", False)
        clipboard = Gtk.Clipboard.get_for_display(display, selection)
        clipboard.set_text(url, -1)
        clipboard.store()

if __name__ == '__main__':
    uploader = ImgurUploader(sys.argv)
