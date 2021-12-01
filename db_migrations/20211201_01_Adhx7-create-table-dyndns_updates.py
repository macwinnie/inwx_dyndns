"""
CREATE TABLE dyndns_updates
"""

from yoyo import step

__depends__ = {}

steps = [
    step("CREATE TABLE dyndns_updates (id INT, type VARCHAR(4), value VARCHAR(128), date VARCHAR(128), PRIMARY KEY (id))")
]
