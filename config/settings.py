# 生产环境需要重新配置

settings = {
    # B2B_WEB 数据库信息
    'DB_HOST': 'localhost',
    'DB_NAME': 'postgres',
    'DB_USER': 'postgres',
    'DB_PASS': '123456',
    'DB_PORT': 5432,

    # REDIS服务器信息
    'REDIS_HOST': '127.0.0.1',
    'REDIS_PORT': 6379,
    'REDIS_DB': 9,
    # 'REDIS_PASS': '1qaz2wsx',

    # MQ服务器信息
    'MQ_BROKER': 'amqp://admin:1qaz2wsx@localhost//',
    'MQ_PORT': 5672,

    # SANIC_JWT_SECRET
    'SANIC_JWT_SECRET': '$$$asjfhldsjfhlskjgVVVdfsdfaff134141!#@#$$$$$rtbbbbg$$$',

    # BASE_URL
    'BASE_URL': 'https://api.b2b.91t.com',

    # WX WORK
    'WX_WORK_API_BASE_URL': 'https://qyapi.weixin.qq.com/cgi-bin',

    # ELASTIC
    'ELASTIC_SEARCH_URL': 'https://index.data.91t.com',
    'ELASTIC_SEARCH_USER': 'xibao',
    'ELASTIC_SEARCH_PASS': '5DDp9r13165nmmBH5N7k'
}
