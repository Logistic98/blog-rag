# -*- coding: utf-8 -*-

from pymilvus import connections, utility

connections.connect(
    alias='default',
    host='localhost',
    port='19530',
    user='root',
    password='Milvus'
)

utility.reset_password(
    old_password='Milvus',
    new_password='cG72vdgVWX5ypaWV',
    user='root',
    using='default'
)
