import re

from lxml import etree


def extract_img_url(string):
    try:
        if string is None:
            return None
        html = etree.HTML(string)
        for ii in html:
            images = ii.xpath('p/img/@src')
            return images[0]
    except Exception as e:
        print(e, string)


def extract_text(raw_data):
    if raw_data is not None:
        raw_data = re.sub(r"<script>[\s\S]*</script>", "", raw_data)
        html = etree.HTML(raw_data)

        content = []
        if html is not None:
            html_data = html.xpath('/html/body/*//text()')
            for data in html_data:
                tmp = data.strip(' \n\r').replace('\n', '').replace('\t', '').replace(u'\u3000', u'') \
                    .replace(u'\xa0', u'').replace('\r', '').replace(u'\u2028', u'').replace(u'\u2029', u'')
                if tmp:
                    content.append(tmp)

        item_article = ''.join(content)
        return item_article
    else:
        return None
