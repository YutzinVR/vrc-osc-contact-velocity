<h2 align="center">OSC Router Setup</h2>

<h2> 📝 Table of Contents </h2>

- [🔀 Routing](#-routing)
- [⚙️ Configuration](#️-configuration)

## 🔀 Routing

The vrc-osc-contact-velocity router sits between VrChat and the OSC program of choice. It will forward any OSC parameters that are not used by the velocity router.

    +-------------------+      +------------------+     +------------------+
    |                   |      |                  |     |                  |
    |      VrChat       +----->| VRC-OSC-Contact- |---->| OSC Program of   |
    |                   |      |     Velocity     |     |     Choice       |
    |                   |      |                  |     |                  |
    +-------------------+      +------------------+     +------------------+

## ⚙️ Configuration

In this case the vrc-osc-contact-velocity router will listen to port 9001 and output the results on port 9002. So your OSC program of choice has to listen to port 9002 so it will receive the changed velocity parameters.

````INI
# Source IP & port is the VRC OSC server to listen to:

sourceIP = 127.0.0.1
sourcePort = 9001

# Target IP & port is the OSC server to send to:

targetIP = ${sourceIP}
targetPort = 9002
````




