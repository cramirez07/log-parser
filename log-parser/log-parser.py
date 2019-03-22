from datetime import datetime
import argparse
import glob
import re
import json
import logging
LOG = logging.getLogger(__name__)

HOST = r'^(?P<host>.*?)'
SPACE = r'\s'
IDENTITY = r'\S+'
USER = r'\S+'
TIME = r'(?P<time>\[.*?\])'
REQUEST = r'\"(?P<request>.*?)\"'
STATUS = r'(?P<status>\d{3})'
SIZE = r'(?P<size>\S+)'

REGEX = HOST+SPACE+IDENTITY+SPACE+USER+SPACE+TIME+SPACE+\
        REQUEST+SPACE+STATUS+SPACE+SIZE+SPACE
        
class WebServerLogParser():
    def __init__(self, log_files, json_flag):
        self.log_files = log_files
        self.log_data = []
        self.output = {}
        
        self.parse_logs()
        self._generate_output()
        LOG.info("Generating Output:\n")
        if json_flag:
            self.generate_json_output()
        else:
            self.generate_text_output()
    
    def __str__(self):
        return str(self.output)
    
    def _generate_output(self):
        self.output['time_range'] = self._get_time_range()
        self.output['total_requests']= self._get_total_request()
        self.output['api_by_frequency'] = [self._compute_api_frequency()]

    def _get_time_range(self):
        time_stamps = []
        for item in self.log_data:
            time_stamps.append(item[0])
        result = '{} - {}'.format(min(time_stamps), max(time_stamps))
        return result
    
    def _compute_api_frequency(self):
        LOG.info("Computing Frequency")
        result = {}
        for item in self.log_data:
            if '/api/' in item[1][:5]:
                url = item[1]
                if url in result:
                    result[url] = result[url] + 1
                else:
                    result[url] = 1
        total_request = self._get_total_request()
        for item in result:
            LOG.debug("{}: {}/{}".format(item, result[item], total_request))
            result[item] = (float(result[item]) / float(total_request))
            
        sorted_result = {k: v for k, v in sorted(result.items(), key=lambda x: x[1], reverse=True)}
        for i in sorted_result:
            sorted_result[i] = "{0:.0%}".format((sorted_result[i]))
        return sorted_result
        
    def _format_time(self, time):
        INPUT_FORMAT = '%d/%b/%Y:%H:%M:%S'
        OUTPUT_FORMAT = '%Y-%m-%d_%H:%M:%S'
        result = datetime.strptime(time[1:].split()[0], INPUT_FORMAT).strftime(OUTPUT_FORMAT)
        return result
        
    def _get_request_path(self, request):
        try:
            result = request.split()[1].split('?')[0]
        except Exception:
            LOG.debug("Unable to parse request path")
            return None
        return result
    
    def _filter(self, line):
        match = re.search(REGEX,line)
        if match:
            LOG.debug("Parsing: %s", line[:-1])
            time_stamp = self._format_time(match.group('time'))
            request = self._get_request_path(match.group('request'))
            LOG.debug("time_stamp: %s; request: %s", time_stamp, request)
            self.log_data.append((time_stamp, request))
        
        
    def parse_logs(self):
        for filename in glob.glob(self.log_files):
            LOG.info("Parsing %s", filename)
            with open(filename, 'r') as f:
                for line in f:
                    self._filter(line)
        if not self.log_data:
            exit("Empty log or file not found!")
    
    def _get_total_request(self):
        return len(self.log_data)
    
    def generate_text_output(self):
        output = self.output
        result = '{}: {}\n'.format('time_range', output['time_range'])
        result += '{}: {}\n'.format('total_requests', output['total_requests'])
        result += '{}:\n'.format('api_by_frequency')
        api_frequencies = output['api_by_frequency']
        for api in api_frequencies:
            for k, v in api.items():
                result += '\t{}: {}\n'.format(k, v)
        print(result)
        with open('output.txt', 'w') as outfile:
            outfile.write(result)
            
    def generate_json_output(self):
        result = self.output
        print(result)
        with open('output.json', 'w') as outfile:
            json.dump(result, outfile)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'File', metavar='F', type=str,
        help='glob file expression for file names to parse')
    parser.add_argument(
        '-d', '--debug',
        help="Prints debugging statements",
        action="store_const", dest="loglevel", const=logging.DEBUG,
    )
    parser.add_argument(
        '-v', '--verbose',
        help="Prints information messages",
        action="store_const", dest="loglevel", const=logging.INFO,
    )
    parser.add_argument(
        '-j', '--json',
        help="Json flag",
        action="store_true", dest="json_flag",
    )
    return parser.parse_args()
    
if __name__ == "__main__":
    args = parse_arguments()

    if args.loglevel == logging.DEBUG:
        logging.basicConfig(filename='debug.log', filemode='w', level=args.loglevel)
    else:
        logging.basicConfig(level=args.loglevel, format='%(asctime)s: %(message)s')
    
    LOG.info("Web Server Log Parser")
    WebServerLogParser(args.File, args.json_flag)
    LOG.info("\nDone!")