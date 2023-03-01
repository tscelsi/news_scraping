import pytest
from src.requestor import Requestor


def test_basic_context_management(httpx_mock):
    httpx_mock.add_response()
    with Requestor() as r:
        r.get('https://google.com')
    assert len(httpx_mock.get_requests()) == 1


def test_delay_between_requests(httpx_mock):
    httpx_mock.add_response()
    with Requestor(delay=10) as r:
        r.get('https://google.com')
        r.get('https://google.com')
    assert len(httpx_mock.get_requests()) == 2


def test_three_requests_works_correctly(httpx_mock):
    httpx_mock.add_response()
    with Requestor(delay=3) as r:
        r.get('https://google.com')
        r.get('https://google.com')
        r.get('https://google.com')
    assert len(httpx_mock.get_requests()) == 3
