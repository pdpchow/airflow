#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""Manages all plugins."""
# noinspection PyDeprecation
import importlib
import inspect
import logging
import os
import sys
import types
from typing import Any, Dict, List, Optional, Type

import pkg_resources

from airflow import settings

log = logging.getLogger(__name__)

import_errors = {}

plugins = None  # type: Optional[List[AirflowPlugin]]

# Plugin components to integrate as modules
operators_modules = []
sensors_modules = []
hooks_modules = []
executors_modules = []
macros_modules = []

# Plugin components to integrate directly
admin_views: List[Any] = []
flask_blueprints: List[Any] = []
menu_links: List[Any] = []
flask_appbuilder_views: List[Any] = []
flask_appbuilder_menu_links: List[Any] = []
global_operator_extra_links: List[Any] = []
operator_extra_links: List[Any] = []
registered_operator_link_classes: Dict[str, Type] = {}
"""Mapping of class names to class of OperatorLinks registered by plugins.

Used by the DAG serialization code to only allow specific classes to be created
during deserialization
"""


class AirflowPluginException(Exception):
    """Exception when loading plugin."""


class AirflowPlugin:
    """Class used to define AirflowPlugin."""
    name: Optional[str] = None
    operators: List[Any] = []
    sensors: List[Any] = []
    hooks: List[Any] = []
    executors: List[Any] = []
    macros: List[Any] = []
    admin_views: List[Any] = []
    flask_blueprints: List[Any] = []
    menu_links: List[Any] = []
    appbuilder_views: List[Any] = []
    appbuilder_menu_items: List[Any] = []

    # A list of global operator extra links that can redirect users to
    # external systems. These extra links will be available on the
    # task page in the form of buttons.
    #
    # Note: the global operator extra link can be overridden at each
    # operator level.
    global_operator_extra_links: List[Any] = []

    # A list of operator extra links to override or add operator links
    # to existing Airflow Operators.
    # These extra links will be available on the task page in form of
    # buttons.
    operator_extra_links: List[Any] = []

    @classmethod
    def validate(cls):
        """Validates that plugin has a name."""
        if not cls.name:
            raise AirflowPluginException("Your plugin needs a name.")

    @classmethod
    def on_load(cls, *args, **kwargs):
        """
        Executed when the plugin is loaded.
        This method is only called once during runtime.

        :param args: If future arguments are passed in on call.
        :param kwargs: If future arguments are passed in on call.
        """


def is_valid_plugin(plugin_obj):
    """
    Check whether a potential object is a subclass of
    the AirflowPlugin class.

    :param plugin_obj: potential subclass of AirflowPlugin
    :return: Whether or not the obj is a valid subclass of
        AirflowPlugin
    """
    global plugins  # pylint: disable=global-statement

    if (
        inspect.isclass(plugin_obj) and
        issubclass(plugin_obj, AirflowPlugin) and
        (plugin_obj is not AirflowPlugin)
    ):
        plugin_obj.validate()
        return plugin_obj not in plugins
    return False


def load_entrypoint_plugins():
    """
    Load and register plugins AirflowPlugin subclasses from the entrypoints.
    The entry_point group should be 'airflow.plugins'.
    """
    global plugins  # pylint: disable=global-statement

    entry_points = pkg_resources.iter_entry_points('airflow.plugins')

    log.debug("Loading plugins from entrypoints")

    for entry_point in entry_points:
        log.debug('Importing entry_point plugin %s', entry_point.name)
        plugin_obj = entry_point.load()
        if is_valid_plugin(plugin_obj):
            if callable(getattr(plugin_obj, 'on_load', None)):
                plugin_obj.on_load()
                plugins.append(plugin_obj)


def load_plugins_from_plugin_directory():
    """
    Load and register Airflow Plugin from plugin directory
    """
    global import_errors  # pylint: disable=global-statement
    global plugins  # pylint: disable=global-statement
    log.debug("Loading plugins from directory: %s", settings.PLUGINS_FOLDER)

    # Crawl through the plugins folder to find AirflowPlugin derivatives
    for root, _, files in os.walk(settings.PLUGINS_FOLDER, followlinks=True):  # noqa # pylint: disable=too-many-nested-blocks
        for f in files:
            filepath = os.path.join(root, f)
            try:
                if not os.path.isfile(filepath):
                    continue
                mod_name, file_ext = os.path.splitext(
                    os.path.split(filepath)[-1])
                if file_ext != '.py':
                    continue

                log.debug('Importing plugin module %s', filepath)

                loader = importlib.machinery.SourceFileLoader(mod_name, filepath)
                spec = importlib.util.spec_from_loader(mod_name, loader)
                mod = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = mod
                loader.exec_module(mod)
                for obj in list(mod.__dict__.values()):
                    if is_valid_plugin(obj):
                        plugins.append(obj)
            except Exception as e:  # pylint: disable=broad-except
                log.exception(e)
                path = filepath or str(f)
                log.error('Failed to import plugin %s', path)
                import_errors[path] = str(e)


# pylint: disable=protected-access
# noinspection Mypy,PyTypeHints
def make_module(name: str, objects: List[Any]):
    """Creates new module."""
    log.debug('Creating module %s', name)
    name = name.lower()
    module = types.ModuleType(name)
    module._name = name.split('.')[-1]  # type: ignore
    module._objects = objects           # type: ignore
    module.__dict__.update((o.__name__, o) for o in objects)
    return module
# pylint: enable=protected-access


def endure_plugins_loaded():
    """
    Load plugins from plugins directory and entrypoints.

    Plugins are only loaded if they have not been previously loaded.
    """
    global plugins  # pylint: disable=global-statement

    if plugins is not None:
        log.debug("Plugins are already loaded. Skipping.")
        return

    if not settings.PLUGINS_FOLDER:
        raise ValueError("Plugins folder is not set")

    log.debug("Loading plugins")

    plugins = []

    load_plugins_from_plugin_directory()
    load_entrypoint_plugins()

    initialize_plugins()


def initialize_plugins():
    """Creates modules for loaded extension from plugins"""
    # pylint: disable=global-statement
    global plugins
    global operators_modules
    global sensors_modules
    global hooks_modules
    global executors_modules
    global macros_modules

    global admin_views
    global flask_blueprints
    global menu_links
    global flask_appbuilder_views
    global flask_appbuilder_menu_links
    global global_operator_extra_links
    global operator_extra_links
    global registered_operator_link_classes
    # pylint: enable=global-statement

    log.debug("Initialize plugin modules")

    for plugin in plugins:
        plugin_name: str = plugin.name
        operators_modules.append(
            make_module('airflow.operators.' + plugin_name, plugin.operators + plugin.sensors))
        sensors_modules.append(
            make_module('airflow.sensors.' + plugin_name, plugin.sensors)
        )
        hooks_modules.append(make_module('airflow.hooks.' + plugin_name, plugin.hooks))
        executors_modules.append(
            make_module('airflow.executors.' + plugin_name, plugin.executors))
        macros_modules.append(make_module('airflow.macros.' + plugin_name, plugin.macros))

        admin_views.extend(plugin.admin_views)
        menu_links.extend(plugin.menu_links)
        flask_appbuilder_views.extend(plugin.appbuilder_views)
        flask_appbuilder_menu_links.extend(plugin.appbuilder_menu_items)
        flask_blueprints.extend([{
            'name': plugin.name,
            'blueprint': bp
        } for bp in plugin.flask_blueprints])
        global_operator_extra_links.extend(plugin.global_operator_extra_links)
        operator_extra_links.extend(list(plugin.operator_extra_links))

        registered_operator_link_classes.update({
            "{}.{}".format(link.__class__.__module__,
                           link.__class__.__name__): link.__class__
            for link in plugin.operator_extra_links
        })


def integrate_executor_plugins() -> None:
    """Integrate executor plugins to the context."""
    endure_plugins_loaded()

    log.debug("Integrate executor plugins")

    for executors_module in executors_modules:
        sys.modules[executors_module.__name__] = executors_module
        # noinspection PyProtectedMember
        globals()[executors_module._name] = executors_module  # pylint: disable=protected-access


def integrate_dag_plugins() -> None:
    """Integrates operator, sensor, hook, macro plugins."""
    endure_plugins_loaded()

    log.debug("Integrate DAG plugins.")

    for operators_module in operators_modules:
        sys.modules[operators_module.__name__] = operators_module
        # noinspection PyProtectedMember
        globals()[operators_module._name] = operators_module  # pylint: disable=protected-access

    for sensors_module in sensors_modules:
        sys.modules[sensors_module.__name__] = sensors_module
        # noinspection PyProtectedMember
        globals()[sensors_module._name] = sensors_module  # pylint: disable=protected-access

    for hooks_module in hooks_modules:
        sys.modules[hooks_module.__name__] = hooks_module
        # noinspection PyProtectedMember
        globals()[hooks_module._name] = hooks_module  # pylint: disable=protected-access

    for macros_module in macros_modules:
        sys.modules[macros_module.__name__] = macros_module
        # noinspection PyProtectedMember
        globals()[macros_module._name] = macros_module  # pylint: disable=protected-access
