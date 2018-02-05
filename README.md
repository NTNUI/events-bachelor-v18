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

```
	test
```
