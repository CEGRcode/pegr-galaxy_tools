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
import gzip

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

def is_gz_file(filepath):
    """
    Check first byte of file to see if it is gzipped
    """
    with open(filepath, 'rb') as test_f:
        return test_f.read(2) == b'\x1f\x8b'

def openfile(filepath, mode='r'):
    if (is_gz_file(filepath)):
        return gzip.open(filepath, mode) 
    return open(filepath, mode)


def get_number_of_lines(file_path):
    """
    Get line count using wc -l for optionally gzipped file
    """
    line_ct = 0
    if (is_gz_file(file_path)):
        gz_process = subprocess.Popen(('gzip', '-dc', file_path), stdout=subprocess.PIPE)
        line_ct = int(subprocess.check_output(('wc', '-l'), stdin=gz_process.stdout).strip().split(b' ')[0])
    else:
        line_ct = int(subprocess.check_output(('wc', '-l', file_path)).strip().split(b' ')[0])
    return (line_ct)


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


def check_samtools():
    samtools_exec = which('samtools')
    if not samtools_exec:
        stop_err('Attempting to use functionality requiring samtools, but it cannot be located on Galaxy\'s PATH.')


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


def get_adapter_dimer_count(file_path):
    adapter_dimer_count = 0.0
    with open(file_path) as fh:
        in_count_section = False
        for i, line in enumerate(fh):
            if line.startswith('>>Overrepresented sequences'):
                in_count_section = True
            if in_count_section:
                if line.startswith('#'):
                    # Skip comments.
                    continue
                line = line.strip()
                items = line.split('\t')
                if len(items) > 3 and items[3].startswith('TruSeq Adapter'):
                    adapter_dimer_count += float(items[1])
                    in_count_section = False
    fh.close()
    adapter_dimer_count = '%.2f' % adapter_dimer_count
    return float(adapter_dimer_count)


def get_base_json_dict(config_file, dbkey, history_id, history_name, stats_tool_id, stderr, tool_id, tool_category, tool_parameters, user_email, workflow_step_id):
    d = {}
    d['genome'] = dbkey
    d['historyId'] = history_id
    d['parameters'] = format_tool_parameters(tool_parameters)
    d['run'] = get_run_from_history_name(history_name)
    d['sample'] = get_sample_from_history_name(history_name)
    d['statsToolId'] = stats_tool_id
    d['toolCategory'] = tool_category
    d['toolStderr'] = stderr
    d['toolId'] = tool_id
    d['userEmail'] = user_email
    d['workflowId'] = get_workflow_id(config_file, history_name)
    d['workflowStepId'] = workflow_step_id
    return d


def get_chrom_lengths(chrom_len_file):
    # Determine the length of each chromosome
    # and add it to the chrom_lengths dictionary.
    chrom_lengths = dict()
    len_file = fileinput.FileInput(chrom_len_file)
    try:
        for line in len_file:
            fields = line.split("\t")
            chrom_lengths[fields[0]] = int(fields[1])
    except Exception as e:
        stop_err('Error reading chromosome length file:\n%s\nException:\n%s\n' % (chrom_len_file, str(e)))
    return chrom_lengths


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
        d['uri'] = '%s/datasets/%s/display?preview=False' % (defaults['GALAXY_BASE_URL'], i)
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


def get_genome_coverage(file_path, chrom_lengths_file):
    """
    Generate the genome coverage for the dataset located at file_path.
    """
    lines_in_input = float(get_number_of_lines(file_path))
    chrom_lengths = get_chrom_lengths(chrom_lengths_file)
    genome_size = float(get_genome_size(chrom_lengths))
    if genome_size == 0:
        # Use default.
        genome_size = float(MAX_GENOME_SIZE)
    genome_coverage = '%.4f' % float(lines_in_input / genome_size)
    return float(genome_coverage)


def get_genome_size(chrom_lengths_dict):
    genome_size = 0
    for k, v in chrom_lengths_dict.items():
        genome_size += v
    return genome_size


def get_motif_count(motif_logo_list):
    return len(motif_logo_list) // 2


def get_peak_stats(file_path):
    """
    The received file_path must point to a gff file and
    we'll return peak stats discovered in the dataset.
    """
    peak_stats = dict(numberOfPeaks=0,
                      peakMean=0,
                      peakMeanStd=0,
                      peakMedian=0,
                      peakMedianStd=0,
                      medianTagSingletons=0,
                      singletons=0)
    stddevs = []
    peak_singleton_scores = []
    scores = []
    singletons = 0
    i = 0
    with openfile(file_path, 'rt') as fh:
        for i, line in enumerate(fh):
            items = line.split('\t')
            # Gff column 6 is score.
            score = float(items[5])
            scores.append(score)
            # Gff column 9 is a semicolon-separated list.
            attributes = items[8].split(';')
            for attribute in attributes:
                if attribute.startswith('stddev'):
                    val = float(attribute.split('=')[1])
                    stddevs.append(val)
                    if val == 0.0:
                        # We have a peakSingleton.
                        singletons += 1
                        peak_singleton_scores.append(score)
                    break
    fh.close()
    if i > 0:
        # The number of lines in the file is the number of peaks.
        peak_stats['numberOfPeaks'] = i + 1
        peak_stats['peakMean'] = numpy.mean(scores)
        peak_stats['peakMeanStd'] = numpy.mean(stddevs)
        peak_stats['peakMedian'] = numpy.median(scores)
        peak_stats['peakMedianStd'] = numpy.median(stddevs)
        peak_stats['medianTagSingletons'] = numpy.median(peak_singleton_scores)
        peak_stats['singletons'] = singletons
    return peak_stats


def get_pegr_url(config_file):
    defaults = get_config_settings(config_file)
    return make_url(defaults['PEGR_API_KEY'], defaults['PEGR_URL'])


def get_pe_histogram_stats(file_path):
    pe_histogram_stats = dict(avgInsertSize=0,
                              medianInsertSize=0,
                              modeInsertSize=0,
                              stdDevInsertSize=0)
    avg_insert_size_set = False
    median_insert_size_set = False
    mode_insert_size_set = False
    std_dev_insert_size_set = False
    with open(file_path) as fh:
        for i, line in enumerate(fh):
            line = line.strip()
            if line.startswith('# Average Insert Size'):
                items = line.split(': ')
                pe_histogram_stats['avgInsertSize'] = float('%.4f' % float(items[1]))
                avg_insert_size_set = True
            elif line.startswith('# Median Insert Size'):
                items = line.split(': ')
                pe_histogram_stats['medianInsertSize'] = float('%.4f' % float(items[1]))
                median_insert_size_set = True
            elif line.startswith('# Mode Insert Size'):
                items = line.split(': ')
                pe_histogram_stats['modeInsertSize'] = float('%.4f' % float(items[1]))
                mode_insert_size_set = True
            elif line.startswith('# Std deviation of Insert Size'):
                items = line.split(': ')
                pe_histogram_stats['stdDevInsertSize'] = float('%.4f' % float(items[1]))
                std_dev_insert_size_set = True
            if avg_insert_size_set and median_insert_size_set and mode_insert_size_set and std_dev_insert_size_set:
                break
    fh.close()
    return pe_histogram_stats


def get_read_from_fastqc_file(file_path):
    read = 0
    with open(file_path) as fh:
        for i, line in enumerate(fh):
            if line.startswith('Filename'):
                if line.find('R1') > 0:
                    read = 1
                elif line.find('R2') > 0:
                    read = 2
                break
    fh.close()
    return read


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

def get_markdup_metrics(file_path):
    """
    Parse metrics output file from Picard's MarkDuplicates (Unused by paired_004 but retained for possible future use)
    """
    # Method: loop through file until encountering the key string (line with all the field names, second to last filename at time of this being written)
    with openfile(file_path, 'rt') as reader:
        key_str = []
        for line in reader:
            # key string defined (in last loop), this line is metrics values string
            if (len(key_str)>10):
                metrics = {}
                tokens = line.split('\t')
                # map key string values to metric values and return
                for i,k in enumerate(key_str):
                    metrics.update({k:tokens[i]})
                # may need to type the metrics here
                return(metrics)
            # key string encountered - split tokens and define
            elif (line.startswith('LIBRARY')):
                key_str = line.split('\t')
    # return default metrics values
    return({'LIBRARY':''})


def get_statistics(file_path, stats, **kwd):
    # ['dedupUniquelyMappedReads', 'mappedReads', 'totalReads', 'uniquelyMappedReads']
    s = {}
    try:
        for k in stats:
            if k == 'adapterDimerCount':
                # We're dealing with the FastQC report file,
                # so populate the statistics with the read.
                s['read'] = get_read_from_fastqc_file(file_path)
                s[k] = get_adapter_dimer_count(file_path)
            elif k == 'genomeCoverage':
                chrom_lengths_file = kwd.get('chrom_lengths_file', None)
                if chrom_lengths_file is None:
                    stop_err('Required chrom_lengths_file parameter not received!')
                s[k] = get_genome_coverage(file_path, chrom_lengths_file)
            elif k == 'motifCount':
                s[k] = get_motif_count(kwd.get('motif_logo_list', []))
            elif k == 'peakPairWis':
                s[k] = get_number_of_lines(file_path)
            elif k == 'peakStats':
                return get_peak_stats(file_path)
            elif k == 'peHistogram':
                return get_pe_histogram_stats(file_path)
            elif k == 'totalReadsFromBam':  # bwa output stats
                s['totalReads'] =                 get_reads("samtools view -c -f 0x40 -F 4 -q 5     %s" % file_path) # R1
                s['totalReadsR2'] =               get_reads("samtools view -c -f 0x80 -F 4 -q 5     %s" % file_path) # R2
            elif k == 'mappingStatsFromBamPaired':  # markdup output stats
                # R1
                s['uniquelyMappedReads'] =        get_reads("samtools view -c -f 0x40 -F 4          %s" % file_path)
                s['mappedReads'] =                get_reads("samtools view -c -f 0x40               %s" % file_path)
                s['dedupUniquelyMappedReads'] =   get_reads("samtools view -c -f 0x41 -F 0x404 -q 5 %s" % file_path)
                # R2
                s['uniquelyMappedReadsR2'] =      get_reads("samtools view -c -f 0x80 -F 4          %s" % file_path)
                s['mappedReadsR2'] =              get_reads("samtools view -c -f 0x80               %s" % file_path)
                s['dedupUniquelyMappedReadsR2'] = get_reads("samtools view -c -f 0x81 -F 0x404 -q 5 %s" % file_path)
            elif k == 'dedupUniquelyMappedReadsSingle':  # succeeded by mappingStatsFromBamSingle
                s['dedupUniquelyMappedReads'] = get_reads("samtools view -c -F 4 -q 5 %s" % file_path)
            elif k == 'dedupUniquelyMappedReads':  # succeeded by mappingStatsFromBamPaired
                s[k] = get_reads("samtools view -c -f 0x41 -F 0x404 -q 5 %s" % file_path)
            elif k == 'mappedReadsSingle':  # succeeded by mappingStatsFromBamSingle
                s['mappedReads'] = get_reads("samtools view -c -F 4 %s" % file_path)
            elif k == 'mappedReads':  # succeeded by mappingStatsFromBamPaired
                s[k] = get_reads("samtools view -c -f 0x40 -F 4 %s" % file_path)
            elif k == 'totalReadsSingle':  # succeeded by mappingStatsFromBamSingle
                s['totalReads'] = get_reads("samtools view -c %s" % file_path)
            elif k == 'totalReads':  # succeeded by mappingStatsFromBamPaired
                s[k] = get_reads("samtools view -c -f 0x40 %s" % file_path)
            elif k == 'uniquelyMappedReadsSingle':  # succeeded by mappingStatsFromBamSingle
                s['uniquelyMappedReads'] = get_reads("samtools view -c -F 4 -q 5 %s" % file_path)
            elif k == 'uniquelyMappedReads':  # succeeded by mappingStatsFromBamPaired
                s[k] = get_reads("samtools view -c -f 0x40 -F 4 -q 5 %s" % file_path)
            # elif k == 'getMetricsSingle':  # picard-style mapping statistics
            #     metrics = get_markdup_metrics(file_path)
            #     s['UNPAIRED_READS_EXAMINED'] = metrics['UNPAIRED_READS_EXAMINED']
            #     s['UNPAIRED_READ_DUPLICATES'] = metrics['UNPAIRED_READ_DUPLICATES']
            #     s['UNMAPPED_READS'] = metrics['UNMAPPED_READS']
            #     s['ESTIMATED_LIBRARY_SIZE'] = metrics['ESTIMATED_LIBRARY_SIZE']
            # elif k == 'getMetrics':
            #     metrics = get_markdup_metrics(file_path)
            #     s['READ_PAIRS_EXAMINED'] = metrics['READ_PAIRS_EXAMINED']
            #     s['READ_PAIR_DUPLICATES'] = metrics['READ_PAIR_DUPLICATES']
            #     s['UNMAPPED_READS'] = metrics['UNMAPPED_READS']
            #     s['ESTIMATED_LIBRARY_SIZE'] = metrics['ESTIMATED_LIBRARY_SIZE']

    except Exception as e:
        stop_err(str(e))
    return s


def get_tmp_filename(dir=None, suffix=None):
    fd, name = tempfile.mkstemp(suffix=suffix, dir=dir)
    os.close(fd)
    return name


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
