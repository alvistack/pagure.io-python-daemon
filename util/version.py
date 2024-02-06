# util/version.py
# Part of ‘python-daemon’, an implementation of PEP 3143.
#
# This is free software, and you are welcome to redistribute it under
# certain conditions; see the end of this file for copyright
# information, grant of license, and disclaimer of warranty.

""" Version information unified for human- and machine-readable formats.

    The project ‘ChangeLog’ file is a reStructuredText document, with
    each section describing a version of the project. The document is
    intended to be readable as-is by end users.

    This module handles transformation from the ‘ChangeLog’ to a
    mapping of version information, serialised as JSON. It also
    provides functionality for Setuptools to use this information.

    Requires:

    * Docutils <https://docutils.sourceforge.io/>
    * JSON <https://docs.python.org/3/reference/json.html>
    """

import collections
import datetime
import functools
import io
import json
import sys
import textwrap

import packaging.version

from .metadata import rfc822_person_regex


def ensure_class_bases_begin_with(namespace, class_name, base_class):
    """ Ensure the named class's bases start with the base class.

        :param namespace: The namespace containing the class name.
        :param class_name: The name of the class to alter.
        :param base_class: The type to be the first base class for the
            newly created type.
        :return: ``None``.

        This function is a hack to circumvent a circular dependency:
        using classes from a module which is not installed at the time
        this module is imported.

        Call this function after ensuring `base_class` is available,
        before using the class named by `class_name`.
        """
    existing_class = namespace[class_name]
    assert isinstance(existing_class, type)

    bases = list(existing_class.__bases__)
    if base_class is bases[0]:
        # Already bound to a type with the right bases.
        return
    bases.insert(0, base_class)

    new_class_namespace = existing_class.__dict__.copy()
    # Type creation will assign the correct ‘__dict__’ attribute.
    del new_class_namespace['__dict__']

    metaclass = existing_class.__metaclass__
    new_class = metaclass(class_name, tuple(bases), new_class_namespace)

    namespace[class_name] = new_class


class VersionInfoWriter(object):
    """ Docutils writer to produce a version info JSON data stream. """

    # This class needs its base class to be a class from `docutils`.
    # But that would create a circular dependency: Setuptools cannot
    # ensure `docutils` is available before importing this module.
    #
    # Use `ensure_class_bases_begin_with` after importing `docutils`, to
    # re-bind the `VersionInfoWriter` name to a new type that inherits
    # from `docutils.writers.Writer`.

    __metaclass__ = type

    supported = ['version_info']
    """ Formats this writer supports. """

    def __init__(self):
        super(VersionInfoWriter, self).__init__()
        self.translator_class = VersionInfoTranslator

    def translate(self):
        visitor = self.translator_class(self.document)
        self.document.walkabout(visitor)
        self.output = visitor.astext()


class ChangeLogEntry:
    """ An individual entry from the ‘ChangeLog’ document. """

    __metaclass__ = type

    field_names = [
            'release_date',
            'version',
            'maintainer',
            'body',
            ]

    date_format = "%Y-%m-%d"
    default_version = "UNKNOWN"
    default_release_date = "UNKNOWN"

    def __init__(
            self,
            release_date=default_release_date, version=default_version,
            maintainer=None, body=None):
        self.validate_release_date(release_date)
        self.release_date = release_date

        self.validate_version(version)
        self.version = version

        self.validate_maintainer(maintainer)
        self.maintainer = maintainer
        self.body = body

    @classmethod
    def validate_release_date(cls, value):
        """ Validate the `release_date` value.

            :param value: The prospective `release_date` value.
            :return: ``None`` if the value is valid.
            :raises ValueError: If the value is invalid.
            """
        if value in ["UNKNOWN", "FUTURE"]:
            # A valid non-date value.
            return None

        # Raises `ValueError` if parse fails.
        datetime.datetime.strptime(value, ChangeLogEntry.date_format)

    @classmethod
    def validate_version(cls, value):
        """ Validate the `version` value.

            :param value: The prospective `version` value.
            :return: ``None`` if the value is valid.
            :raises ValueError: If the value is invalid.
            """
        if value in ["UNKNOWN", "NEXT"]:
            # A valid non-version value.
            return None

        valid_version = packaging.version.Version(value)

    @classmethod
    def validate_maintainer(cls, value):
        """ Validate the `maintainer` value.

            :param value: The prospective `maintainer` value.
            :return: ``None`` if the value is valid.
            :raises ValueError: If the value is invalid.
            """
        valid = False

        if value is None:
            valid = True
        elif rfc822_person_regex.search(value):
            valid = True

        if not valid:
            raise ValueError(
                    "not a valid person specification {value!r}".format(
                        value=value))
        else:
            return None

    @classmethod
    def make_ordered_dict(cls, fields):
        """ Make an ordered dict of the fields. """
        result = collections.OrderedDict(
                (name, fields[name])
                for name in cls.field_names)
        return result

    def as_version_info_entry(self):
        """ Format the changelog entry as a version info entry. """
        fields = vars(self)
        entry = self.make_ordered_dict(fields)

        return entry


class InvalidFormatError(ValueError):
    """ Raised when the document is not a valid ‘ChangeLog’ document. """

    def __init__(self, node, message=None):
        self.node = node
        self.message = message

    def __str__(self):
        text = "{message}: {source} line {line}".format(
                message=(
                    self.message if self.message is not None
                    else "(no message)"),
                source=(
                    self.node.source if (
                        hasattr(self.node, 'source')
                        and self.node.source is not None
                        ) else "(source unknown)"
                    ),
                line=(
                    "{:d}".format(self.node.line) if (
                        hasattr(self.node, 'line')
                        and self.node.line is not None
                        ) else "(unknown)"
                    ),
                )

        return text


class VersionInfoTranslator:
    """ Translator from document nodes to a version info stream. """

    # This class needs its base class to be a class from `docutils`.
    # But that would create a circular dependency: Setuptools cannot
    # ensure `docutils` is available before importing this module.
    #
    # Use `ensure_class_bases_begin_with` after importing `docutils`,
    # to re-bind the `VersionInfoTranslator` name to a new type that
    # inherits from `docutils.nodes.SparseNodeVisitor`.

    __metaclass__ = type

    wrap_width = 78
    bullet_text = "* "

    attr_convert_funcs_by_attr_name = {
            'released': ('release_date', str),
            'version': ('version', str),
            'maintainer': ('maintainer', str),
            }

    def __init__(self, document):
        super(VersionInfoTranslator, self).__init__(document)
        self.settings = document.settings
        self.current_field_name = None
        self.content = []
        self.indent_width = 0
        self.initial_indent = ""
        self.subsequent_indent = ""
        self.current_entry = None

        # Docutils is not available when this class is defined.
        # Get the `docutils` module dynamically.
        self._docutils = sys.modules['docutils']

    def astext(self):
        """ Return the translated document as text. """
        text = json.dumps(self.content, indent=4)
        return text

    def append_to_current_entry(self, text):
        if self.current_entry is not None:
            if self.current_entry.body is not None:
                self.current_entry.body += text

    def visit_Text(self, node):
        raw_text = node.astext()
        text = textwrap.fill(
                raw_text,
                width=self.wrap_width,
                initial_indent=self.initial_indent,
                subsequent_indent=self.subsequent_indent)
        self.append_to_current_entry(text)

    def depart_Text(self, node):
        pass

    def visit_comment(self, node):
        raise self._docutils.nodes.SkipNode

    def visit_field_body(self, node):
        field_list_node = node.parent.parent
        if not isinstance(field_list_node, self._docutils.nodes.field_list):
            raise InvalidFormatError(
                    node,
                    "Unexpected field within {node!r}".format(
                        node=field_list_node))
        if not isinstance(
                field_list_node.parent, self._docutils.nodes.section):
            # Field list is not in a section.
            raise self._docutils.nodes.SkipNode
        if self.current_field_name not in self.attr_convert_funcs_by_attr_name:
            raise InvalidFormatError(
                    node,
                    "Unexpected field name {name!r}".format(
                        name=self.current_field_name))
        (attr_name, convert_func) = self.attr_convert_funcs_by_attr_name[
                self.current_field_name]
        attr_value = convert_func(node.astext())
        setattr(self.current_entry, attr_name, attr_value)

    def depart_field_body(self, node):
        pass

    def visit_field_list(self, node):
        pass

    def depart_field_list(self, node):
        self.current_field_name = None
        self.current_entry.body = ""

    def visit_field_name(self, node):
        field_name = node.astext()
        self.current_field_name = field_name.lower()
        field_list_node = node.parent
        if not isinstance(
                field_list_node.parent, self._docutils.nodes.section):
            # Field list is not in a section.
            raise self._docutils.nodes.SkipNode
        if not isinstance(
                field_list_node.parent.parent, self._docutils.nodes.Root):
            # The section is not top-level.
            raise self._docutils.nodes.SkipNode
        if field_name.lower() not in ["released", "maintainer"]:
            raise InvalidFormatError(
                    node,
                    "Unexpected field name {name!r}".format(name=field_name))

    def depart_field_name(self, node):
        pass

    def visit_bullet_list(self, node):
        self.current_context = []

    def depart_bullet_list(self, node):
        self.current_entry.changes = self.current_context
        self.current_context = None

    def adjust_indent_width(self, delta):
        self.indent_width += delta
        self.subsequent_indent = " " * self.indent_width
        self.initial_indent = self.subsequent_indent

    def visit_list_item(self, node):
        indent_delta = +len(self.bullet_text)
        self.adjust_indent_width(indent_delta)
        self.initial_indent = self.subsequent_indent[:-indent_delta]
        self.append_to_current_entry(self.initial_indent + self.bullet_text)

    def depart_list_item(self, node):
        indent_delta = +len(self.bullet_text)
        self.adjust_indent_width(-indent_delta)
        self.append_to_current_entry("\n")

    def visit_section(self, node):
        if not isinstance(node.parent, self._docutils.nodes.Root):
            raise InvalidFormatError(
                    node, "Subsections not implemented for this writer")
        self.current_entry = ChangeLogEntry()

    def depart_section(self, node):
        self.content.append(
                self.current_entry.as_version_info_entry())
        self.current_entry = None

    _expected_title_word_length = len("Version FOO".split(" "))

    def depart_title(self, node):
        title_text = node.astext()
        words = title_text.split(" ")
        version = None
        if len(words) != self._expected_title_word_length:
            raise InvalidFormatError(
                    node,
                    "Unexpected title text {text!r}".format(text=title_text))
        if words[0].lower() not in ["version"]:
            raise InvalidFormatError(
                    node,
                    "Unexpected title text {text!r}".format(text=title_text))
        version = words[-1]
        self.current_entry.version = version


def changelog_to_version_info_collection(infile):
    """ Render the ‘ChangeLog’ document to a version info collection.

        :param infile: A file-like object containing the changelog.
        :return: The serialised JSON data of the version info collection.
        """

    # Docutils is not available when Setuptools needs this module, so
    # delay the imports to this function instead.
    import docutils.core
    import docutils.nodes
    import docutils.writers

    ensure_class_bases_begin_with(
            globals(), 'VersionInfoWriter', docutils.writers.Writer)
    ensure_class_bases_begin_with(
            globals(), 'VersionInfoTranslator',
            docutils.nodes.SparseNodeVisitor)

    writer = VersionInfoWriter()
    settings_overrides = {
            'doctitle_xform': False,
            }
    version_info_json = docutils.core.publish_string(
            infile.read(), writer=writer,
            settings_overrides=settings_overrides)

    return version_info_json


try:
    lru_cache = functools.lru_cache
except AttributeError:
    # Python < 3.2 does not have the `functools.lru_cache` function.
    # Not essential, so replace it with a no-op.
    def lru_cache(maxsize=None, typed=False):
        return (lambda func: func)


@lru_cache(maxsize=128)
def generate_version_info_from_changelog(infile_path):
    """ Get the version info for the latest version in the changelog.

        :param infile_path: Filesystem path to the input changelog file.
        :return: The generated version info mapping; or ``None`` if the
            file cannot be read.

        The document is explicitly opened as UTF-8 encoded text.
        """
    version_info = collections.OrderedDict()

    versions_all_json = None
    try:
        with io.open(infile_path, 'rt', encoding="utf-8") as infile:
            versions_all_json = changelog_to_version_info_collection(infile)
    except EnvironmentError:
        # If we can't read the input file, leave the collection empty.
        pass

    if versions_all_json is not None:
        versions_all = json.loads(versions_all_json.decode('utf-8'))
        # The changelog will have the latest entry first.
        version_info = versions_all[0]

    return version_info


def get_latest_version(versions):
    """ Get the latest version from a collection of changelog entries.

        :param versions: A collection of mappings for changelog entries.
        :return: An ordered mapping of fields for the latest version,
            if `versions` is non-empty; otherwise, an empty mapping.
        """
    version_info = collections.OrderedDict()

    versions_by_release_date = {
            item['release_date']: item
            for item in versions}
    if versions_by_release_date:
        latest_release_date = max(versions_by_release_date.keys())
        version_info = ChangeLogEntry.make_ordered_dict(
                versions_by_release_date[latest_release_date])

    return version_info


def serialise_version_info_from_mapping(version_info):
    """ Generate the version info serialised data.

        :param version_info: Mapping of version info items.
        :return: The version info serialised to JSON.
        """
    content = json.dumps(version_info, indent=4)

    return content


# Copyright © 2008–2023 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; version 3 of that license or any later version.
# No warranty expressed or implied. See the file ‘LICENSE.GPL-3’ for details.


# Local variables:
# coding: utf-8
# mode: python
# End:
# vim: fileencoding=utf-8 filetype=python :
