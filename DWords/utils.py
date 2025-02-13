import os
import time
import logging
from .db import user_db

logging.basicConfig(format="[%(levelname)s] %(asctime)s | %(message)s",
                    level=logging.INFO)

COLORS = {
    'red': ("231,76,60", "255,255,255"),
    'yellow': ("241,196,15", "255,255,255"),
    'orange': ("243,156,18", "255,255,255"),
    'cyan': ("26,188,156", "255,255,255"),
    'green': ("46,204,113", "255,255,255"),
    'blue': ("52,152,219", "255,255,255"),
    'purple': ("155,89,182", "255,255,255"),
    'dark': ("52,73,94", "255,255,255"),
    'white': ("236,240,241", "0,0,0"),
}

def random_one_word(*exceptions):
    return user_db.getOne("select word, paraphrase, show_paraphrase, color "
        "from words where cleared = 0 and "
        f"word not in ({','.join('?' * len(exceptions))}) "
        "order by random() limit 1", exceptions
    )

def clock():
    return int(time.time() * 1000)

def _on_modify(c, word, op):
    now = clock()
    c.execute("update sync_cache set op = ?, time = ? "
        "where word = ?", (op, now, word))
    c.execute("insert or ignore into sync_cache(word, op, time) "
        "values(?, ?, ?)", (word, op, now))

def add_words(*words):
    now = clock()
    with user_db.cursor() as c:
        for word, paraphrase in words:
            c.execute("update words set paraphrase = ?, modify_time = ? "
                "where word = ?", (paraphrase, now, word))
            c.execute("insert or ignore into words(word, paraphrase) "
                "values(?, ?)", (word, paraphrase))
            _on_modify(c, word, "add")

def delete_words(*words):
    with user_db.cursor() as c:
        c.execute(f"delete from words where word in ({','.join('?' * len(words))})", words)
        for word in words:
            _on_modify(c, word, "del")

def set_word_attribute(word, **kw):
    with user_db.cursor() as c:
        for k, v in kw.items():
            c.execute(f"update words set {k} = ? where word = ?", (v, word))

        now = clock()
        c.execute("update words set modify_time = ? where word = ?", (now, word))
        _on_modify(c, word, "add")

DEFAULT_SETTING = {
    "email": None,
    "password": None,
    "smtp_server": None,
    "pop3_server": None,
    "sync_frequency": 1000 * 60 * 5,

    "danmuku_speed": 1 / 12,
    "danmuku_frequency": 6000,
    "danmuku_default_show_paraphrase": False,
    "danmuku_default_color": "white",
    "danmuku_transparency": 0.5,
}

def get_setting(key):
    value = user_db.getOne("select value from setting where key = ?", (key,))
    if value is None: return DEFAULT_SETTING[key]
    return eval(value[0])

def set_setting(key, value):
    value = repr(value)
    with user_db.cursor() as c:
        c.execute("update setting set value = ? where key = ?", (value, key))
        c.execute("insert or ignore into setting(key, value) values(?, ?)", (key, value))

def is_sync():
    count, = user_db.getOne("select count(key) from setting "
        "where key in ('email', 'password', 'smtp_server', 'pop3_server') "
        "and value != 'None'")

    return count == 4

VALUE_RANGE = {
    "danmuku_speed": (1 / 9, 1 / 18),
    "danmuku_frequency": (3000, 20000),
    "danmuku_transparency": (0.3, 1.0),
}

def progress2value(key, progress):
    MIN, MAX = VALUE_RANGE[key]
    return MIN + (MAX - MIN) * (progress / 99)

def value2progress(key, value):
    MIN, MAX = VALUE_RANGE[key]
    return int((value - MIN) / (MAX - MIN) * 99)

