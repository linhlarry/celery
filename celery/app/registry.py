# -*- coding: utf-8 -*-
"""
    celery.app.registry
    ~~~~~~~~~~~~~~~~~~~

    Registry of available tasks.

"""
from __future__ import absolute_import

import inspect

from celery.exceptions import NotRegistered


class TaskRegistry(dict):
    NotRegistered = NotRegistered

    def __missing__(self, key):
        raise self.NotRegistered(key)

    def register(self, task):
        """Register a task in the task registry.

        The task will be automatically instantiated if not already an
        instance.

        """
        self[task.name] = inspect.isclass(task) and task() or task

    def unregister(self, name):
        """Unregister task by name.

        :param name: name of the task to unregister, or a
            :class:`celery.task.base.Task` with a valid `name` attribute.

        :raises celery.exceptions.NotRegistered: if the task has not
            been registered.

        """
        try:
            self.pop(getattr(name, 'name', name))
        except KeyError:
            raise self.NotRegistered(name)

    # -- these methods are irrelevant now and will be removed in 3.0
    def regular(self):
        return self.filter_types('regular')

    def periodic(self):
        return self.filter_types('periodic')

    def filter_types(self, type):
        return dict((name, task) for name, task in self.iteritems()
                                if getattr(task, 'type', 'regular') == type)


def _unpickle_task(name):
    from celery import current_app
    return current_app.tasks[name]