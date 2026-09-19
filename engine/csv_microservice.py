"""Bounded CSV cleanup; originals and values are preserved, no inferred corrections."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from time import perf_counter


def clean_batch(inputs, output, deduplicate=False):
    started = perf_counter()
    paths = [Path(p) for p in inputs]
    if not 1 <= len(paths) <= 3 or len({p.resolve() for p in paths}) != len(paths):
        raise ValueError('Provide 1–3 distinct CSV files')
    rows, headers, seen, log, sources = [], None, {}, [], []
    duplicates = blanks = input_count = 0
    for path in paths:
        if path.suffix.lower() != '.csv' or path.is_symlink() or path.stat().st_size > 5_000_000:
            raise ValueError('Only regular UTF-8 CSV files up to 5 MB each')
        if path.name.startswith(('=', '+', '-', '@')):
            raise ValueError('Unsafe source filename')
        sources.append({'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        with path.open(encoding='utf-8-sig', newline='') as f:
            reader = csv.reader(f, strict=True)
            raw_headers = next(reader, [])
            current = [h.strip() for h in raw_headers]
            if not current or len(current) > 20 or any(not h for h in current) or len(set(current)) != len(current):
                raise ValueError('Require 1–20 uniquely named columns')
            if headers is not None and current != headers:
                raise ValueError('Column names and order must match; no guessed mapping')
            if any(h.startswith(('=', '+', '-', '@')) for h in current):
                raise ValueError('Formula-like column headers require review')
            headers = current
            if current != raw_headers:
                log.append([path.name, 1, 'trim_headers', 'Header whitespace removed'])
            for line, row in enumerate(reader, 2):
                input_count += 1
                if input_count > 5000:
                    raise ValueError('5,000 total input rows maximum')
                if not row or all(not cell.strip() for cell in row):
                    blanks += 1
                    log.append([path.name, line, 'blank_row', 'Excluded empty row'])
                    continue
                if len(row) != len(headers):
                    raise ValueError(f'Wrong field count at input line {line}')
                cleaned = [cell.strip() for cell in row]
                # No spreadsheet formulas or implicit numeric/date coercion.
                if any(cell.startswith(('=', '+', '-', '@')) for cell in cleaned):
                    raise ValueError('Formula-like or signed fields require separate review')
                if cleaned != row:
                    log.append([path.name, line, 'trim_cells', 'Leading/trailing whitespace removed'])
                if any(cell == '' for cell in cleaned):
                    log.append([path.name, line, 'missing_value', 'Preserved blank cell; no invented value'])
                key = tuple(cleaned)
                if deduplicate and key in seen:
                    duplicates += 1
                    log.append([path.name, line, 'duplicate', f'Identical cleaned row; first occurrence {seen[key]}'])
                    continue
                seen.setdefault(key, f'{path.name}:{line}')
                rows.append(cleaned)
    if input_count != len(rows) + duplicates + blanks:
        raise RuntimeError('Row reconciliation failed')
    out = Path(output)
    out.mkdir(parents=True, exist_ok=False, mode=0o700)
    for name, columns, records in [('cleaned.csv', headers, rows), ('changes.csv', ['file','source_row','action','detail'], log)]:
        with (out/name).open('w',encoding='utf-8-sig',newline='') as f:
            writer = csv.writer(f); writer.writerow(columns); writer.writerows(records)
        (out/name).chmod(0o600)
    audit = {'synthetic': False, 'input_rows':input_count,'output_rows':len(rows),
             'removed_duplicates':duplicates,'removed_blank_rows':blanks,
             'deduplication_requested':deduplicate,'row_balance_passed':True,
             'sources':sources,'processing_seconds':round(perf_counter()-started,4),
             'note':'Import CSV columns as text to preserve leading zeros. No dates or amounts inferred.'}
    (out/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
    (out/'audit.json').chmod(0o600)
    return audit


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='Fixed-scope CSV cleanup')
    parser.add_argument('inputs',nargs='+')
    parser.add_argument('--out',required=True)
    parser.add_argument('--deduplicate',action='store_true',help='Explicitly authorize exact-row removal after trimming')
    args=parser.parse_args()
    print(json.dumps(clean_batch(args.inputs,args.out,args.deduplicate),ensure_ascii=False))
