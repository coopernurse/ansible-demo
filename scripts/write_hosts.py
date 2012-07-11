#!/usr/bin/env python

import os
import sys
from boto.ec2.connection import EC2Connection

print "Using env vars: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
ec2 = EC2Connection(os.environ['AWS_ACCESS_KEY_ID'], 
                    os.environ['AWS_SECRET_ACCESS_KEY'])

roles = { }
fname = "hosts"
if len(sys.argv) > 1:
    fname = sys.argv[1]

print "Writing file: %s" % fname

for res in ec2.get_all_instances():
    for inst in res.instances:
        if inst.tags.has_key('role'):
            role = inst.tags['role']
            if inst.state != 'terminated':
                params = (role, inst.id, inst.state, inst.ip_address)
                print "  Found EC2 instance: role=%s id=%s state=%s ip=%s" % params
                if not roles.has_key(role):
                    roles[role] = []
                roles[role].append(inst.ip_address)

f = open(fname, "w")
for k, v in roles.items():
    f.write("\n[%s]\n" % k)
    for ip in v:
        f.write("%s\n" % ip)
f.close()

print "Done"
