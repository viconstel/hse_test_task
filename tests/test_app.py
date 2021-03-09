import sys
sys.path.append('../')
from bin.app import app, parse_dates, preprocess_dataframe
import pytest
import pandas as pd


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_upload_get_method(client):
    response = client.get('/upload/')
    assert 200 == response.status_code
    assert 'text/html' == response.content_type


def test_parse_dates():
    df = pd.DataFrame({'date': ['2020-01-01', '02.05.2000']})
    result = parse_dates(df)
    assert isinstance(result, pd.DataFrame)
    assert 'datetime64[ns]' == result.date.dtype
    assert 2 == len(df)


def test_preprocess_dataframe_with_no_args():
    df = pd.DataFrame({'date': ['2020-01-01', '02.05.2000']})
    result = preprocess_dataframe(df, {})
    assert isinstance(result, pd.DataFrame)
    assert 'datetime64[ns]' == result.date.dtype
    assert 2 == len(df)


def test_preprocess_dataframe_column_names():
    df = pd.DataFrame({'date': ['2020-01-01', '02.05.2000']})
    result = preprocess_dataframe(df, args={'col_names': ['new_date']})
    assert isinstance(result, pd.DataFrame)
    assert 'date' not in result.columns
    assert 'new_date' in result.columns
    assert 'datetime64[ns]' == result.new_date.dtype
    assert 2 == len(df)


def test_preprocess_dataframe_column_names():
    df = pd.DataFrame({'id': [1, 2, 3]})
    result = preprocess_dataframe(df, args={'type': {'id': float}})
    assert isinstance(result, pd.DataFrame)
    assert 3 == len(df)
    assert 'float' == result.id.dtype


@pytest.fixture()
def wrong_format_file(tmpdir):
    text = 'qwerty'
    file = tmpdir.join('tmp.txt')
    file.write(text)
    return file


def test_upload_post_wrong_format_error(client, wrong_format_file):
    response = client.post('/upload/', data=wrong_format_file,
                           headers={'Content-Type': 'multipart/form-data'})

    assert 422 == response.status_code
    assert 'application/json' == response.content_type

