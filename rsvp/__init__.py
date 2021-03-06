# RSVP Main File
from uuid import uuid4

from rsvp.helpers import RSVP_Helpers
from rsvp.constants import MEMBER_KEYS
from rsvp.exceptions import EXCEPTION_MESSAGES

MEMBERS_KEY = 'event_members'
helpers = RSVP_Helpers()
store_file_name = ''


def _locate_file(event_id):
    all_files = helpers.get_all_store_files()
    required_file = [file for file in all_files if event_id in file]
    if isinstance(required_file, list) and len(required_file) > 0:
        return required_file[0]
    return ''


def create_rsvp_store(*source, **event_details):
    """
    Creates a new RSVP store object
    :param source: Source details
        - rsvp_source           string
    :param event_details: Event detail kwargs
        - event_slug            slug
        - event_name            string
        - event_description     string
        - event_start_date      datetime
        - event_end_date        datetime
        - event_members         list

    :return: event_id           uuid as string
    """
    if not isinstance(source, (list, tuple)) and len(source) > 0:
        raise Exception(EXCEPTION_MESSAGES['SOURCE_NOT_FOUND'])

    rsvp_source = source[0]
    if not event_details.get('event_slug'):
        raise Exception(EXCEPTION_MESSAGES['EVENT_SLUG_NOT_FOUND'])

    if not event_details.get('event_start_date'):
        raise Exception(EXCEPTION_MESSAGES['START_DATE_NOT_FOUND'])

    event_id = uuid4()
    event_master_dict = dict()
    event_master_dict['event_id'] = str(event_id)
    event_master_dict['event_source'] = rsvp_source
    event_master_dict['event_slug'] = event_details['event_slug']
    event_master_dict['event_name'] = event_details.get('event_name')
    event_master_dict['event_description'] = event_details.get('event_description')
    event_master_dict['event_start_date'] = str(event_details['event_start_date'])
    event_master_dict['event_end_date'] = str(event_details.get('event_end_date'))
    event_master_dict[MEMBERS_KEY] = event_details.get('event_members', [])

    store_file_name = str(event_id) + '.' + event_details['event_slug']
    if helpers.save_rsvp(store_file_name, event_master_dict):
        return str(event_id)
    return


def delete_rsvp_store(event_id):
    """
    Deletes RSVP store file
    :param event_id: uuid as string
    :return: boolean
    """
    file_to_delete = _locate_file(event_id)
    if file_to_delete and helpers.delete_store_file(file_to_delete):
            return True
    return False


def add_members(event_id, members):
    """
    Add members to event
    :param event_id: uuid as string
    :param members: list of names (string)
    :return: boolean
    """
    file_to_append = _locate_file(event_id)
    event_data = helpers.load_file_data(file_to_append)
    member_keys_dict = {key: False for key in MEMBER_KEYS}
    members_list = [{member: member_keys_dict} for member in members]
    event_data[MEMBERS_KEY].extend(members_list)
    if helpers.save_rsvp(file_to_append, event_data):
        return True
    return False


def adjust_rsvp_state(event_id, members, **states):
    """
    Set rsvp for members for an event
    :param event_id: uuid as string
    :param members: list
    :param states: dict example {'in_queue_waiting': true}
    :return: boolean
    """
    file_to_update = _locate_file(event_id)
    event_data = helpers.load_file_data(file_to_update)

    for member_rsvp in event_data.get(MEMBERS_KEY, []):
        member = [m for m in members if member_rsvp.get(m)]
        if member and len(member) == 1:
            member = member[0]
            new_state = {i: states.get(i, j) for i, j in member_rsvp[member].items()}
            member_index = event_data[MEMBERS_KEY].index(member_rsvp)
            event_data[MEMBERS_KEY].pop(member_index)
            event_data[MEMBERS_KEY].insert(
                member_index, {member: new_state}
            )
    if helpers.save_rsvp(file_to_update, event_data):
        return True
    return False


def get_rsvp_state(event_id, members):
    """
    Get rsvp for members for an event
    :param event_id: uuid as string
    :param members: list
    :return: list of dict
    """
    members_rsvp = []
    file_to_update = _locate_file(event_id)
    event_data = helpers.load_file_data(file_to_update)
    members_data = event_data.get(MEMBERS_KEY, [])
    if members_data:
        [members_rsvp.append(member) for member in members_data if list(member)[0] in members]
    return members_rsvp
