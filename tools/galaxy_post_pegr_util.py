#These are the functions taken from https://github.com/seqcode/cegr-galaxy/tree/master/tools/cegr_statistics
#with small modification to be used for generalized Galaxy-PEGR API tool

import fileinput
import json
import numpy
import os
import shlex
import string
import subprocess
import sys
import tempfile
import ssl

#import configparser
from configparser import ConfigParser
from six.moves.urllib.error import HTTPError, URLError
from six.moves.urllib.request import Request, urlopen
from six import string_types
from bioblend import galaxy


# Allows characters that are escaped to be un-escaped.
MAPPED_CHARS = {'>': '__gt__',
                '<': '__lt__',
                "'": '__sq__',
                '"': '__dq__',
                '[': '__ob__',
                ']': '__cb__',
                '{': '__oc__',
                '}': '__cc__',
                '@': '__at__',
                '\n': '__cn__',
                '\r': '__cr__',
                '\t': '__tc__',
                '#': '__pd__'}
# Maximum value of a signed 32 bit integer (2**31 - 1).
MAX_GENOME_SIZE = 2147483647


def check_response(pegr_url, payload, response):
    try:
        s = json.dumps(payload)
        response_code = response.get('response_code', None)
        if response_code not in ['200']:
            err_msg = 'Error sending statistics to PEGR!\n\nPEGR URL:\n%s\n\n' % str(pegr_url)
            err_msg += 'Payload:\n%s\n\nResponse:\n%s\n' % (s, str(response))
            if response_code in ['500']:
                # The payload may not have included all items
                # required by PEGR, so write the error but
                # don't exit.
                sys.stderr.write(err_msg)
            else:
                # PEGR is likely unavailable, so exit.
                stop_err(err_msg)
    except Exception as e:
        err_msg = 'Error handling response from PEGR!\n\nException:\n%s\n\n' % str(e)
        err_msg += 'PEGR URL:\n%s\n\nPayload:\n%s\n\nResponse:\n%s\n' % (pegr_url, s, str(response))
        sys.stderr.write(err_msg)



def format_tool_parameters(parameters):
    s = parameters.lstrip('__SeP__')
    items = s.split('__SeP__')
    params = {}
    param_index = 0
    ## python 3 notation update
    for i in range(int(len(items) / 2)):
        params[restore_text(items[param_index])] = restore_text(items[param_index + 1])
        param_index += 2
    return params



def get_base_json_dict(config_file, dbkey, history_id, history_name, stats_tool_id, stderr, tool_id, tool_parameters, user_email, workflow_step_id):
    d = {}
    d['genome'] = dbkey
    d['historyId'] = history_id
    d['parameters'] = format_tool_parameters(tool_parameters)
    d['run'] = get_run_from_history_name(history_name)
    d['sample'] = get_sample_from_history_name(history_name)
    d['statsToolId'] = stats_tool_id
    d['toolCategory'] = "Unknown" #get_tool_category(config_file, tool_id)
    d['toolStderr'] = stderr
    d['toolId'] = tool_id
    d['userEmail'] = user_email
    d['workflowId'] = get_workflow_id(config_file, history_name)
    d['workflowStepId'] = workflow_step_id
    return d


def get_config_settings(config_file, section='defaults'):
    d = {}
    config_parser = ConfigParser()
    config_parser.read(config_file)
    for key, value in config_parser.items(section):
        if section == 'defaults':
            ## python3 updated notation
            d[key.upper()] = value   
        else:
            d[key] = value
    return d


def get_datasets(config_file, ids, datatypes):
    # URL sample: http://localhost:8763/datasets/eca0af6fb47bf90c/display/?preview=True
    defaults = get_config_settings(config_file, section='defaults')
    d = {}
    for i, t in zip(listify(ids), listify(datatypes)):
        d['id'] = i
        d['type'] = t
        d['uri'] = '%s/datasets/%s/display?preview=True' % (defaults['GALAXY_BASE_URL'], i)
    return d


# This function is written based on history url format in Galaxy 19.05 and it is server agnostic.
def get_history_url(config_file, historyId):
    # URL sample: http://hermes.vmhost.psu.edu:8080/histories/view?id=1e8ab44153008be8
    defaults = get_config_settings(config_file, section='defaults')
    return '%s/histories/view?id=%s' % (defaults['GALAXY_BASE_URL'],historyId)



def get_galaxy_instance(api_key, url):
    return galaxy.GalaxyInstance(url=url, key=api_key)


def get_galaxy_url(config_file):
    defaults = get_config_settings(config_file, section='defaults')
    return make_url(defaults['GALAXY_API_KEY'], defaults['GALAXY_BASE_URL'])



def get_number_of_lines(file_path):
    i = 0
    with open(file_path) as fh:
        for i, l in enumerate(fh):
            pass
    fh.close()
    if i == 0:
        return i
    return i + 1




def get_pegr_url(config_file):
    defaults = get_config_settings(config_file)
    return make_url(defaults['PEGR_API_KEY'], defaults['PEGR_URL'])




def get_reads(cmd):
    try:
        reads = '%.2f' % float(subprocess.check_output(shlex.split(cmd)))
        return float(reads)
    except Exception as e:
        stop_err('Error getting reads: %s' % str(e))


def get_run_from_history_name(history_name, exit_on_error=False):
    # Example: paired_001-199-10749.001
    try:
        run = int(history_name.split('-')[1])
    except Exception as e:
        if exit_on_error:
            stop_err('History name is likely invalid, it does not contain a run: %s' % str(e))
        return 'unknown'
    return run


def get_sample_from_history_name(history_name, exit_on_error=False):
    # Example: paired_001-199-10749.001
    items = history_name.split('-')
    try:
        sample = int(items[2].split('.')[0])
    except Exception as e:
        if exit_on_error:
            stop_err('History name is likely invalid, it does not contain a sample: %s' % str(e))
        return 'unknown'
    return sample


def get_tmp_filename(dir=None, suffix=None):
    fd, name = tempfile.mkstemp(suffix=suffix, dir=dir)
    os.close(fd)
    return name



def get_total_reads(file_path, single=False):
    if single:
        cmd = "samtools view -c %s" % file_path
    else:
        cmd = "samtools view -f 0x40 -c %s" % file_path
    return get_reads(cmd)


def get_workflow_id(config_file, history_name):
    workflow_name = get_workflow_name_from_history_name(history_name)
    print ('history name is:')
    print (workflow_name)
    if workflow_name == 'unknown':
        return 'unknown'
    defaults = get_config_settings(config_file)
    gi = get_galaxy_instance(defaults['GALAXY_API_KEY'], defaults['GALAXY_BASE_URL'])
    print ("after fetching galaxy")
    workflow_info_dicts = gi.workflows.get_workflows(name=workflow_name)
    if len(workflow_info_dicts) == 0:
        return 'unknown'
    wf_info_dict = workflow_info_dicts[0]
    return wf_info_dict['id']


def get_workflow_name_from_history_name(history_name, exit_on_error=False):
    # Example: paired_001-199-10749.001
    items = history_name.split('-')
    try:
        workflow_name = items[0]
    except Exception as e:
        if exit_on_error:
            stop_err('History name is likely invalid, it does not contain a workflow name: %s' % str(e))
        return 'unknown'
    return workflow_name


def listify(item, do_strip=False):
    """
    Make a single item a single item list, or return a list if passed a
    list.  Passing a None returns an empty list.
    """
    if not item:
        return []
    elif isinstance(item, list):
        return item
    elif isinstance(item, string_types) and item.count(','):
        if do_strip:
            return [token.strip() for token in item.split(',')]
        else:
            return item.split(',')
    else:
        return [item]


def make_url(api_key, url, args=None):
    """
    Adds the API Key to the URL if it's not already there.
    """
    if args is None:
        args = []
    argsep = '&'
    if '?' not in url:
        argsep = '?'
    if '?apiKey=' not in url and '&apiKey=' not in url:
        args.insert(0, ('apiKey', api_key))
    return url + argsep + '&'.join(['='.join(t) for t in args])


def post(api_key, url, data):
    url = make_url(api_key, url)
    print (type(data))
    gcontext = ssl.SSLContext()
    data=json.dumps(data)
    response = Request(url, headers={'Content-Type': 'application/json'}, data=data.encode("utf-8"))
    #webURL=urlopen(response, context=gcontext)
    #data=webURL.read()
    #encoding=webURL.info().get_content_charset('utf-8')
    #print (json.loads(data.decode(encoding)))
    #print (' I am here again 4')
    return json.loads(urlopen(response, context=gcontext).read())


def restore_text(text, character_map=MAPPED_CHARS):
    """Restores sanitized text"""
    if not text:
        return text
    for key, value in character_map.items():
        text = text.replace(value, key)
    return text


def stop_err(msg):
    sys.stderr.write(msg)
    sys.exit()


def store_results(file_path, pegr_url, payload, response):
    with open(file_path, 'w') as fh:
        # Eliminate the API key from the PEGR url.
        items = pegr_url.split('?')
        fh.write("pegr_url:\n%s\n\n" % str(items[0]))
        fh.write("payload:\n%s\n\n" % json.dumps(payload))
        fh.write("response:\n%s\n" % str(response))
        fh.close()


def submit(config_file, data):
    """
    Sends an API POST request and acts as a generic formatter for the JSON response.
    'data' will become the JSON payload read by Galaxy.
    """
    defaults = get_config_settings(config_file)
    try:
        return post(defaults['PEGR_API_KEY'], defaults['PEGR_URL'], data)
    except HTTPError as e:
        return json.loads(e.read())
    except URLError as e:
        return dict(response_code=None, message=str(e))
    except Exception as e:
        try:
            return dict(response_code=None, message=e.read())
        except:
            return dict(response_code=None, message=str(e))


def which(file):
    # http://stackoverflow.com/questions/5226958/which-equivalent-function-in-python
    for path in os.environ["PATH"].split(":"):
        if os.path.exists(path + "/" + file):
            return path + "/" + file
    return None
