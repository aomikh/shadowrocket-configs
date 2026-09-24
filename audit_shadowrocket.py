#!/usr/bin/env python3
"""Snapshot-based static checks, NOT a Shadowrocket/tvOS emulator.

Run from this checkout: python audit_shadowrocket.py --cache /tmp/sr-audit
Missing public rule snapshots are fetched and verified against pinned SHA256.
No live DNS, GeoIP database, CNAME inference, HTTP headers or device testing.
"""
import argparse
import base64
import collections
import hashlib
import ipaddress
import json
import pathlib
import subprocess
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
E = json.loads((ROOT / 'audit/evidence-20260924.json').read_text())
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--cache', type=pathlib.Path, default=pathlib.Path('/tmp/sr-audit'))
ap.add_argument('--write-results', action='store_true')
args = ap.parse_args()
args.cache.mkdir(parents=True, exist_ok=True)


def source(meta):
    path = args.cache / (meta['key'] + '.txt')
    if not path.exists():
        url = meta.get('immutable_blob_url', meta['url'])
        req = urllib.request.Request(url, headers={'User-Agent': 'Shadowrocket-static-audit'})
        with urllib.request.urlopen(req, timeout=120) as response:
            data = response.read()
        if 'immutable_blob_url' in meta:
            data = base64.b64decode(json.loads(data)['content'])
        assert hashlib.sha256(data).hexdigest() == meta['sha256'], url
        path.write_bytes(data)
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == meta['sha256'], str(path)
    return data.decode('utf-8-sig')


def active(text):
    return [(i, s.strip()) for i, s in enumerate(text.splitlines(), 1)
            if s.strip() and not s.lstrip().startswith('#')]


def parse_config(text):
    section = None
    result = []
    sections = []
    for line, s in active(text):
        if s.startswith('['):
            section = s
            sections.append(s)
        elif section == '[Rule]':
            p = s.split(',')
            assert all(v and v == v.strip() for v in p), (line, s)
            assert p[0] in {'DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD',
                            'DOMAIN-SET', 'RULE-SET', 'IP-CIDR', 'GEOIP', 'FINAL'}, s
            assert len(p) == (2 if p[0] == 'FINAL' else 4 if p[-1] == 'no-resolve' else 3), s
            assert p[1 if p[0] == 'FINAL' else 2] in {'DIRECT', 'PROXY', 'REJECT'}, s
            if p[0] == 'IP-CIDR':
                ipaddress.ip_network(p[1], strict=True)
            if p[0] in {'DOMAIN-SET', 'RULE-SET'}:
                assert p[1].startswith('https://') and '?' not in p[1], s
            result.append((line, s, p))
    assert sections == ['[General]', '[Rule]', '[Host]'], sections
    assert result[-1][1] == 'FINAL,PROXY'
    assert sum(p[0] == 'FINAL' for _, _, p in result) == 1
    assert len({s for _, s, _ in result}) == len(result), 'Exact duplicate rule'
    return result


current = (ROOT / E['config']).read_text()
base = subprocess.check_output(['git', 'show', E['base'] + ':' + E['config']], cwd=ROOT).decode()
rules, old = parse_config(current), parse_config(base)
assert '\r' not in current and current.endswith('\n')
assert current.split('[Rule]')[0] == base.split('[Rule]')[0], 'General/update-url changed'
assert current.split('[Host]')[1] == base.split('[Host]')[1], 'Host changed'
old_text = [s for _, s, _ in old]
assert [s for _, s, _ in rules if s in old_text] == old_text, 'Existing rules changed/reordered'
added = [s for _, s, _ in rules if s not in old_text]
assert len(added) == 16, added
first_external = next(n for n, _, p in rules if p[0] == 'RULE-SET')
apple_start = current.splitlines().index('# Apple ecosystem — ALWAYS DIRECT') + 1
apple = [(n, s, p) for n, s, p in rules if apple_start < n < first_external]
assert len(apple) == 75 and all(p[2] == 'DIRECT' for _, _, p in apple)
apple_nets = [ipaddress.ip_network(p[1]) for _, _, p in apple if p[0] == 'IP-CIDR']


def domain_matches(host, kind, value):
    return (host == value if kind == 'DOMAIN' else
            host == value or host.endswith('.' + value) if kind == 'DOMAIN-SUFFIX' else
            value in host if kind == 'DOMAIN-KEYWORD' else False)


def apple_match(host):
    return next((s for _, s, p in apple if domain_matches(host, p[0], p[1])), None)


official = []
for row in E['apple_document']['rows']:
    host = row['host'].replace('*.', 'audit-probe.')
    match = apple_match(host)
    assert match, row
    official.append(dict(row, first_rule=match))

external = {}
warnings = []
for meta in E['external_lists']:
    contents = active(source(meta))
    if meta['key'] == 'external-198':
        exact, suffix = {}, {}
        for n, s in contents:
            if ',' in s:
                warnings.append(f"Runet DOMAIN-SET line {n}: malformed {s!r}; native handling unknown")
                continue
            (suffix if s.startswith('.') else exact)[s.lstrip('.')] = n
        external[meta['url']] = (exact, suffix)
    else:
        external[meta['url']] = [(n, s, s.split(',')) for n, s in contents]


def trace(host, geo_ru=None):
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    def matches(p):
        if address is not None and p[0] == 'IP-CIDR':
            return address in ipaddress.ip_network(p[1])
        # no-resolve rules do not force a lookup; no cached mapping is fabricated.
        return address is None and domain_matches(host, p[0], p[1])
    for n, s, p in rules:
        reason = None
        if p[0] == 'DOMAIN-SET' and address is None:
            exact, suffix = external[p[1]]
            if host in exact:
                reason = f"entry {exact[host]}: {host}"
            else:
                for i in range(len(host.split('.'))):
                    h = '.'.join(host.split('.')[i:])
                    if h in suffix:
                        reason = f"entry {suffix[h]}: .{h}"
                        break
        elif p[0] == 'RULE-SET':
            reason = next((f'entry {k}: {v}' for k, v, sub in external[p[1]] if matches(sub)), None)
        elif p[0] == 'GEOIP':
            if geo_ru is None:
                return {'host': host, 'line': n, 'first_rule': s + ' if RU; otherwise continue',
                        'policy': 'DIRECT if RU; otherwise FINAL,PROXY',
                        'basis': 'No matching visible domain/literal-IP rule; device GeoIP required'}
            reason = 'Explicit test assumption: GeoIP RU' if geo_ru else None
        elif p[0] == 'FINAL':
            return {'host': host, 'line': n, 'first_rule': s, 'policy': p[1],
                    'basis': 'All previous modeled rules missed; GeoIP non-RU assumed'}
        elif matches(p):
            reason = 'Literal IP match' if address is not None else 'Domain match'
        if reason:
            return {'host': host, 'line': n, 'first_rule': s, 'policy': p[2], 'basis': reason}


mandatory = '''apple.com www.apple.com icloud.com setup.icloud.com guzzoni.apple.com
gateway.push.apple.com api.push.apple.com appleid.apple.com music.apple.com apps.apple.com
mzstatic.com cdn-apple.com apple-cloudkit.com apple-mapkit.com apple-relay.cloudflare.com
apple-relay.fastly-edge.com cp4.cloudflare.com appldnld.apple.com.edgesuite.net
ocsp.digicert.com 17.57.146.140 17.57.146.141 17.57.146.135'''.split()
cases = mandatory + '''shazam.com beatsbydre.com kino.pub dark.kino.pub o.kino.pub www.kino.pub
api.service-kp.com kinopub.fastcdn.pics cdn2cdn.com cdn2site.com digital-cdn.net cdntogo.net
microiptv.org microiptv.com api.alador.space m.alador.space yandex.ru api.market.yandex.ru mail.ru vk.com
2gis.ru aviasales.ru t.me whatsapp.com chatgpt.com youtube.com discord.com redotpay.com
cloudflare.com example.akamaized.net example.fastly.net ocsp5.digicert.com cdn20.com
apple.com.example.net notapple.com 205.180.175.1 57.102.0.1 198.183.31.1
2001:2030:9::1 2a01:b747::1 192.168.1.20 printer.local
crl3.digicert.com crl4.digicert.com ocsp.digicert.cn vertexsmb.com
ocsp.apple.com.cdn20.com 51.15.20.62 46.17.96.110 163.172.72.58
104.21.57.60 172.67.159.228 146.59.16.58 213.183.48.21'''.split()
traces = [trace(h) for h in cases]
traces.append(trace('unknown-audit.example', geo_ru=False))
assert all(t['policy'] == 'DIRECT' for t in traces[:len(mandatory)])
assert trace('api.service-kp.com')['policy'] == 'PROXY'
assert all(trace(h)['policy'] == 'DIRECT' for h in ['yandex.ru', 'mail.ru', 'vk.com', '2gis.ru'])
assert all(trace(h)['policy'] == 'PROXY' for h in ['t.me', 'chatgpt.com', 'whatsapp.com'])
assert traces[-1]['first_rule'] == 'FINAL,PROXY'
for h in ['cloudflare.com', 'example.akamaized.net', 'example.fastly.net', 'ocsp5.digicert.com',
          'cdn20.com', 'apple.com.example.net', 'notapple.com']:
    assert apple_match(h) is None, h

boundaries = 0
for net in apple_nets:
    for address in [net.network_address, net.broadcast_address]:
        assert trace(str(address))['policy'] == 'DIRECT'
        boundaries += 1
    # A neighbor may belong to another Apple allocation; never infer otherwise.
    for i in [int(net.network_address) - 1, int(net.broadcast_address) + 1]:
        if 0 <= i < 2 ** net.max_prefixlen:
            address = type(net.network_address)(i)
            assert (address in net) is False
            boundaries += 1
bgp_counts = {}
for key in ['bgp714.txt', 'bgp6185.txt']:
    nets = [ipaddress.ip_network(x) for x in E['bgp'][key]['prefixes']]
    missing = [str(x) for x in nets if not any(x.version == y.version and x.subnet_of(y) for y in apple_nets)]
    assert not missing, missing
    bgp_counts[key] = len(nets)

bm = []
for meta in E['blackmatrix_sources']:
    for n, s in active(source(meta)):
        if meta['key'] == 'apple-domains':
            h = s.lstrip('.')
            match = apple_match(h)
            # A suffix candidate is covered only if a suffix rule covers it.
            if s.startswith('.') and match and not match.startswith('DOMAIN-SUFFIX,'):
                match = None
            status = 'A: covered' if match else 'D: shared provider; no broad exception' if h in {
                'akadns.net', 'digicert.com', 'crashlytics.com'} else 'E: current ownership/use unverified; not added'
            if h in {'shazam.com', 'beatsbydre.com'}:
                status = 'B: official current service; added'
            if h in {'apple-events.akamaized.net', 'p-events-delivery.akamaized.net', 'e16991.b.akamaiedge.net'}:
                status = 'C: possible dedicated CDN; current necessity unverified; not added'
            if h.endswith('.omtrdc.net'):
                status = 'D: exact shared-provider tenant; current necessity unverified; not added'
        else:
            p = s.split(',');match = None
            if p[0] == 'IP-CIDR':
                net = ipaddress.ip_network(p[1])
                match = next((str(x) for x in apple_nets if x.version == net.version and net.subnet_of(x)), None)
                status = 'F: registered space covered' if match else 'F: 205.180.175.0/24 not Apple-confirmed; not added'
            else:
                status = 'E: broad keyword/user-agent not identity evidence; not copied'
        bm.append({'file':meta['key'],'line':n,'candidate':s,'status':status,'cover':match})

results = {'config_sha256':hashlib.sha256(current.encode()).hexdigest(), 'base':E['base'],
           'rules':len(rules), 'apple_rules':len(apple), 'added_rules':added,
           'official_rows':len(official), 'boundary_checks':boundaries, 'bgp_prefix_counts':bgp_counts,
           'blackmatrix_counts':dict(collections.Counter(x['status'] for x in bm)),
           'warnings':warnings, 'traces':traces,
           'limits':['Snapshot subset model, not native Shadowrocket',
                     'No URL-REGEX/USER-AGENT matching without URL/headers',
                     'No DNS cache, CNAME, fake-IP, GeoIP database or live tvOS execution',
                     'DOMAIN-SET naked entries modeled exact, leading dot suffix; native import untested',
                     'No guarantee that local/upstream bypass enters the rule engine']}
if args.write_results:
    (ROOT/'audit/static-results-20260924.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    for filename, records in [('official-coverage-20260924.tsv',official),('blackmatrix-review-20260924.tsv',bm)]:
        fields=list(records[0]);text='\t'.join(fields)+'\n'
        text+='\n'.join('\t'.join(str(r.get(k) or '') for k in fields) for r in records)+'\n'
        (ROOT/'audit'/filename).write_text(text)
print(json.dumps({k:v for k,v in results.items() if k not in {'traces','added_rules'}},ensure_ascii=False,indent=2))
