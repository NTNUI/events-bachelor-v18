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

## Language files

###gettext
To make any changes to the language files(.po, .mo) you will first need to install gettext, 
it can be downloaded from the following site ([gettext link](https://www.gnu.org/software/gettext))
    
To find out how to add translations to your view or templates, you may visit djangos[documentation](https://docs.djangoproject.com/en/2.0/topics/i18n/translation/)
    
All language files are located in the locale folder, with subfolders corresponding to the language extension(nb, nn etc) 

###Update or create a language
After you have navigated to you project root directory, you can create or update languages using the following command:
    ```
    python manage.py makemessages -l language_code -i env
    ```
Where the language_code is the extension for the language you would like to use, for instance nb is norwegian bokmål. 

###Compile messages
After you have made the translations, you can compile them using the following comand. 
    ```
    python manage.py compilemessages
    ```
To compile the new translations, and you are good to go.
