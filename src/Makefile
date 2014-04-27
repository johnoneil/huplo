

all:
	gcc `pkg-config --cflags glib-2.0 gstreamer-1.0` relay_stream.c `pkg-config --libs glib-2.0 gstreamer-1.0` -o relay-stream
	gcc `pkg-config --cflags glib-2.0 gstreamer-1.0 cairo` relay_stream_with_overlay.c `pkg-config --libs glib-2.0 gstreamer-1.0 cairo` -lgstvideo-1.0 -o relay-stream-with-overlay
