# vrc-osc-contact-velocity
## Description
An OSC router written in Python to intercept VRChat OSC parameters, calculate the velocity, and forward them to another OSC server. Intended for the use case of calculating velocity of a contact sender to drive the Giggletech haptic.
## Requirements:
- Python 3.12+ (I haven't tested on older versions, but it might work)

## Installation:
1. Clone the repo or download the latest release.
2. In the command line, navigate to the directory where you've saved the repo:<br/>
```cmd
cd "<YOUR_DIRECTORY>\vrc-osc-contact-velocity\"
```
3. (optional) Create a python virtual environment and activate it. <br/>
```cmd
pip -m venv .venv
.venv\Scripts\activate.bat
```
5. Install the required python modules: <br/>
```cmd
pip install -r requirements.txt
```
## Setup:

1. Add contact receivers for each haptic device to your VRChat Avatar.
2. (optional) Add additional spherical contact receivers around the haptic device location to assist with velocity estimation. Evenly space the receivers for more consistent velocity estimation.
3. Add unique parameter keys for each contact receiver to your animation controller and map those back to the respective receivers.
4. Change the settings in the configuration file ```Config.ini```. Parameter keys should match those specified in your unity project.
5. Run the server<br/>
 ```cmd
python main.py
```
6. Run the haptice device server (eg. GiggleTech OSC router). Ensure that your haptic device is turned on.
7. Open VRChat.

## Credits
- TenderNya
- Molnia
- ShinyButton
