"""
Functions to manipulate tasks via REST API.
"""

from __future__ import unicode_literals

from celery.result import AsyncResult
from celery.states import FAILURE, SUCCESS, REVOKED
from django.contrib.auth.models import User
from django.http.response import Http404
from rest_framework.exceptions import ValidationError

from exporter.tasks import export_resources
from learningresources.api import get_repo
from learningresources.models import LearningResource

TASK_KEY = 'tasks'
EXPORT_TASK_TYPE = 'resource_export'
EXPORTS_KEY = 'learning_resource_exports'
IMPORT_TASK_TYPE = 'import_course'


def create_initial_task_dict(task, task_type, task_info):
    """
    Create initial task data about a newly created Celery task.

    Args:
        task (Task): A Celery task.
        task_type (unicode): Type of task.
        task_info (dict): Extra information about a task.
    Returns:
        dict: Initial data about task.
    """

    result = None
    if task.successful():
        result = task.get()
    elif task.failed():
        result = {'error': str(task.result)}

    return {
        "id": task.id,
        "initial_state": task.state,
        "task_type": task_type,
        "task_info": task_info,
        "result": result
    }


def create_task_result_dict(initial_data):
    """
    Convert initial data we put in session to dict for REST API.
    This will use the id to look up current data about task to return
    to user.

    Args:
        task (dict): Initial data about task stored in session.
    Returns:
        dict: Updated data about task.
    """
    initial_state = initial_data['initial_state']
    task_id = initial_data['id']
    task_type = initial_data['task_type']
    task_info = initial_data['task_info']

    state = "processing"
    result = None
    # initial_state is a workaround for EagerResult used in testing.
    # In production initial_state should usually be pending.
    async_result = AsyncResult(task_id)

    if initial_state == SUCCESS:
        state = "success"
        result = initial_data['result']
    elif initial_state in (FAILURE, REVOKED):
        state = "failure"
        result = initial_data['result']
    elif async_result.successful():
        state = "success"
        result = async_result.get()
    elif async_result.failed():
        state = "failure"
        result = {'error': str(async_result.result)}

    return {
        "id": task_id,
        "status": state,
        "result": result,
        "task_type": task_type,
        "task_info": task_info
    }


def get_tasks(session):
    """
    Get initial task data for session.

    Args:
        session (SessionStore): The request session.
    Returns:
        dict:
            The initial task data stored in session for all user's tasks. The
            keys are task ids and the values are initial task data.
    """
    try:
        return session[TASK_KEY]
    except KeyError:
        return {}


def get_task(session, task_id):
    """
    Get initial task data for a single task.

    Args:
        session (SessionStore): The request session.
        task_id (unicode): The task id.
    Returns:
        dict: The initial task data stored in session.
    """
    try:
        return session[TASK_KEY][task_id]
    except KeyError:
        return None


def track_task(session, task, task_type, task_info):
    """
    Add a Celery task to the session.

    Args:
        session (SessionStore): The request session.
        task_type (unicode): The type of task being started.
        task_info (dict): Extra information about the task.
    Returns:
        dict: The initial task data (will also be stored in session).
    """
    initial_data = create_initial_task_dict(task, task_type, task_info)
    if TASK_KEY not in session:
        session[TASK_KEY] = {}
    session[TASK_KEY][task.id] = initial_data
    session.modified = True
    return initial_data


def create_task(session, user_id, task_type, task_info):
    """
    Start a new Celery task from REST API.

    Args:
        session (SessionStore): The request session.
        user_id (int): The id for user creating task.
        task_type (unicode): The type of task being started.
        task_info (dict): Extra information about the task.
    Returns:
        dict: The initial task data (will also be stored in session).
    """

    if task_type == EXPORT_TASK_TYPE:
        try:
            repo_slug = task_info['repo_slug']
        except KeyError:
            raise ValidationError("Missing repo_slug")

        # Verify repository ownership.
        get_repo(repo_slug, user_id)

        try:
            exports = set(session[EXPORTS_KEY][repo_slug])
        except KeyError:
            exports = set()

        try:
            ids = task_info['ids']
        except KeyError:
            raise ValidationError("Missing ids")

        for resource_id in ids:
            if resource_id not in exports:
                raise ValidationError("id {id} is not in export list".format(
                    id=resource_id
                ))

        learning_resources = LearningResource.objects.filter(id__in=ids).all()
        user = User.objects.get(id=user_id)
        result = export_resources.delay(learning_resources, user.username)

        # Put new task in session.
        initial_data = track_task(session, result, task_type, task_info)

        return initial_data
    else:
        raise ValidationError("Unknown task_type {task_type}".format(
            task_type=task_type
        ))


def remove_task(session, task_id):
    """
    Cancel task and remove task from task list.

    Args:
        session (SessionStore): The request session.
        task_id (int): The task id.
    """
    tasks = session.get(TASK_KEY, {})
    if task_id not in tasks:
        raise Http404

    AsyncResult(task_id).revoke()
    del tasks[task_id]
    session[TASK_KEY] = tasks
