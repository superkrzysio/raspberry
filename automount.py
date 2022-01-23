import time
import os

# script that automatically mounts a plugged USB stick (which is supposed to be /dev/sda)
#   - mounts under /media/pi/<partition label>
#   - that feature is missing when running pi without X - see https://forums.raspberrypi.com/viewtopic.php?t=276494
#   - affects any stick, without /etc/fstab fiddle
#   - additionally do: `sudo vi /usr/share/polkit-1/actions/org.freedesktop.UDisks2.policy`
#     for action <action id="org.freedesktop.udisks2.filesystem-mount">
#     and action <action id="org.freedesktop.udisks2.filesystem-unmount-others"> change to:
#      <defaults>
#        <allow_any>yes</allow_any>
#     to skip udisksctl asking for authorization
#   - set the script to be run at boot time, e.g.
#     `sudo vi /etc/rc.local` and add:
#     `runuser -l pi -c "python /home/pi/dev/raspberry/automount.py &"`

already_mounted = False
while True:
  if os.path.exists("/dev/sda1"):
    if not already_mounted:
      os.system("udisksctl mount -b /dev/sda1")
      already_mounted = True
  else:
    already_mounted = False
  time.sleep(2)
