# This is generalized version of galaxy-PEGR API tools which is available at https://github.com/seqcode/cegr-galaxy.
# It has been tried that the API tool works with most of the galaxy tools.


#!/usr/bin/env python
import argparse
import galaxy_post_pegr_util



parser = argparse.ArgumentParser()
parser.add_argument('--config_file', dest='config_file', help='stats_config.ini')
parser.add_argument('--dbkey', dest='dbkey', help='Input dbkey')
parser.add_argument('--history_id', dest='history_id', help='History id')
parser.add_argument('--history_name', dest='history_name', help='History name')
parser.add_argument('--input', dest='input', help='Input dataset')
parser.add_argument('--input_datatype', dest='input_datatype', help='Input dataset datatype')
parser.add_argument('--input_id', dest='input_id', help='Encoded input dataset id')
parser.add_argument('--output', dest='output', help='Output dataset')
parser.add_argument('--stats_tool_id', dest='stats_tool_id', help='The caller of this script')
parser.add_argument('--stderr', dest='stderr', help='Job stderr')
parser.add_argument('--tool_id', dest='tool_id', help='Tool that was executed to produce the input dataset')
parser.add_argument('--tool_category', dest='tool_category', help='Tool category key for PEGR to parse')
parser.add_argument('--tool_parameters', dest='tool_parameters', help='Tool parameters that were set when producing the input dataset')
parser.add_argument('--workflow_step_id', dest='workflow_step_id', default=None, help='Workflow step id')
parser.add_argument('--user_email', dest='user_email', help='Current user email')
args = parser.parse_args()

# Initialize the payload.
payload = galaxy_post_pegr_util.get_base_json_dict(args.config_file, args.dbkey, args.history_id, args.history_name, args.stats_tool_id, args.stderr, args.tool_id, args.tool_category, args.tool_parameters, args.user_email, args.workflow_step_id)
# Generate the statistics and datasets.
payload['statistics'] = [{}] # [stats_util.get_statistics(args.input, STATS)]
payload['datasets'] = [galaxy_post_pegr_util.get_datasets(args.config_file, args.input_id, args.input_datatype)]
payload['history_url'] = galaxy_post_pegr_util.get_history_url(args.config_file, args.history_id)
# Send the payload to PEGR.
pegr_url = galaxy_post_pegr_util.get_pegr_url(args.config_file)
response = galaxy_post_pegr_util.submit(args.config_file, payload)
# Make sure all is well.
galaxy_post_pegr_util.check_response(pegr_url, payload, response)
# If all is well, store the results in the output.
galaxy_post_pegr_util.store_results(args.output, pegr_url, payload, response)
