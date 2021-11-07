from log import log
import os
import sys
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

dbx = dropbox.Dropbox(os.environ.get('DROPBOX_ACCESS_TOKEN'))


def login():
    # Check that the access token is valid
    try:
        dbx.users_get_current_account()
    except AuthError:
        sys.exit("ERROR: Invalid access token; try re-generating an "
                 "access token from the app console on the web.")


# Change the text string in LOCALFILE to be new_content
# @param new_content is a string
def change_local_file(local_file_name, new_content):
    log("Changing contents of " + local_file_name + " on local machine...")
    with open(local_file_name, 'wb') as f:
        f.write(new_content)


def get_document(filename):
    # Download the specific revision of the file at BACKUPPATH to LOCALFILE
    log("Downloading current " + './{}'.format(filename) + " from Dropbox, overwriting " + filename + "...")
    return dbx.files_download_to_file('./{}'.format(filename), '/{}'.format(filename), None)
    # return dbx.files_download('PokeDolar/{}'.format(filename))


def save_document(filename):
    with open(filename, 'rb') as f:
        # We use WriteMode=overwrite to make sure that the settings in the file
        # are changed on upload
        log("Uploading " + filename + " to Dropbox as " + './{}'.format(filename) + "...")
        try:
            dbx.files_upload(f.read(), '/{}'.format(filename), mode=WriteMode('overwrite'))
        except ApiError as err:
            # This checks for the specific error where a user doesn't have
            # enough Dropbox space quota to upload this file
            if (err.error.is_path() and
                    err.error.get_path().reason.is_insufficient_space()):
                sys.exit("ERROR: Cannot back up; insufficient space.")
            elif err.user_message_text:
                log(err.user_message_text)
                sys.exit()
            else:
                log(err)
                sys.exit()
