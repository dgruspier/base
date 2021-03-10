###############################################################################
# receiver.py
# Name: Daniel Gruspier
# BU ID: U88626811
# Collaboration Note: Completed in collaboration with Kenneth Chan (kenc@bu.edu)
###############################################################################

import sys
import socket

from util import *

def receiver(receiver_port, window_size):
    """TODO: Listen on socket and print received message to sys.stdout"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', receiver_port))
    # Establish data types
    START = 0
    END = 1
    DATA = 2
    ACK = 3
    next_seq = 0
    buf = []
    while True:
        # receive packet
        pkt, address = s.recvfrom(2048)
        
        # extract header and payload
        pkt_header = PacketHeader(pkt[:16])
        msg = pkt[16:16+pkt_header.length]

        # verify checksum
        pkt_checksum = pkt_header.checksum
        pkt_header.checksum = 0
        computed_checksum = compute_checksum(pkt_header / msg)
        #if pkt_checksum != computed_checksum:
         #   print "checksums not match"

        # print payload
        #print msg

        # send ACK
        if pkt_header.type == START and pkt_checksum == computed_checksum:
		# print msg
		ack_header = PacketHeader(type=ACK, seq_num=pkt_header.seq_num, length=0)
		ack_header.checksum = compute_checksum(ack_header / '')
                ack_pkt = ack_header / ''
		s.sendto(str(ack_pkt), address)
		next_seq = 0
	if pkt_header.type == DATA \
	   and pkt_checksum == computed_checksum \
	   and not pkt_header.seq_num > (next_seq + window_size):
		ack_header = PacketHeader(seq_num = next_seq + 1)
		if pkt_header.seq_num == next_seq:
			sys.stdout.write(msg)
			next_seq += 1
		else:
			buf.append(msg)
			buf.append(pkt_header.seq_num)
		ack_header.type = ACK
		ack_header.length = 0   #tHeader(type=ACK,seq_num=(next_seq + 1), length=0)
		ack_header.checksum = compute_checksum(ack_header / '')
		ack_pkt = ack_header / ''
		s.sendto(str(ack_pkt),address)
		#next_seq += 1
	elif pkt_header.type == DATA and pkt_checksum == computed_checksum and pkt_header.seq_num != next_seq:
		ack_header = PacketHeader(type=ACK,seq_num=next_seq,length=0)
		ack_header.checksum = compute_checksum(ack_header / '')
		ack_pkt = ack_header / ''
		s.sendto(str(ack_pkt),address)
		
	if pkt_header.type == END and pkt_checksum == computed_checksum:
		ack_header = PacketHeader(type=ACK, seq_num=pkt_header.seq_num, length=0)
		ack_header.checksum = compute_checksum(ack_header / '')
		ack_pkt = ack_header / ''
		s.sendto(str(ack_pkt),address)
	for i in range(len(buf) // 2):
		if next_seq in buf:
			ind = buf.index(next_seq)
			dat = buf.pop(ind - 1)
			del buf[ind - 1 : ind + 1]
			sys.stdout.write(dat)
			next_seq += 1
	sys.stdout.flush()

def main():
    """Parse command-line argument and call receiver function """
    if len(sys.argv) != 3:
        sys.exit("Usage: python receiver.py [Receiver Port] [Window Size]")
    receiver_port = int(sys.argv[1])
    window_size = int(sys.argv[2])
    receiver(receiver_port, window_size)

if __name__ == "__main__":
    main()
