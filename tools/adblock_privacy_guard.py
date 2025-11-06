#!/usr/bin/env python3
"""Command-line tool for building consolidated ad/tracker blocklists for Ubuntu.

This module downloads well-known ad blocking and privacy lists and emits a
unified list that can be imported into hosts files, dnsmasq configurations, or
other domain-based blockers. The tool is intentionally dependency free so that
it can be shipped easily with Ubuntu installations without extra packaging.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import gzip
import zlib
import sys
import textwrap
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Set
from urllib.error import URLError
from urllib.request import Request, urlopen


DEFAULT_TIMEOUT = 45  # seconds
USER_AGENT = "adblock-privacy-guard/1.0 (+https://github.com/abp-filters/abp-filters-anti-cv)"


@dataclass(frozen=True)
class BlockList:
    """Definition of a downloadable block list."""

    name: str
    url: str
    category: str


BUILTIN_LISTS: Dict[str, BlockList] = {
    "easylist": BlockList(
        name="EasyList",
        url="https://easylist.to/easylist/easylist.txt",
        category="ads",
    ),
    "easyprivacy": BlockList(
        name="EasyPrivacy",
        url="https://easylist.to/easylist/easyprivacy.txt",
        category="tracking",
    ),
    "stevenblack": BlockList(
        name="StevenBlack Unified hosts",
        url="https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",
        category="hosts",
    ),
}


def _build_request(url: str) -> Request:
    request = Request(url)
    request.add_header("User-Agent", USER_AGENT)
    request.add_header("Accept-Encoding", "gzip,deflate")
    return request


def download(url: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """Fetch *url* and return the decoded text content."""

    try:
        with urlopen(_build_request(url), timeout=timeout) as response:
            data = response.read()
            encoding = response.headers.get("Content-Encoding", "").lower()
    except URLError as exc:  # pragma: no cover - exercised via network failures
        raise RuntimeError(f"Failed to download {url}: {exc}") from exc

    if encoding == "gzip":
        data = gzip.decompress(data)
    elif encoding == "deflate":
        data = zlib.decompress(data, -zlib.MAX_WBITS)

    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


def parse_domains_from_filters(text: str) -> Set[str]:
    """Extract domain names from standard filter list syntax."""

    domains: Set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("!"):
            continue
        if line.startswith("@@"):
            continue  # allow rules
        if line.startswith("/") and line.endswith("/"):
            continue  # regex filters
        if line.startswith("||"):
            domain = line[2:]
            for terminal in ("^", "/"):
                if terminal in domain:
                    domain = domain.split(terminal, 1)[0]
            domain = domain.lstrip("*.")
            if domain:
                domains.add(domain)
            continue
        if line.startswith("0.0.0.0 ") or line.startswith("127.0.0.1 "):
            parts = line.split()
            if len(parts) >= 2:
                domains.add(parts[1].strip())
    return domains


def parse_hosts_file(text: str) -> Set[str]:
    """Parse host file style entries."""

    domains: Set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[0] in {"0.0.0.0", "127.0.0.1"}:
            domains.add(parts[1])
    return domains


def collect_domains(
    list_keys: Sequence[str], extra_urls: Sequence[str], timeout: int
) -> Set[str]:
    """Download and parse blocklists into a set of domains."""

    domains: Set[str] = set()
    for key in list_keys:
        block_list = BUILTIN_LISTS[key]
        content = download(block_list.url, timeout=timeout)
        if block_list.category == "hosts":
            domains.update(parse_hosts_file(content))
        else:
            domains.update(parse_domains_from_filters(content))
    for url in extra_urls:
        content = download(url, timeout=timeout)
        domains.update(parse_domains_from_filters(content) | parse_hosts_file(content))
    return domains


def _format_comment(text: str, width: int = 78) -> str:
    wrapper = textwrap.TextWrapper(width=width)
    return "\n".join(f"# {line}" if line else "#" for line in wrapper.wrap(text))


def render_output(domains: Iterable[str], fmt: str) -> str:
    formatter = {
        "hosts": lambda domain: f"0.0.0.0 {domain}",
        "dnsmasq": lambda domain: f"address=/{domain}/0.0.0.0",
        "domains": lambda domain: domain,
    }[fmt]
    sorted_domains = sorted(set(domains))
    return "\n".join(formatter(domain) for domain in sorted_domains)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate consolidated advertisement and tracker block lists."
    )
    parser.add_argument(
        "--lists",
        nargs="+",
        choices=sorted(BUILTIN_LISTS.keys()),
        default=sorted(BUILTIN_LISTS.keys()),
        help="Built-in lists to include (default: all).",
    )
    parser.add_argument(
        "--format",
        choices=("hosts", "dnsmasq", "domains"),
        default="hosts",
        help="Output formatting (default: hosts).",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Optional output file. If omitted, prints to stdout.",
    )
    parser.add_argument(
        "--extra-url",
        dest="extra_urls",
        action="append",
        default=[],
        help="Additional remote filter list URL to merge.",
    )
    parser.add_argument(
        "--extra-domain",
        dest="extra_domains",
        action="append",
        default=[],
        help="Domain to add manually (can be supplied multiple times).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Download timeout in seconds (default: {DEFAULT_TIMEOUT}).",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)

    try:
        domains = collect_domains(args.lists, args.extra_urls, args.timeout)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    domains.update(args.extra_domains)

    header_lines: List[str] = [
        _format_comment(
            f"Generated on {_dt.datetime.utcnow():%Y-%m-%d %H:%M:%S} UTC using adblock_privacy_guard"
        ),
        _format_comment(
            "Included lists: "
            + ", ".join(BUILTIN_LISTS[key].name for key in args.lists)
        ),
    ]
    if args.extra_urls:
        header_lines.append(
            _format_comment("Additional URLs: " + ", ".join(args.extra_urls))
        )
    if args.extra_domains:
        header_lines.append(
            _format_comment("Extra manual domains: " + ", ".join(sorted(args.extra_domains)))
        )

    body = render_output(domains, args.format)
    content = "\n".join(header_lines + ["", body, ""]) if body else "\n".join(header_lines + [""])

    if args.output:
        path = args.output
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"Wrote {len(domains)} domains to {path}")
    else:
        print(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
