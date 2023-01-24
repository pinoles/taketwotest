#!/usr/bin/env python3

from flask import Flask, request, jsonify
import ipaddress
import json
import re
import sys
## import time

##############################################################################################
## This is hard-coded b/c the assumption is that the container is reading from a mounted drive
## Thus the directory name will always be the same from the container's point of view (/mnt)
##############################################################################################
DIRECTORY = '/mnt'

## Keep json-generation tidy
def wrapJSON(text):
	return " { " + text + " } "

## Keep list-generation tidy
def wrapList(text):
	return " [ " + text + " ] "

## For mapping purposes
def ipToStr(ip):
	return ip.compressed

################################################
### LogAnalysis and Output Class and Methods ###
################################################

class logAnalysisObject:
	def __init__(self, file_name):
		self.file_name = DIRECTORY + '/' + file_name
		self.ip_count = {}
		self.status_count = {}
		self.referer = {}

		self.ip_count = {}
		self.line_count = 0

		self.logfile_regexp = \
			'([(\d\.)]+) ([^\s]) ([^\s]) \[(.*?)\] "(.*?)" (\d+) (\d+) "(.*?)" "(.*?)"'

	def analyzeLogs(self):
		try:
			file_object = open(self.file_name)
		except Exception as e:
			errorJson = (' { "Error": "' + str(e) + '" }')
			print (errorJson)
			return errorJson

		for line in file_object:
			temp_cip = {}
			temp_cip[1] = []
			found = False

			## Import the line; 
			## use regexp to separate the line into individual vars
			self.line_count += 1
			(ipstr, blank, username, timestamp, uri, 
				status_code, bytelen, referer, user_agent) = \
					re.match(self.logfile_regexp, line).groups()

			ip = ipaddress.ip_address(ipstr)
			
			## Populate the status code hash and the IP count hash:
			self.status_count[status_code] = \
				self.status_count.setdefault(status_code, 0) + 1
			self.ip_count[ip] = \
				self.ip_count.setdefault(ip, 0) + 1

			#######################################################################
			## If the request is a GET, then log the referer (we only need a count)
			## print ("URI Split is the following:")
			## print (uri.split())
			#######################################################################
			if uri.split()[0] == 'GET':
				## jself.referer.setdefault(referer, 0) + 1
				self.referer[referer] = \
					self.referer.setdefault(referer, 0) + 1

		file_object.close()

	def printFileNameJSON(self):
		return '{ "Log File Name": "' + str(self.file_name) + '" }'

	def printRefererJSON(self):
		r_list = []
		refererList = '"Referer Top Five": '
		sortedReferers = sorted(self.referer.items(), key=lambda item: item[1], reverse=True)
		for pair in range (0, 5):
			r_list.append('{ "' + str(sortedReferers[pair][0]) + '": ' + str(sortedReferers[pair][1]) + ' }')
		refererList += wrapList(', '.join(r_list))
		return refererList

	def printStatusCodeJSON(self):
		sc_list = []
		sc = '"Status Code Count": '
		for code, count in sorted(self.status_count.items()):
			sc_list.append('{ "' + str(code) + '": ' + str(count) + ' }')
		sc += wrapList(', '.join(sc_list))
		return sc

	def printUniqueIPCountJSON(self):
		return '"Unique IP Count": ' + str(len(self.ip_count.keys()))

	def printUniqueIPsJSON(self):
		uips_list = []
		uips = '"Unique IPs": '
		for ip, count in sorted(self.ip_count.items()):
			uips_list.append('{ "' + ip.compressed + '": ' + str(count) + ' }')
		uips += wrapList(', '.join(uips_list))
		return uips

	def printAnalysisJSON(self):
		ipcount_json = self.printUniqueIPCountJSON()
		uniqueips_json = self.printUniqueIPsJSON()
		statusCodeDistribution = self.printStatusCodeJSON()
		topFiveReferers = self.printRefererJSON()

		json_list = [ipcount_json, uniqueips_json, statusCodeDistribution, topFiveReferers ]
		analysis = ", ".join(json_list)
		return wrapJSON(analysis)

### API ###

app = Flask(__name__)

### /stats and all sub-URIs return API versions ###

@app.route("/stats")
def statsOverview():
	json_out = log_analysis_object.printAnalysisJSON() 
	return json_out 

@app.route("/stats/help")
def statsDocumentation():
	## Documentation
	api_documentation = ' { [ \
		{ "stats": "Returns results of all functions (unique_count, map, statuscodes, top_five)" }, \
		{ "stats/help": " - This documentation" }, \
      { "stats/filename": "Returns the filename of the log file being analyzed" }, \
		{ "stats/statuscodes": " - Returns the HTTP Status Code distribution" }, \
		{ "stats/unique_count": " - Returns only the number of unique IPs (public and private)" }, \
		{ "stats/map": " - Returns every unique IP (public and private) along with its number of hits" }, \
		{ "stats/referers": "Returns the top five referrers for GET requests" } , \
		] } ' + "\n"
	return api_documentation

@app.route("/stats/filename")
def statsFilename():
	json_out = log_analysis_object.printFileNameJSON()
	return json_out

@app.route("/stats/statuscodes")
def statsStatusCodes():
	json_out = log_analysis_object.printStatusCodeJSON() 
	return wrapJSON(json_out)

@app.route("/stats/unique_count")
def statsUniqueCount():
	json_out = log_analysis_object.printUniqueIPCountJSON()
	return wrapJSON(json_out)

@app.route("/stats/map")
def statsUniqueIPs():
	json_out = log_analysis_object.printUniqueIPsJSON()
	return wrapJSON(json_out)

@app.route("/stats/referers")
def statsTopFiveReferers():
	json_out = log_analysis_object.printRefererJSON()	
	return wrapJSON(json_out)

## Main ##

if __name__ == "__main__":
	###############################################################################################
	## I'd prefer to make this happen in the Dockerfile/docker-compose section. (Time constraints.)
	###############################################################################################
	if len(sys.argv) == 1:
		file_name = "access_log_20190520-125058.log"
	else:
		file_name = sys.argv[1]

	log_analysis_object = logAnalysisObject(file_name)
	logAnalysis = log_analysis_object.analyzeLogs()

	##########################################
	## Need a better way of handling this case
	##########################################
	if logAnalysis is not None:
		print ("Problem with the file")
		## time.sleep(100)
		## sys.exit("There was a problem with ingesting the log file.")

	app.run(host='0.0.0.0', port=8000, debug=False)
