# -*- coding: utf-8 -*-
"""
Extension that adjust project file tree to include a namespace package.

This extension adds a **namespace** option to
:obj:`~pyscaffold.api.create_project` and provides correct values for the
options **root_pkg** and **namespace_pkg** to the following functions in the
action list.
"""
from __future__ import absolute_import

import argparse

from .. import templates, utils


def augment_cli(parser):
    """Add an option to parser that enables the namespace extension.

    Args:
        parser (argparse.ArgumentParser): CLI parser object
    """
    parser.add_argument(
        "--with-namespace",
        dest="namespace",
        action=ActivateNamespace,
        metavar="NS1[.NS2]",
        help="put your project inside a namespace package")


class ActivateNamespace(argparse.Action):
    """Consumes the values provided, but also append the extension function
    to the extensions list.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        # First ensure the extension function is stored inside the
        # 'extensions' attribute:
        extensions = getattr(namespace, 'extensions', [])
        extensions.append(extend_project)
        setattr(namespace, 'extensions', extensions)

        # Now the extra parameters can be stored
        setattr(namespace, self.dest, values)


def extend_project(actions, helpers):
    """Register an action responsible for adding namespace to the package."""
    actions = helpers.register(actions, enforce_namespace_options,
                               after='get_default_options')

    return helpers.register(actions, add_namespace,
                            before='apply_update_rules')


def enforce_namespace_options(struct, opts):
    """Make sure options reflect the namespace usage."""
    opts.setdefault('namespace', None)

    if opts['namespace']:
        opts['namespace'] = utils.prepare_namespace(opts['namespace'])
        opts['root_pkg'] = opts['namespace'][0]
        opts['namespace_pkg'] = ".".join([opts['namespace'][-1],
                                          opts['package']])

    return (struct, opts)


def add_namespace(struct, opts):
    """Prepend the namespace to a given file structure

    Args:
        struct (dict): directory structure as dictionary of dictionaries
        opts (dict): options of the project

    Returns:
        tuple(dict, dict):
            directory structure as dictionary of dictionaries and input options
    """
    if not opts['namespace']:
        return (struct, opts)

    namespace = opts['namespace'][-1].split('.')
    base_struct = struct
    pkg_struct = struct[opts['project']][opts['package']]
    struct = base_struct[opts['project']]
    del struct[opts['package']]
    for sub_package in namespace:
        struct[sub_package] = {'__init__.py': templates.namespace(opts)}
        struct = struct[sub_package]
    struct[opts['package']] = pkg_struct

    return (base_struct, opts)
