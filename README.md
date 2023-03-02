# Bite-sized News Scraper

- [Bite-sized News Scraper](#bite-sized-news-scraper)
  - [Newspapers](#newspapers)
  - [Philosophy](#philosophy)
    - [Listing articles](#listing-articles)
    - [Getting an article's contents](#getting-an-articles-contents)
  - [Using the scraping engine](#using-the-scraping-engine)
    - [Installation](#installation)
    - [Configuration](#configuration)
      - [globals](#globals)
      - [lister\_args](#lister_args)
    - [engine.py](#enginepy)
  - [Writing your own scraper](#writing-your-own-scraper)

**NOTE**: This project should be used at own risk and not for commercial purposes. I am not responsible for any legal issues that may arise from using this project.

Welcome to the bite-sized news scraper. This project is a collection of scripts that can be used to scrape news articles from various news websites.

The goals of this project are:
1. Create a flexible framework for scraping news websites able to be used by any developer for any news site.
2. Create a historical database of news articles that can be used for research purposes.

## Newspapers

✅ = ready || ⏱ = in progress || ❌ = not yet

**Newspaper** | **Module** | **Status** | **Version**
--- | --- | --- | ---
The Age | theage | ✅ | v1
News.com.au | newscomau | ✅ | v1
The Guardian | guardian | ✅ | v1
Australian Financial Review | afr | ✅ | v1
ABC | abc | ⏱ | -
BBC | bbc | ✅ | -
Al Jazeera | aljazeera | ⏱ | -

## Philosophy
There are generally two broad steps needed to be taken when extracting news articles:
1. Listing the possible articles to retrieve
2. Retrieving the textual content of each article

### Listing articles

### Getting an article's contents

## Using the scraping engine

### Installation

Install pipenv and run:

```bash
pipenv install --dev
```

### Configuration

I use [confection](https://github.com/explosion/confection) for configuring the scraping engine. Example configuration files can be found in the [/templates](src/templates/) directory.

```python
[globals]
module=str
max_at_once=int
max_per_second=int

[lister_args]
...args
```

#### globals

**module**: The module to use for scraping. This should be the name of a module in the [/src/scrapers](src/scrapers/) directory. For a reference of available modules see the [Newspaper](#newspapers) table above.

Under the hood [aiometer](https://github.com/florimondmanca/aiometer) is responsible for implementing a rate-limiting architecture so that we don't overload any news sites with requests. The following configuration options are available:

**max_at_once**: The maximum number of articles to scrape at once. This is used to prevent overloading the server.

**max_per_second**: The number of articles to scrape per second. This is used to prevent overloading the server.

#### lister_args

Under lister_args can be any arguments that are needed to run the list_articles function of a scraper module. This allows the list_articles function for each scraper to differ from others for maximum flexibility.

### engine.py

Once you have created a configuration file (or choose one of the [templates](src/templates/)), you can run the scraping engine in the pipenv environment.

```bash
# from within a pipenv shell instance
$(venv) python engine.py <path to config file>

# from outside the pipenv environment
$ pipenv run python engine.py <path to config file>
```

## Writing your own scraper
