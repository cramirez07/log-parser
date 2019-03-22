# Log Parser
A simple web server log file parser in python.
* Command-line driven using both long and short option flags (eg: -v vs –verbose).
* Accept a glob file expression for file names to parse. These exist on the local filesystem.
* Supports a -v/--verbose option to log progress/status to stdout.
* Outputs a report in a text or, if a --json flag is used, json.
* List of API paths sorted by frequency with percentage
* Creates output text/json file.
  
## Usage: 
~~~
    log-parse.py [-h] FILE [-v|--verbose] [-d|--debug] [--json]
    
    File                glob file expression for file names to parse
    [-v|--verbose]      Prints progress to screen
    [-d|--debug]        Log debug prints to file(debug.log)
    [--json]            Flag to output into json format
~~~
## Output:
~~~
    ./log-parse.py  /var/log/apache/2019-01-0*
    
    time_range: 2019-01-02_06:00:00 – 2019-01-03_14:00:00
    total_requests: 4000
    api_by_frequency:
        /api/most_common: 30%
        /api/less common: 20%  
~~~
### Requirements:
Since this is a straightforward script that works on Python 2.7 and above, without any 3rd-party libraries, you can just use it as a normal python script.  

Apache common log format: https://httpd.apache.org/docs/1.3/logs.html
Pathname style pattern :https://docs.python.org/3/library/glob.html
