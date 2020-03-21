#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from pathlib import Path
import re
import uuid

from bs4 import BeautifulSoup

FILE_NAME_ACL = Path(r'C:\<...>\ads\<...>\src\<...>.xml')
FILE_NAME_ACL_LOCALE = FILE_NAME_ACL.parent.parent / 'locale' / 'en' / ('mlb' + FILE_NAME_ACL.name)

root_acl = BeautifulSoup(open(FILE_NAME_ACL, 'rb'), 'xml')
root_acl_locale = BeautifulSoup(open(FILE_NAME_ACL_LOCALE, 'rb'), 'xml')

# NOTE: <Group Id="cpg<...>" Name="<...>" Members="<PROP_IDS">
PROP_IDS = "prd<...> prd<...>".split()
items = []

new_prop_ids = []

with open('new_props.txt', 'w', encoding='utf-8') as f:
    for prop_id in PROP_IDS:
        prop_el = root_acl.select_one(f'[Id="{prop_id}"]')
        prop_name = prop_el['Name']

        title_id = prop_el.Presentation['TitleId']
        title = root_acl_locale.select_one(f'[Id="{title_id}"]').Value.text

        # print(name, title)
        prop_el['Id'] = f'prd{uuid.uuid4().hex.upper()[:26]}'
        prop_el['Name'] = f'{prop_name}_Title_{title}'

        new_prop_ids.append(prop_el['Id'])

        new_src = f"""\
            <Src>
                <xsc:Item>
                    <xsc:Java>return </xsc:Java>
                </xsc:Item>
                <xsc:Item>
                    <xsc:IdReference Path="{FILE_NAME_ACL.stem} {prop_id}" Invoke="true">
                        <xsc:Presentation>{prop_name}</xsc:Presentation>
                    </xsc:IdReference>
                </xsc:Item>
                <xsc:Item>
                    <xsc:Java>;</xsc:Java>
                </xsc:Item>
            </Src>\
        """

        new_prop_el_str = re.sub('<Src>.+?</Src>', new_src, str(prop_el), flags=re.DOTALL)
        print(new_prop_el_str, file=f)

    f.write('\n\n')
    f.write('new_prop_ids: "' + ' '.join(new_prop_ids) + '"')
