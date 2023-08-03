#!/usr/bin/env python3
""" The Filtered Logger Module. """

import re
import logging
from typing import List
import mysql.connector
import os


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
        """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        log_message = super().format(record)
        for field in self.fields:
            log_message = re.sub(
                r'(?<={}=).*?(?={})'.format(field, self.SEPARATOR),
                self.REDACTION, log_message)
        return log_message


PII_FIELDS = ["name", "email", "phone", "ssn", "password"]


def get_logger() -> logging.Logger:
    """Returns a logging.Logger object named "user_data" with a StreamHandler and RedactingFormatter."""
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = RedactingFormatter(fields=PII_FIELDS)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    return logger


def get_db():
    """
    Returns a connector to the database (mysql.connector.connection.MySQLConnection object).

    Uses environment variables to obtain database credentials.
    """
    username = os.environ.get("PERSONAL_DATA_DB_USERNAME", "root")
    password = os.environ.get("PERSONAL_DATA_DB_PASSWORD", "")
    host = os.environ.get("PERSONAL_DATA_DB_HOST", "localhost")
    database = os.environ.get("PERSONAL_DATA_DB_NAME")

    # Connect to the database
    db = mysql.connector.connect(host=host,
                                 user=username,
                                 password=password,
                                 database=database)

    return db


def filter_datum(fields: List[str], redaction: str, message: str,
                 separator: str) -> str:
    """
    Obfuscates specified fields in the log message.

    Args:
        fields (list): A list of strings representing fields to obfuscate.
        redaction (str): A string representing the obfuscated value to replace the fields.
        message (str): The log line containing the fields to be obfuscated.
        separator (str): The character separating all fields in the log line.

    Returns:
        str: The obfuscated log message.
    """
    return re.sub(r'({})=([^{}]+)'.format('|'.join(fields), separator),
                  r'\1={}'.format(redaction), message)


def main():
    """Obtain a database connection and display filtered user data."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users;")

    formatter = RedactingFormatter(
        fields=["name", "email", "phone", "ssn", "password"])

    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    for row in cursor:
        formatted_row = [
            f"{col_name}={RedactingFormatter.REDACTION}"
            if col_name in formatter.fields else f"{col_name}={col_value}"
            for col_name, col_value in zip(cursor.column_names, row)
        ]
        log_message = "; ".join(formatted_row)
        logger.info(log_message)

    cursor.close()
    db.close()

