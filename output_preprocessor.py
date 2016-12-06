#!/usr/bin/env python

import argparse
import cgi
import cookielib
import json
import logging
import os
import requests
import subprocess
import sys
import textwrap

import bs4
from six.moves import shlex_quote

import service

LOG = logging.getLogger("output_preprocessor.py")


def get_curl_command(uri, verb="GET", data=None, headers=None, add_code=False,
                     authenticate=False, cookie_file=None):
    retval = ["curl", "-4", "-s"]
    if add_code:
        retval.extend(["-w", "# HTTP code: %{http_code}\\n"])
    if verb.upper() != "GET":
        retval.extend(["-X", verb.upper()])
    if authenticate:
        retval.extend(["-u", "%s:%s" % (service.USERNAME, service.PASSWORD)])
    if data is not None:
        retval.extend(["-d", data])
    if headers is not None:
        for header, value in headers.items():
            retval.extend(["-H", "%s: %s" % (header, value)])
    if cookie_file:
        retval.extend(["-b", cookie_file, "-c", cookie_file])
    retval.append(uri)
    return retval


def get_printable_curl_command(command):
    parts = []
    for i, part in enumerate(command):
        if i > 0 and command[i - 1] in ["-b", "-c"]:
            # rewrite cookie file argument to declutter command line
            parts.append("cookies")
        elif part in ["-4", "-s", "-w"] or part.startswith("# HTTP code:"):
            pass
        else:
            parts.append(shlex_quote(part))
    lines = textwrap.wrap(" ".join(parts), subsequent_indent="    ",
                          break_long_words=False, break_on_hyphens=False)
    return "\n".join(["%s \\" % l for l in lines[0:-1]] + [lines[-1]])


def get_http_command(uri, verb="GET"):
    return "%s %s HTTP/1.0" % (verb.upper(), uri)


def setup_logging():
    LOG.setLevel(logging.DEBUG)
    LOG.addHandler(logging.StreamHandler())


def str2bool(val):
    return val.lower() in ["true", "yes", "on", "1"]


def main():
    setup_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument("html_file")
    parser.add_argument("--output", "-o", default="outputs")
    options = parser.parse_args()

    outdir = os.path.abspath(os.path.expanduser(options.output))
    LOG.info("Writing output to %s" % outdir)

    page_data = bs4.BeautifulSoup(open(options.html_file), "html.parser")
    for tag in page_data.find_all("pre", attrs={"service-uri": True}):
        uri = "http://localhost:5000%s" % tag["service-uri"]
        verb = tag.get("verb", "GET")
        data = tag.get("data")
        style = tag.get("command-style", "curl")
        allow_error = str2bool(tag.get("allow-error", "false"))
        add_code = str2bool(tag.get("add-code",
                                    str(allow_error or verb != "GET")))
        authenticate = str2bool(tag.get("authenticate", "false"))
        headers = json.loads(tag.get("headers", '{}'))
        cookies = tag.get("cookies")
        cookie_file = os.path.join(options.output,
                                   "%s.cookies" % tag.parent["id"])

        LOG.info("Creating output for %s: %s %s" %
                 (tag["id"], verb, tag["service-uri"]))

        outfile = os.path.join(outdir, "%s.txt" % tag["id"])
        if data:
            headers["Content-Type"] = "application/json"

        with open(outfile, "w") as output:
            output_data = None
            if style == "curl":
                cmd = get_curl_command(
                    uri, verb=verb, data=data, headers=headers,
                    authenticate=authenticate, add_code=add_code,
                    cookie_file=cookie_file if cookies else None)
                LOG.info("Running curl command: %s" % cmd)
                output.write("<code class=\"bash\" data-trim>")
                output.write("$ %s\n" %
                             cgi.escape(get_printable_curl_command(cmd)))

                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
                if proc.wait() != 0 and not allow_error:
                    LOG.error("Unexpected error: %s" %
                              "\n".join(proc.stderr.readlines()))
                    return 1

                stderr_data = "".join(proc.stderr.readlines())
                stdout = "\n".join([l.rstrip() for l in proc.stdout.readlines()])
                stdout_data = ""
                if stdout.strip():
                    try:
                        stdout_data = json.dumps(json.loads(stdout), indent=2)
                    except ValueError:
                        stdout_data = stdout
                output_data = stderr_data + stdout_data
            elif style == "http":
                cmd = get_http_command(uri, verb=verb)
                LOG.info("Running HTTP command: %s" % cmd)
                output.write("<code class=\"http\" data-trim>")
                output.write("%s\n" % cgi.escape(cmd))
                output.write("</code><code class=\"nohighlight\" data-trim>")

                response = requests.request(verb.lower(), uri)
                if response.status_code >= 400 and not allow_error:
                    LOG.error("Unexpected error (%s): %s" %
                              (response.status_code, response.text))
                    return 1
                if response.text and response.json():
                    output_data = json.dumps(response.json(), indent=2)
            else:
                raise Exception("Unknown command style %s: %s" % (style, tag))

            if output_data.strip():
                output.write(cgi.escape(output_data))
            else:
                output.write("# no output\n")

            if cookies == "display":
                output.write("\n$ cat cookies\n")
                for line in open(cookie_file).readlines():
                    if line.strip() and not line.startswith("#"):
                        output.write(line)
            output.write("</code>")
        LOG.info("Wrote output to %s" % outfile)

if __name__ == "__main__":
    sys.exit(main())
