from address import Address
from quote import Quote
import webview
import os
import asyncio
import client_calls as call

class Api:
	def __init__(self):
		self.loop = asyncio.get_event_loop()
		self.profile = None
		self.error = None
		self.connected = False
	def login(self, username, password):
		if(not self.connected):
			self.loop.run_until_complete(call.connect())
			self.connected = True
		response = self.loop.run_until_complete(call.login(username, password))
		if(response == "Success"):
			self.profile = self.loop.run_until_complete(call.get_profile())
		return response
	def logout(self):
		self.loop.run_until_complete(call.logout())
		self.profile = None
		self.quotes = None
		self.error = None
		self.connected = False
	def register(self, username, password, confpassword, name, addr1, addr2, city, state, zip):
		if(not self.connected):
			self.loop.run_until_complete(call.connect())
			self.connected = True
		if(password!=confpassword):
			return "Error: password does not match confirmed password"
		response = self.loop.run_until_complete(call.register(username, password, name, Address(city, state, zip, addr1, addr2)))
		if(response == "Success"):
			self.profile = self.loop.run_until_complete(call.get_profile())
		return response
	def getquotefor(self, gallons, date):
		self.profile.quoteinprogress = Quote(int(gallons), date, self.profile.address)
		result = self.loop.run_until_complete(call.get_quote(gallons, date))
		if(isinstance(result, float)):
			self.profile.quoteinprogress.price = result
		return result
	def editprofile(self, name, addr1, addr2, city, state, zip, oldpassword, newpassword, confnewpassword):
		if(newpassword!=confnewpassword):
			return "Error: new password does not match confirmed new password"
		addr = Address(city, state, zip, addr1, addr2)
		changes = {}
		if(addr!=self.profile.address):
			changes["address"] = addr
		if(name!=profile.name):
			changes["name"] = name
		if(len(oldpassword)!=0):
			changes["oldpassword"] = oldpassword
		if(len(newpassword)!=0):
			changes["newpassword"] = newpassword
		if(len(changes.keys()) == 0):
			return "No changes made"
		response = self.loop.run_until_complete(call.update_profile(**changes))
		if(response == "Success"):
			self.profile = self.loop.run_until_complete(call.get_profile())
		return response
	def submitquote(self):
		return self.loop.run_until_complete(call.submit_quote())
	def getquotehistory(self):
		self.profile.quotes = self.loop.run_until_complete(call.get_quote_history())
		return self.profile.quotes
	def getprice(self):
		return self.quote.price
	def gettotal(self):
		return self.quote.total 
	def getname(self):
		if(self.profile is None):
			return None
		return self.profile.name
	def getusername(self):
		if(self.profile is None):
			return None
		return self.profile.username
	def getaddress1(self):
		if(self.profile is None):
			return None
		return self.profile.address.address1
	def getaddress2(self):
		if(self.profile is None):
			return None
		return self.profile.address.address2
	def getcity(self):
		if(self.profile is None):
			return None
		return self.profile.address.city
	def getstate(self):
		if(self.profile is None):
			return None
		return self.profile.address.state
	def getzipcode(self):
		if(self.profile is None):
			return None
		return self.profile.address.zipcode

def main():
	api = Api()
	window = webview.create_window("CS Project", url="login.html", js_api = api)
	window.closing += api.logout
	webview.start(debug=True)

if __name__ == "__main__":
    main()
