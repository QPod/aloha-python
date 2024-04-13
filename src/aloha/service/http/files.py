import time

import requests

from ...logger import LOG


def iter_over_request_files(request, url_files):
    for file_key, files in request.files.items():  # iter over files uploaded by multipart
        for f in files:
            file_name, content_type = f["filename"], f["content_type"]
            body = f.get('body', b"")
            LOG.info(f"File {file_name} from multipart has content type {content_type} and length bytes={len(body)}")
            yield file_key, file_name, content_type, body

    for file_key, list_url in {'url_files': url_files or []}.items():  # iter over files specified by `url_files`
        for url in sorted(set(list_url)):
            try:
                t_start = time.time()
                resp = requests.get(url, stream=True)  # download the file from given url
                if resp.status_code == 200:
                    body = resp.content
                    content_type = resp.headers.get("Content-Type", "UNKNOWN")
                else:
                    raise RuntimeError("Failed to download file after %s seconds with code=%s from URL %s" % (
                        time.time() - t_start, resp.status_code, url
                    ))
                del resp
            except Exception as e:
                raise e
            t_cost = time.time() - t_start
            LOG.info(f"File {url} has content type {content_type} and length bytes={len(body)}, downloaded in {t_cost} seconds")
            yield 'url_files', url, content_type, body
