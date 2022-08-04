# 99damage_reader

a simple script to scrape info about 99damage teams or matches

## Description

this script gets information about 99damage teams/matches
* Player information
	* 99damage Name
	* SteamID3
	* Steam Name
	* VAC Ban
	* Game Ban
	* Faceit Elo
	* Faceit K/D
	* HLTV Rating
	* Faceit Match count
* Match information
	* Match score
	* Map score
	* Pick/Ban
	* Player information for every player


## Getting Started

### Dependencies

* [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
* [requests](https://pypi.org/project/requests/)

### Executing program

* python 99reader.py <-t | -m> <-p | -c>
	* 2 arguments are required
	* -t / --team
	* -m / --match
	* -p / --print
	* -c / --csv

## Authors

[@yurox19](https://github.com/yurox19)

## Version History

* 0.1
	* Initial Release
* 0.2
	* Updated "99damage.de" to "liga.esl-meisterschaft.de"

## License

This project is licensed under the [The Unlicense] License - see the LICENSE.md file for details
