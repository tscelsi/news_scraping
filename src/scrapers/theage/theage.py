import logging
from enum import Enum
from datetime import datetime

import httpx
from pydantic import ValidationError

from .model import TheAgeArticle
from models import Article
from requestor import Requestor
from consts import HEADERS
from exceptions import BaseException

class Categories(Enum):
    businessmarkets = '/business/markets'
    businesscompanies = '/business/companies'
    businesseconomy = '/business/the-economy'
    businessbankingnfinance = '/business/banking-and-finance'
    businessentrepreneurship = '/business/entrepreneurship'
    businessworkplace = '/business/workplace'


logger = logging.getLogger(__name__)

OUTLET = 'theage'
ARTICLE_BASE_HREF = 'https://api.theage.com.au/api/content/v0/assets/'


async def list_articles(client: httpx.AsyncClient, path: str | list[str], page_limit: int = 1, delay: int = 0) -> list[str]:
    """Because the pagination relies on synchronous requests, we simply add the delay between
    using our Requestor context.
    """
    try:
        _category = Categories[path]
    except KeyError as e:
        logger.error(f'list_articles;{path};{e}')
        raise BaseException(
            f'Categories should be one of {Categories.__members__.keys()}') from e
    url = 'https://api.theage.com.au/graphql'
    with Requestor(client=client, delay=delay) as R:
        r = await R.get(url, params={
            'query': 'query CategoryIndexPageAssetsQuery( $brand: String! $render: Render! $path: String! $first: Int! $offset: Int $types: [AssetType!]! ) { pageAssets: pageAssetsByNavigationPath(brand: $brand, render: $render, path: $path) { error { message type { __typename class ... on ErrorTypeInvalidRequest { fields { field message } } ... on ErrorTypeNotFound { class } ... on ErrorTypeUnavailable { retryable } } } page { ...PageFragment_pageData id } assetsConnection(first: $first, offset: $offset, types: $types) { ...AssetsConnectionFragment_showMoreData } } } fragment PageFragment_pageData on Page { config { ads { suppress } seo { canonical { brand path } description keywords title } } description id name redirect } fragment AssetsConnectionFragment_showMoreData on AssetsConnection { assets { ...AssetFragmentFragment_assetDataWithTag id } pageInfo { endCursor hasNextPage } } fragment AssetFragmentFragment_assetDataWithTag on Asset { ...AssetFragmentFragment_assetData tags { primaryTag { ...AssetFragment_tagFragment id } } } fragment AssetFragmentFragment_assetData on Asset { id asset { about byline duration headlines { headline } live totalImages } extensions label urls { canonical { path brand } external published { brisbanetimes { path } canberratimes { path } smh { path } theage { path } watoday { path } } } featuredImages { landscape16x9 { ...ImageFragment } landscape3x2 { ...ImageFragment } portrait2x3 { ...ImageFragment } square1x1 { ...ImageFragment } } assetType dates { modified published } sponsor { name } } fragment AssetFragment_tagFragment on AssetTagDetails { displayName urls { published { brisbanetimes { path } canberratimes { path } smh { path } theage { path } watoday { path } } } } fragment ImageFragment on Image { data { animated aspect autocrop cropWidth id mimeType offsetX offsetY zoom } }',
            'variables': '{"brand": "%s","first": 11,"offset": 0,"path": "%s","render": "WEB","types": ["article", "bespoke", "collection", "featureArticle", "gallery", "liveArticle"]}' % (OUTLET, _category.value)
        }, headers=HEADERS)
        if r.status_code != 200 or r.json()['data']['pageAssets']['error'] is not None:
            logger.error(f'list_articles;{r.status_code};{r.json()}')
            raise BaseException(f'Error getting articles for {_category.value}')
        main_data = r.json()['data']['pageAssets']['assetsConnection']
        article_urls = [ARTICLE_BASE_HREF + asset['id']
                        for asset in main_data['assets']]
        current_page_data = main_data
        pages_collected = 1
        while main_data['pageInfo']['hasNextPage'] and pages_collected < page_limit:
            pagination_key = main_data['pageInfo']['endCursor']
            r = await R.get("https://api.theage.com.au/graphql", params={
                "query": "query CategoryIndexMoreQuery( $brand: String! $count: Int! $path: String! $since: ID $types: [String!]! ) { assetsConnection: assetsConnectionByNavigationPath(brand: $brand, path: $path, count: $count, sinceID: $since, types: $types) { ...AssetsConnectionFragment_showMoreData } } fragment AssetsConnectionFragment_showMoreData on AssetsConnection { assets { ...AssetFragmentFragment_assetDataWithTag id } pageInfo { endCursor hasNextPage } } fragment AssetFragmentFragment_assetDataWithTag on Asset { ...AssetFragmentFragment_assetData tags { primaryTag { ...AssetFragment_tagFragment id } } } fragment AssetFragmentFragment_assetData on Asset { id asset { about byline duration headlines { headline } live totalImages } extensions label urls { canonical { path brand } external published { brisbanetimes { path } canberratimes { path } smh { path } theage { path } watoday { path } } } featuredImages { landscape16x9 { ...ImageFragment } landscape3x2 { ...ImageFragment } portrait2x3 { ...ImageFragment } square1x1 { ...ImageFragment } } assetType dates { modified published } sponsor { name } } fragment AssetFragment_tagFragment on AssetTagDetails { displayName urls { published { brisbanetimes { path } canberratimes { path } smh { path } theage { path } watoday { path } } } } fragment ImageFragment on Image { data { animated aspect autocrop cropWidth id mimeType offsetX offsetY zoom } }",
                "variables": '{"brand":"theage","count":10,"path":"%s","since":"%s","types":["article","bespoke","collection","featureArticle","gallery","liveArticle","video"]}' % (_category.value, pagination_key)
            }, headers=HEADERS)
            if r.status_code != 200:
                logger.error(f'list_articles;{r.status_code};{r.text}')
                raise BaseException(f'Error paginating articles for {_category.value}')
            current_page_data = r.json()['data']['assetsConnection']
            article_urls.extend([ARTICLE_BASE_HREF + asset['id']
                                for asset in current_page_data['assets']])
            pages_collected += 1
    return article_urls


async def get_article(client: httpx.AsyncClient, url: str) -> Article:
    response = await client.get(url, headers=HEADERS)
    try:
        article = TheAgeArticle(**response.json(), url=url)
        standardised_article = Article(
            outlet=OUTLET,
            url=url,
            created=datetime.strptime(article.dates.created, '%Y-%m-%dT%H:%M:%SZ'),
            modified=datetime.strptime(article.dates.modified, '%Y-%m-%dT%H:%M:%SZ'),
            published=datetime.strptime(article.dates.published, '%Y-%m-%dT%H:%M:%SZ'),
            title=article.asset.headlines.headline,
            body=article.asset.body,
            wordCount=article.asset.wordCount,
        )
    except ValidationError as e:
        logger.error(f'get_article;{e};{url}')
        return None
    return standardised_article
