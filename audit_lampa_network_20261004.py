#!/usr/bin/env python3
"""Focused static snapshot audit, NOT the Shadowrocket engine or a tvOS test.

python audit_lampa_network_20261004.py --cache /tmp/sr-lampa --write-results
Only public immutable list snapshots may be downloaded. No media/account requests.
GeoIP is an explicit scenario input. no-resolve does not initiate DNS.
"""
import argparse
import base64
import hashlib
import ipaddress
import json
import pathlib
import re
import subprocess
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
E = json.loads((ROOT / 'audit/lampa-network-evidence-20261004.json').read_text())
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--cache', type=pathlib.Path, default=pathlib.Path('/tmp/sr-lampa'))
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
            assert p[0] in {'DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD', 'IP-CIDR',
                            'RULE-SET', 'DOMAIN-SET', 'GEOIP', 'FINAL'}, (n, s)
            assert len(p) == (2 if p[0] == 'FINAL' else 4 if p[0] == 'IP-CIDR' else 3), s
            assert p[1 if p[0] == 'FINAL' else 2] in {'DIRECT', 'PROXY', 'REJECT'}, s
            if p[0] == 'IP-CIDR':
                ipaddress.ip_network(p[1], strict=True)
                assert p[3] == 'no-resolve'
            if p[0] in {'DOMAIN', 'DOMAIN-SUFFIX'}:
                assert re.fullmatch(r'[a-z0-9-]+(?:\.[a-z0-9-]+)*', p[1]), s
            if p[0].endswith('-SET'):
                assert p[1].startswith('https://raw.githubusercontent.com/') and '?' not in p[1]
            rules.append((n, s, p))
    assert sections == ['[General]', '[Rule]', '[Host]']
    assert rules[-1][1] == 'FINAL,PROXY' and sum(p[0] == 'FINAL' for _, _, p in rules) == 1
    assert len({s for _, s, _ in rules}) == len(rules), 'Exact duplicate'
    assert '\r' not in text and text.endswith('\n')
    return rules


def domain(host, kind, value):
    if kind == 'DOMAIN':
        return host == value
    if kind == 'DOMAIN-SUFFIX':
        return host == value or host.endswith('.' + value)
    return kind == 'DOMAIN-KEYWORD' and value in host


before = subprocess.check_output(['git', 'show', E['base'] + ':' + E['config']], cwd=ROOT).decode()
after = (ROOT / E['config']).read_text()
old, new = parse(before), parse(after)
assert hashlib.sha256(before.encode()).hexdigest() == E['baseline']['sha256']
tmdb = ['api.themoviedb.org', 'image.tmdb.org']
added = [f'DOMAIN,{h},PROXY' for h in tmdb]
assert [s for _, s, _ in new if s not in added] == [s for _, s, _ in old]
assert set(s for _, s, _ in new) - set(s for _, s, _ in old) == set(added)
assert len(old) == 187 and len(new) == 189
assert before.split('[Rule]')[0] == after.split('[Rule]')[0], 'General/update-url changed'
assert before.split('[Host]')[1] == after.split('[Host]')[1], 'Host changed'
anchor = 'DOMAIN,vod-images.onvesper.com,PROXY'
assert before.split(anchor)[0] == after.split(anchor)[0], 'Local/Apple/UFC changed'
assert before.split('# REJECT block')[1] == after.split('# REJECT block')[1], 'Other rules changed'
first_external = next(n for n, _, p in new if p[0].endswith('-SET'))
assert all(n < first_external for n, s, _ in new if s in added)
redundant = []
for i, (n, s, p) in enumerate(new):
    for m, t, q in new[:i]:
        if len(p) < 3 or len(q) < 3 or p[2:] != q[2:]:
            continue
        covered = q[0] == 'DOMAIN-SUFFIX' and p[0] in {'DOMAIN', 'DOMAIN-SUFFIX'} and domain(p[1], q[0], q[1])
        covered |= q[0] == 'DOMAIN-KEYWORD' and p[0] in {'DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD'} and q[1] in p[1]
        if p[0] == q[0] == 'IP-CIDR':
            a, b = ipaddress.ip_network(p[1]), ipaddress.ip_network(q[1])
            covered |= a.version == b.version and a.subnet_of(b)
        if covered:
            redundant.append([n, s, m, t])
assert not redundant, redundant

external, warnings, list_stats = {}, [], []
for meta in E['external_lists']:
    path = args.cache / (meta['key'] + '.txt')
    if not path.exists():
        with urllib.request.urlopen(meta['immutable_blob_url'], timeout=60) as response:
            data = base64.b64decode(json.load(response)['content'])
        path.write_bytes(data)
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == meta['sha256'], path
    assert hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == meta['git_blob']
    rows = active(data.decode('utf-8-sig'))
    list_stats.append({'key': meta['key'], 'active': len(rows), 'sha256': meta['sha256']})
    if meta['key'] == 'antifilter-download.txt':
        exact, suffix = {}, {}
        for n, s in rows:
            # Do not label internationalized domain names invalid or turn this
            # targeted audit into a cleanup of an unrelated upstream list.
            if ',' in s:
                warnings.append(f'DOMAIN-SET line {n}: unexpected comma {s!r}; native handling unknown')
                continue
            (suffix if s.startswith('.') else exact)[s.lstrip('.').lower()] = n
        external[meta['url']] = (exact, suffix)
    else:
        items = []
        for n, s in rows:
            p = s.split(',')
            assert p[0] in {'DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD', 'IP-CIDR', 'URL-REGEX', 'USER-AGENT'}, s
            assert not any(x in {'DIRECT', 'PROXY', 'REJECT'} for x in p[2:]), s
            net = ipaddress.ip_network(p[1], strict=True) if p[0] == 'IP-CIDR' else None
            assert p[2:] in ([], ['no-resolve']) if net else len(p) == 2
            items.append((n, s, p, net))
        external[meta['url']] = items


def trace(host, rules, geo_ru=None, known_ip=None, match_cached=False):
    try:
        addr, literal = ipaddress.ip_address(host), True
    except ValueError:
        addr, literal = ipaddress.ip_address(known_ip) if known_ip else None, False

    def match(p, net=None):
        if p[0] == 'IP-CIDR':
            # Default follows documented skipping of no-resolve for domain requests.
            # Optional cached mode is a sensitivity test, NOT a claim about native caching.
            if not literal and 'no-resolve' in p[2:] and not match_cached:
                return False
            return addr is not None and addr in (net or ipaddress.ip_network(p[1]))
        return not literal and domain(host, p[0], p[1])

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
            detail = next((f'entry {i}: {t}' for i, t, q, net in external[p[1]] if match(q, net)), None)
        elif p[0] == 'GEOIP':
            if geo_ru is None:
                return {'conditional': {'RU': trace(host, rules, True, known_ip, match_cached),
                                        'non-RU': trace(host, rules, False, known_ip, match_cached)}}
            detail = 'GeoIP RU scenario, not measured' if geo_ru else None
        elif p[0] == 'FINAL':
            return {'line': n, 'rule': s, 'policy': p[1], 'detail': 'No earlier modeled match'}
        elif match(p):
            detail = 'Literal address' if literal else 'Known-IP sensitivity' if p[0] == 'IP-CIDR' else 'Domain'
        if detail:
            return {'line': n, 'rule': s, 'policy': p[2], 'detail': detail}


def semantic(result):
    if 'conditional' in result:
        return {k: semantic(v) for k, v in result['conditional'].items()}
    return result['rule'], result['policy'], result['detail']


apple = '''apple.com appleid.apple.com setup.icloud.com guzzoni.apple.com gateway.push.apple.com
api.push.apple.com apps.apple.com music.apple.com apple-relay.cloudflare.com apple-relay.fastly-edge.com
cp4.cloudflare.com 17.57.146.140 17.57.146.141 17.57.146.135'''.split()
ufc = [x['host'] for x in json.loads((ROOT / 'audit/ufc-evidence-20260927.json').read_text())['rules']]
others = '''kino.pub www.kino.pub api.service-kp.com kinopub.fastcdn.pics cdn2cdn.com cdn2site.com
digital-cdn.net cdntogo.net aomikh.github.io raw.githubusercontent.com cdn.jsdelivr.net
lampa.mx s.fastcdn.pics yandex.ru mail.ru vk.com 2gis.ru aviasales.ru telegram.org whatsapp.com
chatgpt.com openai.com claude.ai gemini.google.com grok.com perplexity.ai youtube.com discord.com
ebay.com paypal.com bybit.com redotpay.com ads.doubleclick.net cloudflare.com other.fastcdn.pics
example.akamaized.net example.cloudfront.net example.fastly.net api.themoviedb.org.example.org
other.api.themoviedb.org other.image.tmdb.org image.tmdb.org.example.org ufc.com.example.org
unknown-lampa-audit.example 192.168.1.1 10.1.30.1 172.16.1.1 audit.local'''.split()
traces = []
for group, hosts in [('Apple', apple), ('UFC', ufc), ('TMDB', tmdb), ('Other', others)]:
    for host in hosts:
        a, b = trace(host, old), trace(host, new)
        if group in {'Apple', 'UFC', 'TMDB'}:
            assert b['policy'] == ('DIRECT' if group == 'Apple' else 'PROXY'), (host, b)
        if group != 'TMDB':
            assert semantic(a) == semantic(b), (host, a, b)
        traces.append({'host': host, 'group': group, 'before': a, 'after': b,
                       'changed': semantic(a) != semantic(b)})

scenarios = []
for host in tmdb + ufc:
    for ip, geo in [('95.173.136.70', True), ('93.184.216.34', False)]:
        for cached in [False, True]:
            a, b = trace(host, old, geo, ip, cached), trace(host, new, geo, ip, cached)
            assert b['policy'] == 'PROXY', (host, b)
            scenarios.append({'host': host, 'assumed_ip': ip, 'assumed_RU': geo,
                              'cached_sensitivity': cached, 'before': a, 'after': b})
assert trace('ads.doubleclick.net', new)['policy'] == 'REJECT'
assert trace('unknown-lampa-audit.example', new, False)['rule'] == 'FINAL,PROXY'
assert not domain('ufc.com.example.org', 'DOMAIN-SUFFIX', 'ufc.com')
excluded_line = next((n, s) for n, s in enumerate(after.splitlines(), 1) if s.startswith('tun-excluded-routes'))
excluded = [ipaddress.ip_network(s.strip()) for s in excluded_line[1].split('=', 1)[1].split(',')]
for h in ['224.0.0.251', '239.255.255.250', '192.168.1.1', '10.1.30.1', '172.16.1.1']:
    assert any(ipaddress.ip_address(h) in net for net in excluded)
skip = next(s for s in after.splitlines() if s.startswith('skip-proxy')).split('=', 1)[1]
assert set(s.strip() for s in skip.split(',')) == {'192.168.0.0/16', '10.0.0.0/8', '172.16.0.0/12', 'localhost', '*.local'}
result = {'base': E['base'], 'config_sha256': hashlib.sha256(after.encode()).hexdigest(),
          'rules_before': len(old), 'rules_after': len(new), 'added': added, 'removed': [],
          'apple_rules_unchanged': 75, 'ufc_rules_unchanged': 15, 'external_lists': list_stats,
          'warnings': warnings, 'traces': traces, 'known_ip_scenarios': scenarios,
          'multicast': {'line': excluded_line[0], 'rule': 'tun-excluded-routes: 224.0.0.0/4',
                        'policy': 'Excluded from tunnel', 'unchanged': True},
          'limits': ['Static subset, not native Shadowrocket parser/import or tvOS test.',
                     'Domain traces have no device IP/cache/GeoIP database; conditional branches are not measurements.',
                     'no-resolve skips domain requests by default; cached-IP variant is only sensitivity analysis.',
                     'URL-REGEX and USER-AGENT cannot be decided without actual observable URLs/headers.',
                     'DOMAIN-SET bare names modeled exact; leading dot suffix. Native malformed-line handling untested.',
                     'Internationalized-domain conversion and trailing-dot normalization are not emulated.',
                     'No home direct video tests, signed resource responses, DNS packet capture or router inspection.']}
if args.write_results:
    (ROOT / 'audit/lampa-network-results-20261004.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'rules': len(new), 'traces': len(traces), 'known_ip_scenarios': len(scenarios),
                  'sha256': result['config_sha256'], 'warnings': warnings}, ensure_ascii=False, indent=2))
