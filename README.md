<p align="center">
<img width="200" src="ntnui/static/img/ntnui.svg" />
</p>

## Description

Internal system for members and volunteers in NTNUI.

## Installation

```
make build
```

## How to run

```
make start
```

## Docker

## Browser testing

### Requirements for testing with visual browser:

* [Install Google Chrome](https://www.google.com/chrome/browser/desktop/index.html)
* [Install Firefox](https://www.mozilla.org/nb-NO/firefox/new/)
* Install chromedriver

  * macOS:
    * [Install homebrew](https://brew.sh/index_no.html)
    * `brew install chromedriver`
  * windows
    * [Download chromedriver](https://sites.google.com/a/chromium.org/chromedriver/)
    * Unzip
    * Put into `C:\Windows`
  * linux
    * [Download chromedriver](https://sites.google.com/a/chromium.org/chromedriver/)
    * Unzip
    * Put into `/usr/local/bin`

* Install geckodriver
  * macOS:
    * [Install homebrew](https://brew.sh/index_no.html)
    * `brew install geckodriver`
  * windows
    * [Download geckodriver](https://github.com/mozilla/geckodriver/releases)
    * Unzip
    * Put into `C:\Windows`
  * linux
    * [Download geckodriver](https://github.com/mozilla/geckodriver/releases)
    * Unzip
    * Put into `/usr/local/bin`

## Updating language files:

All language files are located in the locale folder, to edit them simply 
choose the language of your choice
Language files can be updated by using:
```
python manage.py makemessages -l nb -i env
```
were nb is norwegian (bokmål), to add a diffrent language simply find its code.
English is default.

Use:
```
python manage.py compilemessages
```
To compile the new translations, and you are good to go.
