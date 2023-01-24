# taketwotest

The below URLs produce the following effects:

curl [dockerContainer]/stats								
/stats
											{
												"unique_count" : XX,
												"map" : [ { $IP: $REQUEST_COUNT, $IP: $REQUEST_COUNT, etc } ],
												"statuscodes" : [ { $CODE : $COUNT, $CODE: $COUNT, etc } ],
												"top_five" : [$MostReferrer, $SecondMostReferrer .. $FifthMostReferrer]
											}
/stats/unique_count 				Returns only the number of unique IPs
/stats/map 							Returns every unique IP along with its number of hits
/stats/statuscodes				Returns the HTTP Status Code distribution
/stats/top_five					Returns the top five referer URLs. (Note: Does not sort.)
/stats/filename					Returns the filename of the log file being analyzed
/stats/help		 					This documentation

Use the Dockerfile to build the container image. 
From there, be sure to specify the ports and volume to map (e.g., `docker run -p 8000:8000 -v /Users/mshea/works/git/taketwotest/logdir:/mnt [container name]`)

A parameter may be sent to the `docker run` command. If it is not sent, the script will default to using the file `access_log_20190520-125058.log`, located in the `logdir` directory

(A second copy of that file, alternately named `access_log_20190520-125055.log`, is also in the logdir directory, to demonstrate that either using a parameter or not using one will work.)

If the docker run command references a file that doesn't exist, the script will stop, albeit not as gracefully as I'd like.
