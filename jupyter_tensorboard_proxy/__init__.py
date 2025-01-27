import os
import shutil
import logging
from dotenv import load_dotenv


logger = logging.getLogger(__name__)
logger.setLevel('INFO')


def setup_tensorboard():
    """Setup commands and icon paths and return a dictionary compatible
    with jupyter-server-proxy.
    """
    def _get_icon_path():
        return os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'icons', 'tensorboard.svg'
    )

    # Make sure executable is in $PATH
    def _get_tensorboard_command(port):
        """
        Takes in port number and returns a tensorboard command like this:
            `tensorboard --logdir {TF_LOG_DIR} --port {port}`
        
        TF_LOG_DIR and AWS/S3 credentials (if relevant) can be curated either:
            - as environment variables, or
            - in a file named ~/.tensorboard
        
        If TF_LOG_DIR is not provided, the logdir defaults to the $HOME/logs directory
        
        If TF_LOG_DIR is specified as an s3:// bucket, required variables in environment
        or ~/.tensorboard include:
        
            - AWS_ACCESS_KEY_ID
            - AWS_SECRET_ACCESS_KEY
            - AWS_DEFAULT_REGION
            - S3_ENDPOINT_URL (if not official AWS)
        """
        executable = shutil.which('tensorboard')
        if not executable:
            raise FileNotFoundError('Can not find tensorboard executable in $PATH')
        # first check for --logdir override as TF_LOG_DIR environment variable
        if os.environ.get('TF_LOG_DIR'):
            TF_LOG_DIR = os.environ.get('TF_LOG_DIR')
        # second check if it is in a specific file called $HOME/.tensorboard
        elif os.path.isfile("%s/.tensorboard" % os.environ.get('HOME')):
            load_dotenv("%s/.tensorboard" % os.environ.get('HOME'))
        # As a last resort, use a local --logdir in the home directory
        else:
            home_dir = os.environ.get('HOME') or "/home/%s" % os.environ.get('NB_USER') or '/home/jovyan'
            working_dir = f'{home_dir}'
            if not os.path.exists(working_dir):
                os.makedirs(working_dir)
                logger.info("Created directory %s" % working_dir)
            else:
                logger.info("Directory %s already exists" % working_dir)
            TF_LOG_DIR = '%s/logs' % home_dir
        return ['tensorboard', '--logdir', TF_LOG_DIR, '--port', '{port}']
    
    return {
        'command': _get_tensorboard_command,
        'port': 6006,
        'timeout': 20,
        'new_browser_tab': True,
        'launcher_entry': {
            'title': 'Tensorboard',
            'icon_path': _get_icon_path()
        },
    }
