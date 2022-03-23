# DiscoCam (formerly: Spicy Cam)

Make your video calls more "spicy" with these video effects
on the fly!

## Installation

Currently this only supports Linux although the image processing
can eventually be used on all platforms.

First, install `v4l2loopback-dkms` on your computer

```sh
sudo apt install v4l2loopback-dkms
```

Then, activate the virtual camera

```sh
sudo modprobe v4l2loopback exlusive_caps=1 video_nr=2 card_label="Spicy Cam"
```

Now you're ready to go!

## Usage

Run the camera script as follows:

```sh
./cam.py
```

Add a filter by typing `add <filtername>` or read the help documentation
to see other things you can do to your webcam!

Make sure that you're not currently using your original webcam when you
start this script, and when you need to use it for another application,
like Zoom or gather.town, be sure to choose the "Spicy Cam" option
on your list of webcams

## Note regarding hackathon submissions

You might have seen that one team member had previously created
[webcam-video-effects](https://github.com/intermezzio/webcam-video-effects) which
attempts to add effects to webcams using ffmpeg. However, at the time of the hackathon
submission, these projects have different effects and there was no overlap other than
the backend tool used.
