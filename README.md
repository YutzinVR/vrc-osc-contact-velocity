
<h2 align="center">vrc-osc-contact-velocity</h2>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![GitHub Issues](https://img.shields.io/github/issues/YutzinVR/vrc-osc-contact-velocity.svg)](https://github.com/YutzinVR/vrc-osc-contact-velocity/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/YutzinVR/vrc-osc-contact-velocity.svg)](https://github.com/YutzinVR/vrc-osc-contact-velocity/pulls)


</div>

---



## 📝 Table of Contents

- [📝 Table of Contents](#-table-of-contents)
- [🧐 About ](#-about-)
- [🏁 Getting Started ](#-getting-started-)
- [✍️ Authors ](#️-authors-)
- [🎉 Acknowledgements ](#-acknowledgements-)

## 🧐 About <a name = "about"></a>

An OSC router written in Python to intercept VRChat OSC parameters, calculate the velocity, and forward them to another OSC server. Intended for the use case of calculating velocity of a contact sender to drive the Giggletech haptic.

## 🏁 Getting Started <a name = "getting_started"></a>

1. Add contact receivers for each haptic device to your VRChat Avatar.
2. (optional) Add additional spherical contact receivers around the haptic device location to assist with velocity estimation. Evenly space the receivers for more consistent velocity estimation.
3. Add unique parameter keys for each contact receiver to your animation controller and map those back to the respective receivers.
4. Change the settings in the configuration file ```Config.ini```. Parameter keys should match those specified in your unity project.
5. Run the server<br/>
 ```cmd
vrc-osc-contact-velocity.exe
```
6. Run the haptice device server (eg. GiggleTech OSC router). Make sure to configure the correct IP, port, and parameter addresses to listen to this contact velocity server. Ensure that your haptic device is turned on.
7. Open VRChat.

## ✍️ Authors <a name = "authors"></a>

- [@YutzinVR](https://github.com/YutzinVR) - Idea & Initial work
- [@LukasL28](https://github.com/LukasL28) - Contributor

See also the list of [contributors](https://github.com/YutzinVR/vrc-osc-contact-velocity/contributors) who participated in this project.

## 🎉 Acknowledgements <a name = "acknowledgement"></a>
- TenderNya
- Molnia
- ShinyButton

