import unittest

from covertutils.handlers import SimpleShellHandler
from covertutils.orchestration import StackOrchestrator

from os import urandom
from time import sleep
from hashlib import sha512
import re
out_length = 4
in_length = 4


orch1 = StackOrchestrator( "passphrase",
    2, out_length, in_length,
    # cycling_algorithm = sha512
    )

orch2 = StackOrchestrator( "passphrase",
    2, out_length, in_length,
    # cycling_algorithm = sha512,
    reverse = True)

chunks = []
def dummy_receive( ) :
    while not chunks :
        sleep(0.1)
    # print "Receiving"
    return chunks.pop(0)


testable = None

def dummy_send( raw ) :
    global testable
    # print "sending!"
    stream, message = orch1.depositChunk( raw )
    if message :
        testable = message



class Test_ShellHandler (unittest.TestCase) :

    def setUp( self ) :
        self.p_handler = SimpleShellHandler( dummy_receive, dummy_send, orch2 )

    def test_shell_usage( self, ) :
        echoed = '111111111111'
        chunk = orch1.readyMessage( "echo '%s' " % echoed, 'main' )

        chunks.extend( chunk )
        sleep(0.5)
        # print '======================================================='
        # print testable
        self.failUnless( testable.strip() == echoed )