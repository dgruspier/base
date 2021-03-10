###############################################################################
# sender.py
# Name: Daniel Gruspier
# BU ID: U88626811
# Collaboration note: Completed in collaboration with Kenneth Chan (kenc@bu.edu)
###############################################################################

import sys
import socket
#import random
#import time

from util import *
PKT_SIZE = 1472	# Bytes
WAIT_TIME = 0.5 # seconds
LOAD_LEN = 43 # Characters
BUFFER_LEN = 1400 # Bytes

def sender(receiver_ip, receiver_port, window_size):
    """TODO: Open socket and send message from sys.stdin"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #message = sys.stdin.read(PKT_SIZE)
   
    # Establish .type values
    START = 0
    END = 1
    DATA = 2
    ACK = 3

    # START message
    start_seq = 93928
    pkt_header = PacketHeader(type=START,seq_num = start_seq,length=0)
    pkt_header.checksum = compute_checksum(pkt_header / '')
    pkt = pkt_header / ''
    start_ack = ''
    start_ack_header = PacketHeader(start_ack)
    s.sendto(str(pkt), (receiver_ip, receiver_port))
    ack_checksum = 1
    computed_checksum = 2
    while True:				# Keep sending until we get an ACK
	if start_ack_header.type == ACK and start_ack_header.seq_num == start_seq and computed_checksum == ack_checksum:
		break
        s.settimeout(WAIT_TIME)		# Set 500ms timeout timer
    	try:
		start_ack , address = s.recvfrom(PKT_SIZE)	# Try to receive ACK on the socket
                start_ack_header = PacketHeader(start_ack[:16])
		ack_checksum = start_ack_header.checksum
		start_ack_header.checksum = 0
		computed_checksum = compute_checksum(start_ack_header / '')
	except:				# If 500ms pass and there is no ACK...
                s.sendto(str(pkt), (receiver_ip, receiver_port))	# Resend START

    # DATA message
    
    next_seq = 0					# First seq_num in the window
    #last_seq = next_seq + window_size			# Last seq_num in the window
    #final_seq = (len(message) // LOAD_LEN) + 1		# Last seq_num for the whole message
    all_pkts = []					# Store all pkts in memory in case retransmission is needed
    all_seqs = []					# For tracking which packets have already been created
    #all_acks = []
    #all_ack_seqs = []
    go_sign = 1
    ack_checksum = 1
    computed_checksum = 2
    while go_sign:
	last_seq = next_seq + window_size
	for i in range(next_seq,next_seq + window_size):
		#current_mes = message[i*LOAD_LEN:i*LOAD_LEN + LOAD_LEN]
                #pkt_header = PacketHeader(type=DATA,seq_num=i,length = len(current_mes))
		#pkt_header.checksum = compute_checksum(pkt_header / current_mes)
		#pkt = pkt_header / current_mes
                if not i in all_seqs:
			message = sys.stdin.read(BUFFER_LEN)
			if message == '':
				go_sign = 0
			pkt_header = PacketHeader(type=DATA,seq_num=i,length=len(message))
			pkt_header.checksum = compute_checksum(pkt_header / message)
			pkt = pkt_header / message
			all_pkts.append(pkt)
			all_seqs.append(pkt_header.seq_num)
		s.sendto(str(all_pkts[i]), (receiver_ip, receiver_port))
	#for i = [next_seq:next_seq + window_size - 1]:
	#	s.sendto(str(all_pkts[i]), (receiver_ip, receiver_port))
	#	s.settimeout(WAIT_TIME)
	#while next_seq < last_seq:
	#s.sendto(str(all_pkts[next_seq]), (receiver_ip, receiver_port))
	#ack_count = 0
	window = range(next_seq, next_seq + window_size)
	for h in window:
	#	print 'Current window: ' + str(range(next_seq, next_seq + window_size))
		s.settimeout(WAIT_TIME)
                try:
			ack_pkt , address = s.recvfrom(PKT_SIZE)
			ack_header = PacketHeader(ack_pkt[:16])
			#print 'ACK recvd: ' + str(ack_header.seq_num)
			ack_checksum = ack_header.checksum
			ack_header.checksum = 0
			computed_checksum = compute_checksum(ack_header / '')
			#if not ack_header.seq_num in all_ack_seqs:
			#	all_acks.append(ack_pkt)
			#	all_ack_seqs.append(ack_header.seq_num)
			#print 'ACK recvd?' + str(ack_header.type==ACK and ack_header.seq_num == next_seq and computed_checksum == ack_checksum)
			if ack_header.type == ACK and ack_header.seq_num == (next_seq + 1) \
			   and computed_checksum == ack_checksum:
				next_seq += 1
			#	print 'Current window: ' + str(range(next_seq, next_seq + window_size))
				#ack_count += 1
		except:
				#s.sendto(str(all_pkts[next_seq]), (receiver_ip, receiver_port))
				break
		
			
    # END message
 #   print "Now sending END MESSAGE..."
    end_seq = 99928
    end_pkt_header = PacketHeader(type=END, seq_num=end_seq, length=0)
    end_pkt_header.checksum = compute_checksum(end_pkt_header / '')
    end_pkt = end_pkt_header / ''
    end_ack = ''
    end_ack_header = PacketHeader(end_ack)
    s.sendto(str(end_pkt), (receiver_ip, receiver_port))
    ack_checksum = 1
    computed_checksum = 2
    while True:
    	if end_ack_header.type==ACK and end_ack_header.seq_num==end_seq and computed_checksum == ack_checksum:
		break
	s.settimeout(WAIT_TIME)
	try:
#		print "Waiting for ACK..."
		end_ack, address = s.recvfrom(PKT_SIZE)
		end_ack_header = PacketHeader(end_ack[:16])
		ack_checksum = end_ack_header.checksum
		end_ack_header.checksum = 0
		computed_checksum = compute_checksum(end_ack_header / '')
	except:
#		print "Trying again..."
		s.sendto(str(end_pkt), (receiver_ip, receiver_port))                
#    print "[DONE CLOSING CONNECTION]"
    s.close()

def main():
    """Parse command-line arguments and call sender function """
    if len(sys.argv) != 4:
        sys.exit("Usage: python sender.py [Receiver IP] [Receiver Port] [Window Size] < [message]")
    receiver_ip = sys.argv[1]
    receiver_port = int(sys.argv[2])
    window_size = int(sys.argv[3])
    sender(receiver_ip, receiver_port, window_size)

if __name__ == "__main__":
    main()
