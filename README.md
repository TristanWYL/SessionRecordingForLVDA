# Motivation
To code this program is for monitoring users' operations. Citris system brings Session Recording feature for Windows VDA, while not for Linux VDA. This is why I code this.

# To install this software as a Linux Service
## For Ubuntu
1. set suitable parameters in **config.py**;
2. update the **ExecStart** item as appropriate in **SessionRecording.service**;
3. run the following commands;
    ```
    sudo cp SessionRecording.service /lib/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable SessionRecording.service
    sudo systemctl start SessionRecording.service
    ```

# Note
1. The subprocess should be terminated/killed before the main process, otherwise the recorded video will not be playable. To achieve this, the following steps are applied:
    1. KillMode=process
    2. python code handles the SIGTERM gracefully
2. This repository should work with **Citrix** system, as **ctxqsession** is used to detect whether a GNOME session is active for a user.

# DRAWBACKS:
1. Cannot track the change of resolutions. If the resolution is getting bigger when recording, the smaller window _width by height_ is still in force, till the next recording period.
