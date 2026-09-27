#!/usr/bin/env python3
"""Focused snapshot checks, NOT a Shadowrocket parser or a tvOS network test.

python audit_ufc_20260927.py --cache /tmp/sr-ufc-audit --write-results
Missing external snapshots are fetched by immutable Git blob and SHA256 checked.
No DNS lookup, CNAME inference, fake-IP, real GeoIP database or URL/UA emulation.
"""
import argparse
import base64
import collections
import hashlib
import ipaddress
import json
import pathlib
import re
import subprocess
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
E = json.loads((ROOT / 'audit/ufc-evidence-20260927.json').read_text())
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--cache', type=pathlib.Path, default=pathlib.Path('/tmp/sr-ufc-audit'))
ap.add_argument('--write-results', action='store_true')
args = ap.parse_args()
args.cache.mkdir(parents=True, exist_ok=True)


def active(text):
    return [(n, s.strip()) for n, s in enumerate(text.splitlines(), 1)
            if s.strip() and not s.lstrip().startswith('#')]


def parse(text):
    section, sections, rules = None, [], []
    for n, s in active(text):
        if s.startswith('['):
            section = s
            sections.append(s)
        elif section == '[Rule]':
            p = s.split(',')
            assert all(x and x == x.strip() for x in p), (n, s)
            assert p[0] in {'DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD',
                            'IP-CIDR', 'RULE-SET', 'DOMAIN-SET', 'GEOIP', 'FINAL'}, (n, s)
            assert len(p) == (2 if p[0] == 'FINAL' else 4 if p[0] == 'IP-CIDR' else 3), s
            assert p[1 if p[0] == 'FINAL' else 2] in {'DIRECT', 'PROXY', 'REJECT'}, s
            if p[0] == 'IP-CIDR':
                ipaddress.ip_network(p[1], strict=True)
                assert p[3] == 'no-resolve', s
            if p[0] in {'DOMAIN', 'DOMAIN-SUFFIX'}:
                assert re.fullmatch(r'[a-z0-9-]+(?:\.[a-z0-9-]+)*', p[1]), s
            if p[0] in {'RULE-SET', 'DOMAIN-SET'}:
                assert p[1].startswith('https://raw.githubusercontent.com/') and '?' not in p[1], s
            rules.append((n, s, p))
    assert sections == ['[General]', '[Rule]', '[Host]'], sections
    assert rules[-1][1] == 'FINAL,PROXY'
    assert sum(p[0] == 'FINAL' for _, _, p in rules) == 1
    assert len({s for _, s, _ in rules}) == len(rules), 'Exact duplicate'
    assert '\r' not in text and text.endswith('\n')
    return rules


def domain_match(host, kind, value):
    if kind == 'DOMAIN':
        return host == value
    if kind == 'DOMAIN-SUFFIX':
        return host == value or host.endswith('.' + value)
    return kind == 'DOMAIN-KEYWORD' and value in host


def covers(earlier, later):
    if earlier == later:
        return True
    if len(earlier) < 3 or len(later) < 3 or earlier[2:] != later[2:]:
        return False
    if earlier[0] == 'DOMAIN-SUFFIX' and later[0] in {'DOMAIN', 'DOMAIN-SUFFIX'}:
        return domain_match(later[1], earlier[0], earlier[1])
    if earlier[0] == later[0] == 'IP-CIDR':
        a, b = ipaddress.ip_network(earlier[1]), ipaddress.ip_network(later[1])
        return a.version == b.version and b.subnet_of(a)
    if earlier[0] == 'DOMAIN-KEYWORD' and later[0] in {'DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD'}:
        return earlier[1] in later[1]
    return False


before = subprocess.check_output(['git', 'show', E['base'] + ':' + E['config']], cwd=ROOT).decode()
after = (ROOT / E['config']).read_text()
old, new = parse(before), parse(after)
assert hashlib.sha256(before.encode()).hexdigest() == E['baseline']['sha256']
assert before.split('[Rule]')[0] == after.split('[Rule]')[0], 'General/update-url changed'
assert before.split('[Host]')[1] == after.split('[Host]')[1], 'Host changed'
marker = '# Apple ecosystem — ALWAYS DIRECT'
apple_before = before.split(marker)[1].split('# REJECT block')[0].rsplit('# -------------------------------', 1)[0]
apple_after = after.split(marker)[1].split('# UFC / UFC Fight Pass')[0].rsplit('# -------------------------------', 1)[0]
assert apple_before == apple_after, 'Apple block changed'
assert before.split(marker)[0] == after.split(marker)[0], 'Local rules changed'
assert [(s, p) for _, s, p in new if s in {x[1] for x in old}] == [(s, p) for _, s, p in old if s not in E['removed_rules']]
added = [s for _, s, _ in new if s not in {r[1] for r in old}]
expected = [f"{x['type']},{x['host']},PROXY" for x in E['rules']]
assert set(added) == set(expected) and len(added) == 15
assert len(old) == 175 and len(new) == 187
ufc_start = after.splitlines().index('# UFC / UFC Fight Pass — PROXY') + 1
external_start = next(n for n, _, p in new if p[0] == 'RULE-SET')
apple = [(n, s, p) for n, s, p in new if after.splitlines().index(marker) + 1 < n < ufc_start]
assert len(apple) == 75 and all(p[2] == 'DIRECT' for _, _, p in apple)
assert all(ufc_start < n < external_start for n, s, _ in new if s in added)
removed = []
for n, s, p in old:
    if s not in E['removed_rules']:
        continue
    replacement = next((r for r in old if r[0] < n and covers(r[2], p)), None)
    assert replacement and replacement[1] in {r[1] for r in new}, s
    removed.append({'rule': s, 'old_line': n, 'replacement': replacement[1],
                    'replacement_old_line': replacement[0],
                    'replacement_new_line': next(r[0] for r in new if r[1] == replacement[1])})
redundant = [(n, s, m, t) for i, (n, s, p) in enumerate(new)
             for m, t, q in new[:i] if covers(q, p)]
assert not redundant, redundant

external, warnings = {}, []
for meta in E['external_lists']:
    path = args.cache / (meta['key'] + '.txt')
    if not path.exists():
        with urllib.request.urlopen(meta['immutable_blob_url'], timeout=60) as response:
            blob = json.load(response)
        path.write_bytes(base64.b64decode(blob['content']))
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == meta['sha256'], path
    rows = active(data.decode('utf-8-sig'))
    if meta['key'] == 'external-198':
        exact, suffix = {}, {}
        for n, s in rows:
            if ',' in s:
                warnings.append(f'DOMAIN-SET entry {n}: {s!r}; native error handling unknown')
                continue
            (suffix if s.startswith('.') else exact)[s.lstrip('.')] = n
        external[meta['url']] = (exact, suffix)
    else:
        items = []
        for n, s in rows:
            p = s.split(',')
            assert not any(x in {'DIRECT', 'PROXY', 'REJECT'} for x in p[2:]), s
            assert p[0] in {'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD', 'IP-CIDR', 'USER-AGENT', 'URL-REGEX'}, s
            if p[0] == 'IP-CIDR':
                ipaddress.ip_network(p[1])
                assert p[2:] in [[], ['no-resolve']], s
            else:
                assert len(p) == 2, s
            items.append((n, s, p))
        external[meta['url']] = items


def trace(host, rules, geo_ru=None, known_ip=None):
    try:
        address = ipaddress.ip_address(host)
        literal = True
    except ValueError:
        address = ipaddress.ip_address(known_ip) if known_ip else None
        literal = False
    def matches(p):
        if p[0] == 'IP-CIDR':
            return address is not None and address in ipaddress.ip_network(p[1])
        return not literal and domain_match(host, p[0], p[1])
    for n, s, p in rules:
        detail = None
        if p[0] == 'DOMAIN-SET' and not literal:
            exact, suffix = external[p[1]]
            if host in exact:
                detail = f'entry {exact[host]}: {host}'
            else:
                for i in range(len(host.split('.'))):
                    v = '.'.join(host.split('.')[i:])
                    if v in suffix:
                        detail = f'entry {suffix[v]}: .{v}'
                        break
        elif p[0] == 'RULE-SET':
            detail = next((f'entry {i}: {t}' for i, t, q in external[p[1]] if matches(q)), None)
        elif p[0] == 'GEOIP':
            if geo_ru is None:
                other = trace(host, rules, geo_ru=False, known_ip=known_ip)
                policy = p[2] if p[2] == other['policy'] else p[2] + ' if RU; otherwise ' + other['policy']
                return {'line': n, 'rule': s + ' [if RU]; ' + other['rule'] + ' [otherwise]',
                        'policy': policy, 'detail': f'Device GeoIP unknown; non-RU branch line {other["line"]}'}
            detail = 'GeoIP RU assumed' if geo_ru else None
        elif p[0] == 'FINAL':
            return {'line': n, 'rule': s, 'policy': p[1], 'detail': 'GeoIP non-RU assumed'}
        elif matches(p):
            detail = 'Literal IP' if literal else 'Known cached IP' if p[0] == 'IP-CIDR' else 'Domain'
        if detail:
            return {'line': n, 'rule': s, 'policy': p[2], 'detail': detail}


apple_hosts = '''apple.com setup.icloud.com guzzoni.apple.com api.push.apple.com appleid.apple.com
music.apple.com apps.apple.com apple-relay.cloudflare.com apple-relay.fastly-edge.com cp4.cloudflare.com
17.57.146.140 17.57.146.141 17.57.146.135'''.split()
others = '''yandex.ru market.yandex.ru api.market.yandex.ru mail.ru vk.com 2gis.ru 2gis.com aviasales.ru
aviasales.com t.me telegram.org whatsapp.com graph.facebook.com openai.com chatgpt.com claude.ai
gemini.google.com grok.com perplexity.ai youtube.com discord.com ebay.com paypal.com bybit.com
redotpay.com helpcenter.redotpay.com kino.pub api.service-kp.com 192.168.1.1 10.1.30.1 172.16.1.1 audit.local
ufc.com.example.org notufc.com other.imggaming.com other.onvesper.com cloudflare.com example.akamaized.net
example.cloudfront.net example.fastly.net'''.split()
ufc_hosts = [x['host'] for x in E['rules']] + ['www.ufc.com', 'jp.ufc.com', 'kr.ufc.com',
             'www.ufcfightpass.com', 'app.ufcfightpass.com', 'app.ufc.tv', 'us.ufcespanol.com']
cases = [(h, 'Apple') for h in apple_hosts] + [(h, 'UFC') for h in ufc_hosts] + [(h, 'Other/local/boundary') for h in others]
traces = []
for h, group in cases:
    a, b = trace(h, old), trace(h, new)
    if group == 'Apple':
        assert b['policy'] == a['policy'] == 'DIRECT'
    elif group == 'UFC':
        assert b['policy'] == 'PROXY' and b['rule'] in added
    else:
        assert (a['rule'], a['policy']) == (b['rule'], b['policy']), h
    traces.append({'host': h, 'group': group, 'before': a, 'after': b,
                   'changed_policy': a['policy'] != b['policy'], 'changed_first_rule': a['rule'] != b['rule']})
scenarios = []
for h in ufc_hosts:
    for country, ip, ru in [('RU assumed', '95.173.136.70', True), ('non-RU assumed', '93.184.216.34', False)]:
        t = trace(h, new, geo_ru=ru, known_ip=ip)
        assert t['policy'] == 'PROXY' and t['rule'] in added
        scenarios.append({'host': h, 'ip': ip, 'geo_assumption': country, 'result': t})
assert not domain_match('ufc.com.example.org', 'DOMAIN-SUFFIX', 'ufc.com')
assert not domain_match('notufc.com', 'DOMAIN-SUFFIX', 'ufc.com')
for name in ['ufc.com.example.org', 'notufc.com', 'unknown-ufc-audit.example']:
    for ru in [False, True]:
        a, b = trace(name, old, ru), trace(name, new, ru)
        assert (a['rule'], a['policy']) == (b['rule'], b['policy'])
assert trace('unknown-ufc-audit.example', new, False)['rule'] == 'FINAL,PROXY'
traces.append({'host': 'unknown-ufc-audit.example [GeoIP non-RU]', 'group': 'Fallback',
               'before': trace('unknown-ufc-audit.example', old, False),
               'after': trace('unknown-ufc-audit.example', new, False),
               'changed_policy': False, 'changed_first_rule': False})
excluded_line = next((n, s) for n, s in enumerate(after.splitlines(), 1) if s.startswith('tun-excluded-routes'))
excluded = [ipaddress.ip_network(x.strip()) for x in excluded_line[1].split('=', 1)[1].split(',')]
assert any(ipaddress.ip_address('224.0.0.251') in net for net in excluded)
skip_line = next(s for s in after.splitlines() if s.startswith('skip-proxy'))
assert set(x.strip() for x in skip_line.split('=', 1)[1].split(',')) == {
    '192.168.0.0/16', '10.0.0.0/8', '172.16.0.0/12', 'localhost', '*.local'}
for h in ['192.168.1.1', '10.1.30.1', '172.16.1.1']:
    assert any(ipaddress.ip_address(h) in net for net in excluded)
traces.append({'host': '224.0.0.251', 'group': 'Tunnel bypass',
               'after': {'line': excluded_line[0], 'rule': 'tun-excluded-routes = …224.0.0.0/4…',
                         'policy': 'Excluded from tunnel', 'detail': 'General mechanism, before Rule processing'},
               'changed_policy': False, 'changed_first_rule': False})
result = {'base': E['base'], 'sha256': hashlib.sha256(after.encode()).hexdigest(),
          'rules_before': len(old), 'rules_after': len(new), 'apple_rules': len(apple),
          'added': added, 'removed': removed, 'external_lists': len(external), 'warnings': warnings,
          'traces': traces, 'ufc_ip_scenarios': scenarios,
          'limits': ['Static subset model, not native Shadowrocket; no live tvOS import/playback.',
                     'No URL-REGEX/USER-AGENT without URL/headers; no live DNS, CNAME, fake-IP or device GeoIP.',
                     'no-resolve never creates a DNS lookup; known_ip is an explicit test input, not an observed cache.',
                     'DOMAIN-SET naked names modeled exact, leading dot suffix; native importer unverified.',
                     'Local/upstream tunnel bypass and router VPN are outside the rule model.',
                     'Shared-IP traffic without an original hostname cannot be attributed to UFC.']}
if args.write_results:
    (ROOT / 'audit/ufc-results-20260927.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k not in {'traces', 'ufc_ip_scenarios', 'added'}}, ensure_ascii=False, indent=2))
print(f'Traces: {len(traces)}; UFC known-IP scenarios: {len(scenarios)}')
