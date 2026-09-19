import csv
import pytest
from engine.csv_microservice import clean_batch


def test_reconcile_preserve_ids_and_missing(tmp_path):
    a=tmp_path/'a.csv';b=tmp_path/'b.csv'
    a.write_text('id,name,amount\n001, Widget ,10.00\n002,Other,\n\n')
    b.write_text('id,name,amount\n001,Widget,10.00\n003,Third,0\n')
    result=clean_batch([a,b],tmp_path/'out',True)
    assert result['input_rows']==5 and result['output_rows']==3
    assert result['removed_duplicates']==1 and result['removed_blank_rows']==1
    with (tmp_path/'out/cleaned.csv').open(encoding='utf-8-sig') as f: rows=list(csv.reader(f))
    assert rows[1]==['001','Widget','10.00'] and rows[2][-1]==''
    assert a.read_text().startswith('id,name,amount\n001, Widget')


def test_no_implicit_dedup_or_overwrite(tmp_path):
    a=tmp_path/'a.csv';a.write_text('id\n001\n001\n')
    assert clean_batch([a],tmp_path/'out')['output_rows']==2
    with pytest.raises(FileExistsError): clean_batch([a],tmp_path/'out')


@pytest.mark.parametrize('text',['id,id\n1,2\n','id\n=1+1\n','id\n1,2\n','id\n'+'1\n'*5001])
def test_invalid_or_oversized_input(tmp_path,text):
    a=tmp_path/'a.csv';a.write_text(text)
    with pytest.raises(ValueError):clean_batch([a],tmp_path/'out')
    assert not (tmp_path/'out').exists()


def test_mismatched_columns(tmp_path):
    a=tmp_path/'a.csv';b=tmp_path/'b.csv';a.write_text('id\n001\n');b.write_text('name\n001\n')
    with pytest.raises(ValueError):clean_batch([a,b],tmp_path/'out')


def test_formula_like_headers_rejected(tmp_path):
    a=tmp_path/'a.csv';a.write_text('=1+1\nvalue\n')
    with pytest.raises(ValueError):clean_batch([a],tmp_path/'out')
