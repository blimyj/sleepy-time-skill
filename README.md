# <img src="https://raw.githack.com/FortAwesome/Font-Awesome/master/svgs/solid/bed.svg" card_color="#000000" width="50" height="50" style="vertical-align:bottom"/> Sleepy Time
Plays a local audio file to help you sleep.

## About
When activated it will play a local audio file to help you sleep.
Automatically pauses when Mycroft is listening or speaking and resumes after Mycroft is done.
Saves last played position so you can resume without having to remember where you last stopped!
This is especially useful if you are playing an audiobook.

## Examples
* "Help me sleep"
* "Time to sleep"
* "I'm going to bed"
* "Stop reading"
* "Continue reading"

## Credits
blimyj

## Category
**Daily**

## Tags

## FAQ

* "libvlc_new not found"
  * Restart mycroft-core as current instance may be using the previous version of vlc.
  * bash stop-mycroft.sh all
  * bash start-mycroft debug
