# MiniBotters

Small botting program made for [Minitroopers](http://enzoo987.minitroopers.fr), all rights reserved.
Easy of use, just put your accounts in the mtbotlist.txt file and run the python script, which will farm them.
Any idea for improvement is welcome, just open an issue to submit your idea.

Obviously, this program saves everything locally, none of your info is sent to me by any mean. (Felt like I had to clarify this, or at least write it down somewhere)

## Functionalities

* Farms battles, missions and raids for any account.
* Farms a whole list of account with their passwords.
* Autobuys missions if affordable.
* Reports the results of each action.
* Possibility to select an opponent and have every account attack him in battle (effectively raiding him).
* A menu
* [ ] Tells you if a trooper can be upgraded or if you can afford a new one.
* [ ] Different log levels, to prevent your console from getting flooded.
* [x] A recursive research of accounts to farm. (farm your recruits, and the recruits of your recruits)
* [ ] A way to add a strong password to each of your accounts, and note it in the file.
* [ ] A beautiful GUI for immensly improved usability. (well, in a distant future... maybe)

## Requirements

The script requires the [requests](https://2.python-requests.org/en/master/) python library as well as python3 to work (3.6 verified).
It needs rights to read the files in its directory.

## Warnings

The script was never tested on an account which already had actions performed for the day. Please only use clean accounts. (A warning might be implemented later)

Furthermore, it was only tested on french versions of the website, please let me know if it crashes and you use another language.
