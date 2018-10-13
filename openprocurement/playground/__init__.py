# -*- coding: utf-8 -*-
import os
import re
from glob import glob
from uuid import uuid4
from pytz import timezone
from hashlib import md5
from mimetypes import guess_type
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
from requests import Session
from requests.auth import HTTPBasicAuth as BasicAuth
try:
    import simplejson as json
except ImportError:
    import json

TZ = timezone('Europe/Kiev')


app = Flask(__name__)
app.config.update(
    JSON_AS_ASCII=False,
    JSON_SORT_KEYS=True,
    SNIPPETS_DIR='snippets')
if 'FLASK_SETTINGS' in os.environ:
    app.config.from_envvar('FLASK_SETTINGS')


def prepare_date(root, key):
    delta = root[key].strip()
    oper = delta[0]
    if oper in ('+', '-'):
        delta = delta[1:]
    unit = delta[-1].lower()
    if unit in ('d', 'h', 'm'):
        delta = delta[:-1]
    delta = float(delta)
    if unit == 'd':
        delta *= 24 * 3600
    elif unit == 'h':
        delta *= 3600
    elif unit == 'm':
        delta *= 60
    dt = datetime.now(TZ)
    dl = timedelta(seconds=delta)
    if oper == '-':
        dt = dt - dl
    else:
        dt = dt + dl
    root[key] = dt.isoformat()


def prepare_tender(root):
    for key, val in root.items():
        if key in ('startDate', 'endDate'):
            if val and val[0] in ('+', '-'):
                prepare_date(root, key)
        if key == 'id' and not val:
            root[key] = uuid4().hex
        if key in ('title', 'description') and val.find('{now}') > 0:
            now = datetime.now().isoformat().replace('T', ' ')[:16]
            root[key] = val.replace('{now}', now)
        if isinstance(val, list):
            for item in val:
                prepare_tender(item)
        elif isinstance(val, dict):
            prepare_tender(val)


@app.route("/")
def index(template_name="index.html"):
    return render_template(template_name)


@app.route("/api", methods=["POST"])
def post_api():
    try:
        req = "\r\n".join(["{}={}".format(k, v) for k, v in request.form.items()])
        app.logger.info("FORM\r\n%s", req)
    except:
        app.logger.info("FORM %s", str(request.form))

    method = request.form['method']
    api_key = request.form['api_key']
    api_url = request.form['api_url']
    path_url = request.form['path_url']
    acc_token = request.form['acc_token']
    json_text = request.form['editor']

    url = api_url + path_url

    match_version = re.match(r'/api/(\d[\d\.]*)/', path_url)
    api_version = match_version.group(1) if match_version else '2.3'

    try:
        session = Session()
        login_pass = (api_key, '')
        session.auth = BasicAuth(*login_pass)
        response = session.request(
            'HEAD', '{}/api/{}/spore'.format(api_url, api_version)
        )
        response.raise_for_status()

        headers = {}
        if acc_token:
            headers['X-Access-Token'] = acc_token

        kw = {'headers': headers}

        if method != 'GET':
            tender = json.loads(json_text)
            prepare_tender(tender)
            kw['json'] = tender

        app.logger.info("{} {} {}".format(method, url, kw))

        resp = session.request(
            method,
            url, **kw)
    except Exception as e:
        app.logger.exception(e)
        return jsonify(exception=str(e))

    try:
        hdrs = "\r\n".join(["{}: {}".format(k, v) for k, v in resp.headers.items()])
        hdrs = "{} {}\r\n\r\n{}\r\n\r\n".format(resp.status_code, resp.reason, hdrs)
        response = hdrs + resp.text
        data = json.loads(resp.text)
        text = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
        response = hdrs + text
    except Exception as e:
        app.logger.exception("Exception due response processing {}".format(e))

    app.logger.info("RESP %s", response)

    return response


@app.route("/doc", methods=["POST"])
def post_doc():
    try:
        req = "\r\n".join(["{}={}".format(k, v) for k, v in request.form.items()])
        app.logger.info("DOC_FORM\r\n%s", req)
    except:
        app.logger.info("DOC_FORM %s", str(request.form))

    doc_api_key = request.form['doc_api_key']
    doc_api_url = request.form['doc_api_url']
    doc_api_path = request.form['doc_api_path']
    document_id = request.form['document_id']
    doc_filename = request.form['doc_filename']
    document_body = request.form['document_body']

    method = "POST"
    url = doc_api_url + doc_api_path

    if document_id:
        url += '/' + document_id

    try:
        session = Session()
        login_pass = tuple(doc_api_key.split(':', 1))
        session.auth = BasicAuth(*login_pass)
        kw = {}

        if 'upload' in doc_api_path:
            doc_mimetype, _ = guess_type(doc_filename)
            kw['files'] = {'file': (doc_filename, document_body, doc_mimetype)}
        else:
            kw['data'] = {'hash': "md5:{}".format(md5(document_body).hexdigest())}

        app.logger.info("{} {} {}".format(method, url, kw))

        resp = session.request(
            method,
            url, **kw)
    except Exception as e:
        app.logger.exception(e)
        return jsonify(exception=str(e))

    try:
        hdrs = "\r\n".join(["{}: {}".format(k, v) for k, v in resp.headers.items()])
        hdrs = "{} {}\r\n\r\n{}\r\n\r\n".format(resp.status_code, resp.reason, hdrs)
        response = hdrs + resp.text
        data = json.loads(resp.text)
        text = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
        response = hdrs + text
    except Exception as e:
        app.logger.exception("Exception due response processing {}".format(e))

    app.logger.info("RESP %s", response)

    return response
