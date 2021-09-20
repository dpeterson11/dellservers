# dellservers
Welcome to gatorRAID
This script will show, delete and create raids on Dell Servers using racadm

You will need to replace [username] and [password] with the racadm username and password for your system.
Add the base IP address for your system as well 192.168.0. The last octet is left empty to iterate through a range if you have multiple servers.
You can also manage by nodename. ie, myawesomeserver

The command line takes serveral arguments

'nodes' will specify which nodes you intend to run these commands on. This is the last ip address number in the set. ie. 10.0.0.1, 10.0.0.2, 10.0.0.3 would be -nodes 1,2,3
'c' will specify the Raid level. ie. -c 5
'd' and the raid number will delete a raid and put disks in ready state ie. -d 5 
'--info' will pull information on raid setup.