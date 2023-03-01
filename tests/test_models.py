import json
import pytest
from src.consts import TEST_DIR
from src.scrapers.theage.model import TheAgeArticle

@pytest.fixture
def article():
    with open(TEST_DIR / "theage_article.json") as f:
        return json.load(f)

def test_convert_to_article_form(article):
    article = TheAgeArticle(**article)
    TheAgeArticle.article_convert_map()
