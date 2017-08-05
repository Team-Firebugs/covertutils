import unittest

from pprint import pprint
from os import urandom
from random import randint, choice, shuffle
from covertutils.orchestration import StackOrchestrator

from hashlib import sha512


class TestOrchestrator( unittest.TestCase ) :
	# pass
	streams = ['main', 'control']

	def setUp( self ) :

		self.out_length = 10
		self.in_length = 11

		passp_ = "passphrase"
		self.orch1 = StackOrchestrator( passp_,
			2, self.out_length, self.in_length,
			# cycling_algorithm = sha512
			 )
		self.orch2 = StackOrchestrator( passp_,
			2, self.out_length, self.in_length,
			# cycling_algorithm = sha512,
			reverse = True)


	def test_readyMessage( self ) :

		payload = "A"*5
		chunks = self.orch1.readyMessage( payload )


	def test_reset( self ) :
		self.orch1.reset()
		self.orch2.reset()


	def test_usage_simple_control( self ) :
		self.test_reset()
		l = randint(1,100)
		payload = urandom(l)
		chunks = self.orch1.readyMessage( payload )

		for chunk in chunks :
			stream, ret = self.orch2.depositChunk( chunk )
		self.failUnless( payload == ret )


	def test_length_consistency( self ) :
		self.test_reset()
		l = randint(1,100)
		payload = urandom(l)
		chunks = self.orch1.readyMessage( payload )
		for c in chunks :
			self.failUnless( len(c) == self.out_length )



	def test_usage_simple_control( self ) :
		self.test_reset()

		l = randint(1,100)
		payload = urandom(l)
		chunks = self.orch1.readyMessage( payload, 'main' )

		for chunk in chunks :
			stream, ret = self.orch2.depositChunk( chunk )
		self.failUnless( payload == ret )

		self.failUnless( stream == 'main' )



	def test_stream_dict( self, n = 100, rep = 10 ) :
		byte_n = 0

		orch1 = self.orch1
		orch2 = self.orch2

		for repetition in range (rep) :
			self.test_reset()

			d = {}
			for s in self.streams :
				d[s] = ''


			for i in range(n) :
				s = choice( self.streams )
				l = randint( 1, 100 )
				pload = urandom( l )
				byte_n += len( pload )
				d[s] = pload
			# print d


			chunks = []
			for s in self.streams :
				chunks.extend( orch1.readyMessage(d[s], s) )

			trash = [urandom( len(chunks[-1]) ) for i in range( n*2 )]

			for i in range( len(trash) ) :		# Simulate fake packets
				index = randint( 1, len(chunks) )
				chunks.insert( index, trash[i] )

			for chunk in chunks :
				orch2.depositChunk( chunk )

			d2 = orch2.getStreamDict()
			# pprint( d )
			# print '============'
			# pprint( d2 )
			print "[*] Round %d. Accumulated %d bytes" % ( repetition, byte_n )
			self.failUnless( d == d2 )

			orch1, orch2 = orch2, orch1