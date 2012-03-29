'''
Created on Jun 1, 2011

@author: peymankazemian
'''

import re
from math import pow
from headerspace.hs import byte_array_get_bit, byte_array_set_bit, byte_array_to_hs_string
    
def is_ip_address(str):
    ips = re.match('(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})', str)
    if ips == None:
        return False
    else:
        return True
    
def is_ip_subnet(str):
    ips = re.match('(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})/(?:[\d]{1,2})', str)
    if ips == None:
        return False
    else:
        return True
    
def int_to_dotted_ip( intip ):
        octet = ''
        for exp in [3,2,1,0]:
            octet = octet + str(intip / ( 256 ** exp )) + "."
            intip = intip % ( 256 ** exp )
        return(octet.rstrip('.'))
 
def dotted_ip_to_int( dotted_ip ):
        exp = 3
        intip = 0
        for quad in dotted_ip.split('.'):
            intip = intip + (int(quad) * (256 ** exp))
            exp = exp - 1
        return(intip)
    
def dotted_subnet_to_int( dotted_subnet ):
        exp = 3
        intip = 0
        subnet = 32
        parts = dotted_subnet.split('/')
        if len(parts) > 1:
            try:
                subnet = int(parts[1])
            except Exception:
                pass
        dotted_ip = parts[0]
        for quad in dotted_ip.split('.'):
            intip = intip + (int(quad) * (256 ** exp))
            exp = exp - 1
        return([intip,subnet])
    
def range_to_wildcard(r_s,r_e,length):
    vals = r_s
    vale = r_e
    match = []
    while (vals <= vale):
        for i in range(1,length+2):
            if not ((vals | (2**i - 1 )) <= vale and (vals % 2**i)==0) :
                match.append((vals,i-1))
                vals = (vals| (2**(i-1) - 1 )) + 1
                break
    return match
    
def find_num_mask_bits_right_mak(mask):
    count = 0
    while (True):
        if (mask & 1 == 1):
            mask = mask >> 1
            count += 1
        else:
            break
    return count

def find_num_mask_bits_left_mak(mask):
    count = 0
    while (True):
        if (mask & 1 == 0):
            mask = mask >> 1
            count += 1
        else:
            break
    return 32-count
    
class node(object):
    def __init__(self):
        self.zero = None;
        self.one = None;
        self.ips = []
        self.action = None;
        
    def printSelf(self, indent):
        ind = ""
        for i in range(indent):
            ind = ind + "\t";
        str_ip = "%sIPs: "%ind
        for i in self.ips:
            str_ip = str_ip + int_to_dotted_ip(i[0]) + "/%d"%i[1] + ", "
        print str_ip
        print "%sAction: %s"%(ind,self.action)
        if self.zero != None:
            print "%sZero:"%(ind)
            self.zero.printSelf(indent+1)
        if self.one != None:
            print "%sOne:"%(ind)
            self.one.printSelf(indent+1)
    
    def is_leaf(self):
        return (self.zero == None and self.one == None)
    
    def optimize(self,action):
        propagate_action = action
        if (self.action != None):
            propagate_action = self.action
            
        if (self.zero != None):
            self.zero.optimize(propagate_action)
            if (self.zero.action == propagate_action and self.zero.action != None):
                self.ips.extend(self.zero.ips)
                self.action = propagate_action
                self.zero.ips = []
                self.zero.action = None
                if self.zero.is_leaf():
                    self.zero = None
        if (self.one != None):
            self.one.optimize(propagate_action)
            if (self.one.action == propagate_action and self.one.action != None):
                self.ips.extend(self.one.ips)
                self.action = propagate_action
                self.one.ips = []
                self.one.action = None
                if self.one.is_leaf():
                    self.one = None
        if (self.zero != None and self.one != None and \
            self.zero.action == self.one.action and self.zero.action != None):
            self.action = self.zero.action
            self.ips.extend(self.zero.ips)
            self.ips.extend(self.one.ips)
            self.zero.ips = []
            self.zero.action = None
            self.one.ips = []
            self.one.action = None
            if self.zero.is_leaf():
                self.zero = None
            if self.one.is_leaf():
                self.one = None
              
    def output_compressed(self, power, cip, result):
        if (self.zero != None):
            self.zero.output_compressed(power-1, cip, result)
        if (self.one != None):
            self.one.output_compressed(power-1, int(cip + pow(2,power-1)), result)
        if len(self.ips) > 0:
            result.append((cip,32-power,self.action,self.ips))
          
    
def compress_ip_list(ip_list):
    '''
    ip_list is a list of ip address, subnet, next_hop,... of type (int,int,string,...)
    we compress it, and return a list of (int ip address,int subnet,next_hop,[ip_list_elem]) where list of
    ip_list_elem shows which input ipl_list elem is compressed to create the output entry and next_hop is a
    string indicating the next hop.
    '''
    root = node()
    # create the tri
    for elem in ip_list:
        cur = root
        for i in range(31,31-elem[1],-1):
            next_bit = (elem[0] >> i) & 0x1
            if (next_bit == 0):
                if (cur.zero == None):
                    cur.zero = node()
                cur = cur.zero
            elif (next_bit == 1):
                if (cur.one == None):
                    cur.one = node()
                cur = cur.one
        if (len(cur.ips) == 0):
            cur.ips.append(elem)
            cur.action = elem[2]

    # optimize the tri
    #root.printSelf(0)
    root.optimize(None)
    #root.printSelf(0)
    result = []
    root.output_compressed(32, 0, result)
    return result
        