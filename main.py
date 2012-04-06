#!/usr/bin/python27
import sqlite3
import win32com.client

def insert(db, row):
	db.execute('insert into settings (i, ip, mask, gateway, dns1, dns2) values (?, ?, ?, ?, ?, ?)'\
			, (row['i'], row['ip'], row['mask'], row['gateway'], row['dns1'], row['dns2']))
	db.commit()

def retrieve(db, key):
	cursor = db.execute('select * from settings where i = ?', (key,))
	if cursor:
		for r in cursor:
			return (r['i'], r['ip'], r['mask'], r['gateway'], r['dns1'], r['dns2'])
	else:
		return -1

def update(db, row):
	db.execute('update settings set ip = ?, mask = ?, gateway = ?, dns1 = ?, dns2 = ? where i = ?',
		(row['ip'], row['mask'], row['gateway'], row['dns1'], row['dns2'], row['i']))
	db.commit()

def delete(db, key):
	db.execute('delete from settings where i = ?', (key,))
	db.commit()

def disp_rows(db):
	cursor = db.execute('select * from settings order by i')
	print '------------------------------------------------------------------------------'
	print('{}\t{}\t\t{}\t\t{}\t\t{}\t{}'.format('Id','IP','Mask','Gateway','DNS1','DNS2'))
	for row in cursor:
		print('{}\t{}\t{}\t{}\t{}\t{}'.\
			format(row['i'], row['ip'], row['mask'], row['gateway'], row['dns1'], row['dns2']))
	print '------------------------------------------------------------------------------'

def d(db):	
	while True:
		id = raw_input('enter id of profile to delete: ')
		try:
			iOld,ipOld,maskOld,gatewayOld,dns1Old,dns2Old = retrieve(db, id)
		except:
			print 'error: wrong id!'
		else:
			delete(db, id)
			break
			
def u(db):
	while True:
		id = raw_input('enter id of profile to edit: ')
		try:
			iOld,ipOld,maskOld,gatewayOld,dns1Old,dns2Old = retrieve(db, id)
		except:
			print 'error: wrong id!'
		else:
			while True:
				ip = raw_input('enter new IP: ')
				if ip == '': 
					ip = ipOld
					break
				else:
					if validate(ip) != 0: break
			while True:
				mask = raw_input('enter new Mask: ')
				if mask == '': 
					mask = maskOld
					break
				else: 
					if validate(mask, isMask = True) != 0: break
			while True:
				gateway = raw_input('enter new Gateway: ')
				if gateway == '': 
					gateway = gatewayOld
					break
				else:
					if validate(gateway) != 0: break
			while True:
				dns1 = raw_input('enter new DNS1: ')
				if dns1 == '': 
					dns1 = dns1Old
					break
				else:
					if validate(dns1) != 0: break
			while True:
				dns2 = raw_input('enter new DNS2: ')
				if dns2 == '': 
					dns2 = dns2Old
					break
				else:
					if validate(dns2) != 0: break
			update(db, dict(i = id, ip = ip, mask = mask, gateway = gateway, dns1 = dns1, dns2 = dns2))
			break
			
def a(db):
	while True:
		id = raw_input('enter id of new profile: ')
		try:
			iOld,ipOld,maskOld,gatewayOld,dns1Old,dns2Old = retrieve(db, id)
			print 'error: id already exists!'
		except:
			while True:
				ip = raw_input('enter new IP: ')
				if validate(ip) != 0: break
			while True:
				mask = raw_input('enter new Mask: ')
				if validate(mask, isMask = True) !=0: break
			while True:
				gateway = raw_input('enter new Gateway: ')
				if validate(gateway) != 0: break
			while True:
				dns1 = raw_input('enter new DNS1: ')
				if validate(dns1) != 0: break
			while True:
				dns2 = raw_input('enter new DNS2: ')
				if validate(dns2) != 0: break
			insert(db, dict(i = id, ip = ip, mask = mask, gateway = gateway, dns1 = dns1, dns2 = dns2))
			break
			
def validate(str, isMask = False):
	set = str.split('.')
	if len(set) != 4:
		print 'error: wrong elements number!'
		return 0
	for el in set:	
		if el == '':
			print 'error: missing element!'
			return 0
		if int(el) > 255 or int(el) < 0:
			print 'error: wrong binding of element {}!'.format(el)
			return 0
	if isMask == False:
		if int(set[0]) == 0 or int(set[3]) == 0:
			print 'error: first or last element is equal to zero!'
			return 0
			
	# validating mask
	else:
		str = ''
		for el in set:
			str += make8bits(el)
			
		error = 0
		pos = -1
		c = 0
		for i in range(32):
			if str[i] == '0':
				if c == 0 :
					pos = i
				c = pos
				while c < 32:
					if str[c] == '1':
						error = 1
					c = c + 1
		if error == 1:
			print 'error: wrong mask format!'
			return 0
		else:
			return pos	
			
# input - raw result after unpack
# output - str with '0' added in front if needed to make 8 bits long
def make8bits(string_val):
	string_val = str(bin(int(string_val)))
	string_val = string_val[2:]
	while len(string_val) < 8:
		string_val = '0' + string_val
	if len(string_val) > 8:
		string_val = string_val[:8]
	return string_val			
	
def s(db):
	while True:
		id = raw_input('enter id of profile to set: ')
		try:
			iOld,ipOld,maskOld,gatewayOld,dns1Old,dns2Old = retrieve(db, id)	
			break
		except:
			print 'error: wrong id!'

	import wmi

	# Obtain network adaptors configurations
	nic_configs = wmi.WMI().Win32_NetworkAdapterConfiguration(IPEnabled=True)

	# First network adaptor
	nic = nic_configs[0]

	# IP address, subnetmask and gateway values should be unicode objects
	ip = unicode(ipOld)
	subnetmask = unicode(maskOld)
	gateway = unicode(gatewayOld)
	dns1 = unicode(dns1Old)
	dns2 = unicode(dns2Old)

	# Set IP address, subnetmask and default gateway
	# Note: EnableStatic() and SetGateways() methods require *lists* of values to be passed
	nic.EnableStatic(IPAddress=[ip],SubnetMask=[subnetmask])
	nic.SetGateways(DefaultIPGateway=[gateway])
	
	# Sets DNS
	nic.SetDNSServerSearchOrder(DNSServerSearchOrder=[dns1, dns2])
		
	
def g():
	import wmi
	c = wmi.WMI ()
	
	#If true, local lookup files are used. Lookup files will contain mappings of IP addresses to host names
	c.Win32_NetworkAdapterConfiguration.EnableWINS(WINSEnableLMHostsLookup = False)
	
	#for mask
	objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
	objSWbemServices = objWMIService.ConnectServer(".", "root\cimv2")
	for objItem in objSWbemServices.ExecQuery("SELECT * FROM Win32_NetworkAdapterConfiguration"):
		strList = " "
		try :
			Mask = objItem.IPSubnet[0]
		except:
			pass
	
	#output data
	for interface in c.Win32_NetworkAdapterConfiguration(IPenabled = 1):
		print '	Current settings are:'
		print "Adapter: ",interface.caption
		print "MAC-Address:	",interface.MACAddress
		print "IP:		",interface.IPAddress[0]
		print "Mask:		",Mask
		if interface.DefaultIPGateway[0]:
			print "Gateway:	",interface.DefaultIPGateway[0]
		cntr = 1
		for i in interface.DNSServerSearchOrder:
			print "DNS{}:		{}".format(cntr, i)
			cntr += 1
			
def m():
	import wmi

	# Obtain network adaptors configurations
	nic_configs = wmi.WMI().Win32_NetworkAdapterConfiguration(IPEnabled=True)

	# First network adaptor
	nic = nic_configs[0]

	# Enable DHCP
	nic.EnableDHCP()
	
	# Enable DNS
	nic.EnableDNS()
	
def main():
	db = sqlite3.connect('settings.db')
	db.row_factory = sqlite3.Row
    #print('Create table settings')
	#db.execute('drop table if exists settings')
	#db.execute('create table settings ( i text, ip text, mask text, gateway text, dns1 text, dns2 text )')
	message = None
	while message != 'e':
		disp_rows(db)
		print """[d - delete] [u - update] [a - add new] [s - set] [g - get] [e - exit]"""#\n
#[m - obtaining an IP address (via DHCP) and DNS automatically]"""
		
		message = raw_input()
		if message == 'd':
			d(db)
		elif message == 'u':
			u(db)
		elif message == 'a':
			a(db)
		elif message == 's':
			s(db)
		elif message == 'g':
			g()
		elif message == 'm':
			m()
		
if __name__ == "__main__": main()
