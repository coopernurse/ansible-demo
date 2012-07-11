#!/usr/bin/env python

import os
import sys
import time
from boto.ec2.connection import EC2Connection

# change these as desired
#
# EC2 keypair to attach to instance on boot
KEY        = 'james-mac'
if os.environ.has_key('EC2_SSH_KEY'):
    KEY = os.environ['EC2_SSH_KEY']

# probably don't want to change these:
ROLE       = sys.argv[1]
ZONE       = 'us-east-1b'
SEC_GROUP  = ['default']
AMI        = 'ami-eafa5883'
INST_TYPE  = 'm1.small'
USER_DATA = """#!/bin/bash
set -e

# install basic OS packages
sleep 15
apt-get update
apt-get install -yf ntp git bzr mercurial curl build-essential
"""

#######################################################

# Create EC2 conn
print "Creating EC2 conn using env: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
print "Will boot instance using keypair (set: EC2_SSH_KEY to override): %s" % KEY
ec2 = EC2Connection(os.environ['AWS_ACCESS_KEY_ID'], 
                    os.environ['AWS_SECRET_ACCESS_KEY'])

# Describe instances
print "Looking for existing EC2 instance with role: %s" % ROLE
target_inst = None
for res in ec2.get_all_instances():
    for inst in res.instances:
        print "    id=%s tags=%s" % (inst.id, str(inst.tags))
        if inst.tags.has_key('role') and inst.tags['role'] == ROLE:
            if inst.state == 'terminated':
                print "Found terminated EC2 instance. id=%s" % inst.id
            else:
                print "Found existing EC2 instance: id=%s state=%s ip=%s" % (inst.id, inst.state, inst.ip_address)
                target_inst = inst

# Boot instance if not found
if not target_inst:
    print "Existing EC2 instance not found - booting"

    resp = ec2.run_instances(AMI, 
                             key_name=KEY, 
                             instance_type=INST_TYPE,
                             security_groups=SEC_GROUP, 
                             user_data=USER_DATA)
    inst = resp.instances[0]
    inst.add_tag("role", ROLE)

    # Poll until instance available
    print "Waiting for instance to become available"
    while True:
        instances = ec2.get_all_instances([inst.id])
        if instances and len(instances) > 0:
            if instances[0].instances[0].state=='running':
                target_inst = instances[0].instances[0]
                break
        else:
            time.sleep(5)

    print "Instance booted: id=%s ip_addr=%s" % (target_inst.id, target_inst.ip_address)



print "Done!"
