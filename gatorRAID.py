#!/usr/bin/env python3
##Welcome to gatorRAID
##This script will show, delete and create raids on Dell Servers using racadm

#                        .--.  .--.
#                       /    \/    \
#                      | .-.  .-.   \
#                      |/_  |/_  |   \
#                      || `\|| `\|    `----.
#                      |\0_/ \0_/    --,    \_
#    .--"""""-.       /              (` \     `-.
#   /          \-----'-.              \          \
#   \  () ()                         /`\          \
#   |                         .___.-'   |          \
#   \                        /` \|      /           ;
#    `-.___             ___.' .-.`.---.|             \
#       \| ``-..___,.-'`\| / /   /     |              `\
#        `      \|      ,`/ /   /   ,  /
#                `      |\ /   /    |\/
#                 ,   .'`-;   '     \/
#            ,    |\-'  .'   ,   .-'`
#          .-|\--;`` .-'     |\.'
#         ( `"'-.|\ (___,.--'`'
#          `-.    `"`          _.--'
#             `.          _.-'`-.
#               `''---''``  jgs  `.

import subprocess
import re
import logging
import time
import argparse



def _run_cmd(cmd): #this will log the output of bash command that runs so you can manipulate the output.
    logging.debug(cmd)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    o, e = proc.communicate()
    logging.info('code: ' + str(proc.returncode))
    logging.info('Output: ' + o.decode('ascii'))
    logging.info('Error: '  + e.decode('ascii'))
    return o.decode('ascii'), e.decode('ascii')
def reboot_node(ipaddress):
  _run_cmd('racadm --nocertwarn -r {} -u [username] -p [password] serveraction powercycle'.format(ipaddress))
  print("the server was rebooted")
def schedule_config_now(ipaddress):
  scheduleconfigjob,  Err = _run_cmd('racadm --nocertwarn -r {} -u [username] -p [password] jobqueue create RAID.Integrated.1-1 --realtime'.format(ipaddress))
  logging.debug(scheduleconfigjob)
  if not Err:
    print (Err)

  nopending = re.search(r'there are no pending Configuration changes', scheduleconfigjob)
  jidnum = re.findall(r'JID_[0-9]{12}', scheduleconfigjob)
  if nopending: 
    print("there are no pending Configuration changes")
  else:
    print (jidnum)
    print("job in progress please wait 90 seconds")
    time.sleep(90)
    while True:
      jidcheck,  Err = _run_cmd('racadm --nocertwarn -r {} -u [username] -p [password] jobqueue view -i {}'.format(ipaddress, jidnum[0]))
      jobinprogress = re.search('Job in progress', jidcheck)
      jobcomplete = re.search('Job completed successfully', jidcheck)
      if jobinprogress:
        print("job still in progress, waiting 10 seconds")
        time.sleep(10)
      elif jobcomplete:
        print ("Job Completed SuCcEsSfUlLy")
        break
      else:
        print("The JID number wasn't found. The job might have been completed before the code got to here.")
        break

def delete_raid(ipaddress, deletelevel):
  listvdisks, Err = _run_cmd('racadm --nocertwarn -r {} -u [username] -p [password] raid get vdisks -o -p Layout,Size'.format(ipaddress))
  if not Err:
    print (Err)
  line_output1 = listvdisks.replace("\n ",'')
  logging.debug (line_output1)
  line_output2 = re.sub(" +", ' ', line_output1)
  logging.debug(line_output2)
  vdisks = re.findall(r'Disk\.Virtual\.[0-3]:RAID.Integrated.1-1.Layout = Raid-[0-6] Size = [0-9]+.[0-9]+ GB', line_output2)
  logging.debug(vdisks)
  drl = "Raid-{}".format(deletelevel)
  logging.debug(drl)
   #RAID to delete is defined by arg parse "-d "
  raidmatch = re.compile('.*({}).*'.format(drl))
  for disk in vdisks:
      if raidmatch.match(disk):
        vdisknum = re.findall(r'Disk\.Virtual\.[0-3]', disk)
        logging.debug("you made it this far")
        logging.debug(disk)
        logging.debug(vdisknum)
        logging.debug(nodename,"has a ip of", ipaddress, "and")
        logging.debug(vdisknum[0]," has a Raid of Zero") #[0] gets first item out of array
        _run_cmd('racadm --nocertwarn -r {} -u [username] -p [password] raid deletevd:{}:RAID.Integrated.1-1'.format(ipaddress,vdisknum[0]))# deletevd:Disk.Virtual.0")#delete old raid
        print("deleting the virtual disk that has a raid {}".format(deletelevel))
        schedule_config_now(ipaddress)
      else:
        logging.debug("There are no disks to delete in this specific vdisk array. Most Dells have multiple arrays or vdisks")
def p_disks(ipaddress): #This will list the physical disks and their state. Ready means that it can be added to a raid.
  print("Getting information on physical disks of {}".format(nodename))
  getpdisks,  Err = _run_cmd('racadm --nocertwarn -r {} -u [username] -p [password] raid get pdisks -o -p State,Size,MediaType'.format(ipaddress))
  print (getpdisks)
  if not Err:
    print (Err)
  print("Getting information on virtual disks of {}".format(nodename))
  listvdisks, Err = _run_cmd('racadm --nocertwarn -r {} -u [username] -p [password] raid get vdisks -o -p Layout,Size'.format(ipaddress))
  if not Err:
    print (Err)
  print(listvdisks)
#  line_output1 = listvdisks.replace("\n ",'')
#  logging.debug (line_output1)
#  line_output2 = re.sub(" +", ' ', line_output1)
#  logging.debug(line_output2)

#  getphysicaldisks = (getpdisks.replace("\n ",''))
#  #print (getpdisks.replace("\n ",''))
#  diskmatch = re.compile(
#      'Disk.*Ready'
#    )
#  for disk in getphysicaldisks.split("\n"):
#      if diskmatch.match(disk):
#        pdisksnum = re.findall(r'Disk\.Bay\.[0-9]+', disk)
#        logging.debug (pdisksnum[0])
def create_vdisk(ipaddress, raidlevel):
  getpdisks,  Err = _run_cmd('racadm --nocertwarn -r {} -u [username] -p [password] raid get pdisks -o -p state'.format(ipaddress))
  if not Err:
    print (Err)
  getphysicaldisks = (getpdisks.replace("\n ",''))
  logging.debug(getpdisks.replace("\n ",''))
  diskmatch = re.compile(
      'Disk.*Ready'
    )
  pdisklist = []
  for disk in getphysicaldisks.split("\n"):
      if diskmatch.search(disk):
        pdisksnum = re.findall(r'Disk\.Bay\.[0-9]+:Enclosure\.Internal\.0-1:RAID\.Integrated\.1-1', disk)
        pdisklist.append(pdisksnum[0])
        logging.debug (pdisksnum[0])
  parameter = ",".join(pdisklist)
  logging.debug(pdisklist)
  logging.debug(parameter)
  create_raid,  Err = _run_cmd('racadm --nocertwarn -r {} -u [username] -p [password] storage createvd:RAID.Integrated.1-1 -rl r{} -wp wb -rp ara -ss 512k -pdkey:{}'.format(ipaddress, raidlevel, parameter))
  if not Err:
    print (Err)
  print(create_raid)
  schedule_config_now(ipaddress)




if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Manages RAID Level on DELL servers with RACADM')
  parser.add_argument('nodes', type=str, help='last ip octet for drac controller in a comma separated list')
  parser.add_argument('-c', type=str, help='specify RAID level ie. -c 5 to take ready disks and create a RAID 5')
  parser.add_argument('-d', type=str, help='delete RAID level ie. -d 5 to remove ALL disks with a RAID level 5 and make the disks go to a ready state.')
  parser.add_argument('--info', action="store_true", help='gets info on raid setup')
#  clihelper.argparse_add_verbose_logging(parser)
  args = parser.parse_args()
#  clihelper.argparse_set_level(args,logging.getLogger())

  for node in args.nodes.split(','):
    nodename = "[nodename]" + str(node)
    nodenum = int(node) + 1
    ipaddress = "0.0.0." + str(nodenum)
    print (ipaddress)

    raidlevel = args.c
    deletelevel = args.d
    informat = args.info
    logging.debug("raidlevel is {}".format(raidlevel))
    if deletelevel:
      delete_raid(ipaddress, deletelevel)
    if raidlevel:
      create_vdisk(ipaddress, raidlevel)
    if informat:
      p_disks(ipaddress)


#:) Written by David Peterson 
