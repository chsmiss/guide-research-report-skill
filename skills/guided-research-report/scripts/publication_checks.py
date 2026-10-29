"""Publication references and declared display-value checks (standard library).

Run --help for commands. Body means exported reader text before bibliography.
Mechanical checks do not establish source truth, semantic readability, numeric
coverage, or visual quality. No input file is modified.
"""
import argparse
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
import json
from pathlib import Path
import re
import sys

STABLE_CITATION = re.compile(r'\[([A-Za-z]+\d+)\]')
NUMBERED_CITATION = re.compile(r'\[(\d+)\]')


def unique(items):
    return list(dict.fromkeys(items))


def compact(text):
    return re.sub(r'\s+', '', text)


def decimal(value):
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError('Expected a finite decimal number') from exc
    if not result.is_finite():
        raise ValueError('Expected a finite decimal number')
    return result


def format_value(value, decimals=2, percent=False):
    """Use the same formatter in the report builder and display-value record."""
    if type(decimals) is not int or not 0 <= decimals <= 12:
        raise ValueError('decimals must be an integer from 0 to 12')
    number = decimal(value)
    with localcontext() as ctx:
        ctx.prec = max(60, len(number.as_tuple().digits) + abs(number.adjusted()) + decimals + 4)
        rounded = number.quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP)
    if rounded == 0:
        rounded = rounded.copy_abs()
    return f'{rounded:.{decimals}f}' + ('%' if percent else '')


def calculate(kind, inputs):
    values = [decimal(v) for v in inputs]
    with localcontext() as ctx:
        ctx.prec = 60
        if kind == 'number' and len(values) == 1:
            return values[0]
        if kind == 'share_pct' and len(values) == 2:
            if values[1] == 0:
                raise ValueError('share denominator is zero')
            return values[0] / values[1] * 100
        if kind == 'growth_pct' and len(values) == 2:
            if values[0] == 0:
                raise ValueError('growth base is zero')
            return (values[1] / values[0] - 1) * 100
    raise ValueError('Use number [value], share_pct [numerator, denominator], or growth_pct [old, new]')


def prepare_references(sources, body):
    """Keep stable source IDs; make a separate publication map by first use."""
    if not isinstance(sources, list):
        raise ValueError('sources must be a list of source objects')
    by_id = {}
    for source in sources:
        sid = source.get('id', '')
        if not re.fullmatch(r'[A-Za-z]+\d+', sid) or not source.get('title'):
            raise ValueError('Every source needs a letter/digit ID and a title')
        if sid in by_id:
            raise ValueError('Duplicate source ID: ' + sid)
        by_id[sid] = source
    if NUMBERED_CITATION.search(body):
        raise ValueError('Prepare from stable-ID body text before adding publication numbers')
    order = unique(STABLE_CITATION.findall(body))
    unknown = [sid for sid in order if sid not in by_id]
    if unknown:
        raise ValueError('Unknown cited sources: ' + ', '.join(unknown))
    refs = [dict(by_id[sid], number=n, source_id=sid) for n, sid in enumerate(order, 1)]
    numbers = {row['source_id']: row['number'] for row in refs}
    rendered = STABLE_CITATION.sub(lambda m: '[' + str(numbers[m.group(1)]) + ']', body)
    return {
        'schema_version': 1, 'references': refs,
        'unused_source_ids': [sid for sid in by_id if sid not in numbers],
        'scope': 'First-use numbering of stable citation tokens; source truth not checked'
    }, rendered


def check_numbers(records, body):
    errors, warnings, results = [], [], []
    seen = set()
    if not isinstance(records, list):
        return ['Display values must be a list'], [], []
    for index, row in enumerate(records, 1):
        key = row.get('id', '') if isinstance(row, dict) else ''
        label = key or f'row-{index}'
        try:
            if not key or key in seen:
                raise ValueError('Use a unique nonempty metric id')
            seen.add(key)
            kind = row['kind']
            value = calculate(kind, row['inputs'])
            places = row['decimals']
            expected = format_value(value, places, percent=(kind != 'number'))
            shown = row['display']
            if shown != expected:
                errors.append(f'{label}: display {shown!r}, expected {expected!r}')
            context = row.get('context', '')
            if not context or compact(shown) not in compact(context) or compact(context) not in compact(body):
                errors.append(f'{label}: display context is absent or does not contain the declared display')
            result = {'id': key, 'expected_display': expected, 'context': context}
            if kind != 'number':
                if 'shown_inputs' not in row:
                    errors.append(f'{label}: declare shown_inputs to check reader-side arithmetic')
                else:
                    reader_value = calculate(kind, row['shown_inputs'])
                    reader_display = format_value(reader_value, places, percent=True)
                    result['shown_input_result'] = reader_display
                    if reader_display != expected:
                        note = row.get('rounding_note', '').strip()
                        if note and compact(note) in compact(body):
                            warnings.append(f'{label}: reader-side result {reader_display}; rounding basis disclosed in text')
                        else:
                            errors.append(f'{label}: shown inputs yield {reader_display}; add precision or disclose rounding basis')
            results.append(result)
        except (KeyError, ValueError, TypeError, AttributeError, InvalidOperation, OverflowError) as exc:
            errors.append(f'{label}: {exc}')
    return errors, warnings, results


def editorial_hints(body):
    """Only generate location-specific review leads, never readability grades."""
    hints, seen = [], {}
    blocks = [s.strip() for s in re.split(r'\n\s*\n', body) if s.strip()]
    for number, block in enumerate(blocks, 1):
        markers = re.findall(r'(?<![A-Za-z0-9_-])[A-Za-z0-9_-]+\.(?:json|py)(?![A-Za-z0-9_])|(?<![A-Za-z0-9_])python3?\s+[A-Za-z0-9_./-]+|(?<![A-Za-z0-9_])qa(?=/|目录)|/Users/[^\s，。；（）]+', block)
        if markers:
            hints.append({'block': number, 'type': 'production_detail_candidate',
                          'excerpt': block[:180], 'markers': unique(markers),
                          'action': 'Place production instructions in the research package; retain technical content needed to explain the research object.'})
        normalized = compact(NUMBERED_CITATION.sub('', block))
        if len(normalized) >= 40 and normalized in seen:
            hints.append({'block': number, 'earlier_block': seen[normalized], 'type': 'exact_repetition',
                          'excerpt': block[:180], 'action': 'Review what this repetition adds for the reader.'})
        seen[normalized] = number
    for term in ['分模式', '待核实', '条件更新', '值得进一步研究']:
        positions = [i for i, block in enumerate(blocks, 1) if term in block]
        if len(positions) >= 3:
            hints.append({'type': 'recurring_general_guidance', 'term': term, 'blocks': positions,
                          'action': 'Review current findings and distinct section tasks; preserve material local limits.'})
    return hints


def check_publication(body, mapping, values=None):
    errors, warnings = [], []
    refs = mapping.get('references', [])
    if not isinstance(refs, list):
        raise ValueError('references must be a list')
    numbered = [r.get('number') for r in refs]
    stable_ids = [r.get('source_id') for r in refs]
    if any(type(n) is not int for n in numbered) or numbered != list(range(1, len(refs) + 1)):
        errors.append('Publication reference list must be ordered and continuous from 1')
    if any(not sid for sid in stable_ids) or len(set(stable_ids)) != len(stable_ids):
        errors.append('Publication map must identify each stable source once')
    for ref in refs:
        if not ref.get('title'):
            errors.append('Every publication reference needs its source title')
    stable = STABLE_CITATION.findall(body)
    if stable:
        errors.append('Stable source tokens remain in publication body: ' + ', '.join(unique(stable)))
    used = unique(int(n) for n in NUMBERED_CITATION.findall(body))
    if used != list(range(1, len(refs) + 1)):
        errors.append('Body first-use order or coverage differs from the publication map')
    numeric_results = []
    if values is not None:
        numeric_errors, numeric_warnings, numeric_results = check_numbers(values, body)
        errors.extend(numeric_errors)
        warnings.extend(numeric_warnings)
        if not values:
            warnings.append('Display-value list is empty; numeric coverage remains unverified')
    else:
        warnings.append('Display-value checks not supplied; numeric coverage remains unverified')
    return {
        'mechanical_status': 'failed' if errors else 'passed',
        'editorial_status': 'manual_review_required',
        'reference_count': len(refs), 'numeric_record_count': len(numeric_results),
        'errors': errors, 'warnings': warnings, 'numeric_results': numeric_results,
        'editorial_hints': editorial_hints(body),
        'scope': 'Supplied body, publication map and declared numeric contexts only',
        'remaining_checks': ['Source truth and inference', 'Completeness of declared numeric records',
                             'Semantic repetition and reader comprehension',
                             'Bibliography rendering and hyperlink targets in the final artifact',
                             'Every final rendered page and text extraction']
    }


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_json_new(path, obj):
    with Path(path).open('x', encoding='utf-8') as handle:
        json.dump(obj, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write('\n')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prepare = commands.add_parser('prepare-references', help='Create first-use reference map and numbered body in a new directory')
    prepare.add_argument('--sources', required=True)
    prepare.add_argument('--body', required=True)
    prepare.add_argument('--output-dir', required=True)
    check = commands.add_parser('check', help='Check exported body plus map and optional declared display values')
    check.add_argument('--body', required=True)
    check.add_argument('--references', required=True)
    check.add_argument('--numbers')
    check.add_argument('--output', required=True)
    args = parser.parse_args(argv)
    try:
        body = Path(args.body).read_text(encoding='utf-8')
        if args.command == 'prepare-references':
            mapping, text = prepare_references(read_json(args.sources), body)
            out = Path(args.output_dir)
            out.mkdir(parents=True, exist_ok=False)
            write_json_new(out/'citation_map.json', mapping)
            with (out/'numbered_body.txt').open('x', encoding='utf-8') as handle:
                handle.write(text)
            print(json.dumps({'status': 'numbered', 'references': len(mapping['references']),
                              'unused_source_ids': mapping['unused_source_ids']}, ensure_ascii=False))
            return 0
        records = read_json(args.numbers)['values'] if args.numbers else None
        result = check_publication(body, read_json(args.references), records)
        write_json_new(args.output, result)
        print(json.dumps({'mechanical_status': result['mechanical_status'], 'errors': result['errors'],
                          'editorial_hints': len(result['editorial_hints']),
                          'editorial_status': result['editorial_status']}, ensure_ascii=False))
        return 1 if result['errors'] else 0
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as exc:
        print(f'publication_checks: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
