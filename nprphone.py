import os
import wsgiref.handlers
from xml.dom import minidom

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.api import urlfetch

BASE_URL = "http://nprphone.appspot.com/"
API_KEY="MDAzODIzNDM0MDEyNDkwOTUwNTViOTM4Zg001"
NPR_API_URL="http://api.npr.org/stations"

class ZipPage(webapp.RequestHandler):
	"""
	Accepts input digits from the caller, fetches the weather from an
	external site, and reads back the weather to the caller
	"""
	def get(self):
		self.post()
	
	def _error(self, msg, redirecturl=None):
		templatevalues = {
			'msg': msg,
			'redirecturl': redirecturl
		}
		xml_response(self, 'error.xml', templatevalues)
	
	
	
	
	def _fetch(self, zipcode):
		url = NPR_API_URL +"?zip=" +zipcode+"&apiKey="+API_KEY
		result = urlfetch.fetch(url)
		if result.status_code != 200:
			return None
		return result.content
	
	def _parse(self, xml):
		dom = minidom.parseString(xml)
		stations = dom.getElementsByTagName('station')
		x = 0
		stationlist = ""
		for node in stations:
			freq = node.getElementsByTagName('frequency')
			for f in freq:
				stationlist += f.childNodes[0].nodeValue+" </Say><Pause length=\"1\"/><Say voice=\"woman\">"
				x+=1
		stationlist += "Thank you."
		return {
			'stations': stationlist,
			'count':x
		}
		
		
		
		
	  # @start snippet
	def post(self):
		zipcode = self.request.get('Digits')
		if not zipcode:
			self._error("Invalid zip code.", BASE_URL)
			return
		
		 #strip off extra digits and keys from the Digits we got back
		zipcode = zipcode.replace('#', '').replace('*', '')[:5]
		
		#xml_response(self,'stations.xml')
		
		stationxml = self._fetch(zipcode)
		if not stationxml:
			self._error("Error fetching NPR listings. Good Bye.")
			return
		try:
			xml_response(self, 'stations.xml', self._parse(stationxml))
		except:
			self._error("There are no stations in your area. Sorry!")
		
		 #@end snippet

# @start snippet
def xml_response(handler, page, templatevalues=None):
	"""
	Renders an XML response using a provided template page and values
	"""
	path = os.path.join(os.path.dirname(__file__), page)
	handler.response.headers["Content-Type"] = "text/xml"
	handler.response.out.write(template.render(path, templatevalues))

class GatherPage(webapp.RequestHandler):
	"""
	Initial user greeting.	Plays the welcome audio file then reads the
	"enter zip code" message.  The Play and Say are wrapped in a Gather
	verb to collect the 5 digit zip code from the caller.  The Gather
	will post the results to /weather
	"""
	def get(self):
		self.post()
	
	def post(self):
		templatevalues = {
			'postprefix': BASE_URL,
		}
		xml_response(self, 'gather.xml', templatevalues)
# @end snippet

def main():
	# @start snippet
	application = webapp.WSGIApplication([ \
		('/', GatherPage),
		('/station', ZipPage)],
		debug=True)
	# @end snippet
	wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
	main()
