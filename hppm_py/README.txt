Recommended Windows setup:
Install MSYS2
In MSYS2 shell

pacman -S mingw-w64-x86_64-gtk3 mingw-w64-x86_64-python3 mingw-w64-x86_64-python3-gobject mingw-w64-x86_64-gst-python mingw-w64-x86_64-gst-libav mingw-w64-x86_64-gst-plugins-bad mingw-w64-x86_64-gst-plugins-base mingw-w64-x86_64-gst-plugins-good mingw-w64-x86_64-gst-plugins-ugly

In MINGW64 shell

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
pip install serial

You will need the following packages at minimum:
pySerial
pyOSC

Optional:
psyco

Raspbian (Debian 12)
sudo apt install -y python3-gst-1.0 python3-serial gstreamer1.0-alsa gstreamer1.0-plugins-good
