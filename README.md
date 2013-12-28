Huplo- Heads Up Presention Layer
================================

Huplo is a simple gstreamer based framework to overlay text (and possibly graphics) on a video stream. It was first developed to overlay IRC chats onto a live stream, but could be driven by any data source.

Currently clients can convey text data to the gstreamer rendering graph via gtk DBus, allowing clients to be cleanly separated from the rendering code. N clients can feed data to M displays.

Since it currently is heavily dependent upon numerous packages not managed
by pypi, installation is currently haphazard. These outside packages include:

* cairo
* pango
* pycairo
* pangocairo
* gtk
* dbus etc..

The overall model followed is fairly simple, and a full specific new type of overlay server/client can be implemented in about 250-300 lines of python code. The existing code should make this fairly easy.

Refer to the github repository for more info:
https://github.com/johnoneil/huplo
