import plistlib
import unicodedata
import base64
import os
import contextlib
import re
import mimetypes

from loguru import logger


def parse_bdsk_file_to_path(basedir: str, bdsk_str: str) -> str:
    assert os.path.isabs(basedir)
    rp = plistlib.loads(base64.b64decode(bdsk_str))['relativePath']
    rp = unicodedata.normalize('NFC', rp)
    return os.path.normpath(os.path.join(basedir, rp))


def is_text_field(field_name: str) -> bool:
    field_name = field_name.lower()
    if field_name in ('id', 'entrytype', 'url', 'link', 'file'):
        return False
    if re.fullmatch(r'bdsk-(file|url)-(\d+)', field_name):
        return False
    return True


def form_zotero_file_field(file_paths: list[str]) -> str:
    buf = []
    for path in file_paths:
        title = os.path.splitext(os.path.basename(path))[0]
        mt = mimetypes.guess_type(path)[0] or ''
        if not mt:
            logger.error('Failed to guess MIME type for path: {}', path)
        buf.append(f'{title}:{path}:{mt}')
    return ';'.join(buf)


class Processor:
    """Parsing processor."""
    def __init__(self, basedir: str, strip_existing_file: bool):
        """
        Parameters
        ----------
        basedir : str
            The base directory of the BibDesk attachments.
        strip_existing_file : bool
            True to strip existing `file` field.
        """
        self.basedir = basedir
        self.strip_existing_file = strip_existing_file
        self.modified = False

    def do_strip_existing_file(self, record):
        with contextlib.suppress(KeyError):
            del record['file']
            self.modified = True
            logger.debug('Stripped field `file` for record ID={}',
                         record['ID'])
        with contextlib.suppress(KeyError):
            del record['File']
            self.modified = True
            logger.debug('Stripped field `File` for record ID={}',
                         record['ID'])
        return record

    def do_cleanup_messy_brackets(self, record):
        for key in record:
            if is_text_field(key):
                s = record[key]
                s = s.replace(r'{\{}', '').replace(r'{\}}', '')
                if record[key] != s:
                    record[key] = s
                    self.modified = True
                    logger.debug(
                        'Stripped messy bracket escapes for record ID={}',
                        record['ID'])
        return record

    def do_convert_bdsk_file(self, record):
        relevant_keys = (
            re.fullmatch(r'bdsk-file-(\d+)', key, flags=re.IGNORECASE)
            for key in record)
        relevant_keys = [m for m in relevant_keys if m]
        relevant_keys.sort(key=lambda m: int(m.group(1)))
        relevant_keys = [m.group(0) for m in relevant_keys]
        bdsk_file_paths = [
            parse_bdsk_file_to_path(self.basedir, record[k])
            for k in relevant_keys
        ]
        if bdsk_file_paths:
            # Warn if the paths are not files.
            for path in bdsk_file_paths:
                if not os.path.isfile(path):
                    logger.warning(
                        'bdsk_file in record ID={} is not a file: {}',
                        record['ID'], path)
            record['file'] = form_zotero_file_field(bdsk_file_paths)
            for k in relevant_keys:
                del record[k]
            self.modified = True
            logger.debug('Converted bdsk-file(s) for record ID={}',
                         record['ID'])
        return record

    def do_warn_bdsk_url(self, record):
        relevant_keys = (
            re.fullmatch(r'bdsk-url-(\d+)', key, flags=re.IGNORECASE)
            for key in record)
        relevant_keys = [m.group(0) for m in relevant_keys if m]
        for k in relevant_keys:
            logger.warning('bdsk_url in record ID={} will not be migrated: {}',
                           record['ID'], record[k])
        return record

    def __call__(self, record):
        if self.strip_existing_file:
            record = self.do_strip_existing_file(record)
        record = self.do_cleanup_messy_brackets(record)
        record = self.do_convert_bdsk_file(record)
        record = self.do_warn_bdsk_url(record)
        return record
