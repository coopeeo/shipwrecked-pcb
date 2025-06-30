# Shipwrecked Badge
Welcome to the Shipwrecked Badge! This repository is the source code for the operating system of the badge. If you're looking for apps for your badge, check out [the registry](https://need-to-do-this.example.com). If you're looking for documentation on how to use your badge, check out the [wiki](https://need-to-do-this.example.com).

The rest of this page is about how the badge works under the hood and how to develop for it.

## OS Structure
The badge's operating system is structured around the `BadgeOS` class. This class coordinates the various subsystems of the badge. Most of its functions run asynchronously on the main core, leaving the second core free to run the app thread.

For additional documentation, especially early plans, check the canvases in the #shipwrecked-pcb channel.