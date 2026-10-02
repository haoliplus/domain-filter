#!/usr/bin/env python3
"""Build native sing-box source rule-sets from this repository's Surge files.

No downloads: the checked-in Surge files remain the single source of truth.
Routing policies belong to the consuming configuration, not these rule-sets.
"""
import argparse
from collections import OrderedDict
import hashlib
import ipaddress
import json
from pathlib import Path
import re
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    'direct.txt', 'private.txt', 'proxy.txt', 'gfw.txt', 'Adblock4limbo_surge.list',
    'GoogleCN.list', 'Download.list', 'ai.list', 'KoreaMedia.list', 'JapanMedia.list',
    'MAX.list', 'GameRule.list', 'chat.list', 'ProxyGFWlist.list', 'apple.list',
    'telegramcidr.txt', 'cncidr.txt',
)
FIELDS = {'DOMAIN': 'domain', 'DOMAIN-SUFFIX': 'domain_suffix',
          'DOMAIN-KEYWORD': 'domain_keyword', 'IP-CIDR': 'ip_cidr',
          'IP-CIDR6': 'ip_cidr', 'PROCESS-NAME': 'process_name'}


def clean_line(line):
    line = line.strip()
    if not line or line.startswith(('#', ';', '//', '[')):
        return ''
    return re.split(r'\s+(?://|#|;)', line, maxsplit=1)[0].strip()


def convert(text):
    fields = OrderedDict()
    skipped = []
    source_count = 0
    for number, line in enumerate(text.lstrip('\ufeff').splitlines(), 1):
        line = clean_line(line)
        if not line:
            continue
        source_count += 1
        parts = [s.strip() for s in line.split(',')]
        kind = parts[0]
        if kind in ('URL-REGEX', 'USER-AGENT'):
            skipped.append({'line': number, 'type': kind,
                            'reason': 'no equivalent sing-box route matcher'})
            continue
        if kind not in FIELDS or len(parts) < 2 or not parts[1]:
            raise ValueError(f'line {number}: unsupported or malformed rule type {kind}')
        if any(p != 'no-resolve' for p in parts[2:]):
            raise ValueError(f'line {number}: unsupported rule option')
        value = parts[1]
        field = FIELDS[kind]
        if field == 'ip_cidr':
            value = str(ipaddress.ip_network(value, strict=False))
        elif field == 'process_name' and value.startswith('/'):
            field = 'process_path_regex' if value.endswith('/') else 'process_path'
            if value.endswith('/'):
                value = '^' + re.escape(value)
        fields.setdefault(field, OrderedDict())[value] = None
    # Separate fields into separate OR rules. Combining process_name with domain
    # in a single sing-box default rule would accidentally require BOTH to match.
    rules = [{key: list(values)} for key, values in fields.items()]
    if not rules:
        raise ValueError('rule-set has no supported conditions')
    return {'version': 3, 'rules': rules}, source_count, skipped


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, default=ROOT / 'surge')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'singbox/surge')
    args = parser.parse_args()
    # Convert everything before writing: unknown syntax must fail the update.
    converted = []
    manifest = {}
    for name in SOURCES:
        raw = (args.source_dir / name).read_bytes()
        result, count, skipped = convert(raw.decode('utf-8-sig'))
        filename = Path(name).stem + '.json'
        converted.append((filename, result))
        manifest[filename] = {
            'source': 'surge/' + name,
            'sha256': hashlib.sha256(raw).hexdigest(),
            'source_rules': count,
            'skipped': skipped,
        }
        print(f'{name}: {count} source rules, {len(skipped)} unsupported')
        for item in skipped:
            print(f'  WARNING: line {item["line"]}: {item["type"]} omitted (no native matcher)')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, result in converted:
        write_atomic(args.output_dir / filename, json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    write_atomic(args.output_dir / 'manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')


def write_atomic(path, text):
    data = text.encode('utf-8') if isinstance(text, str) else text
    with tempfile.NamedTemporaryFile(mode='wb', dir=path.parent,
                                     prefix='.'+path.name, delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(data)
            stream.close()
            temporary.chmod(0o644)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
