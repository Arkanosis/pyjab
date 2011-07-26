#! /usr/bin/env python
# -*- coding: utf-8 -*-

# pyjab v0.1
# (C) 2011 Jérémie Roquet
# arkanosis@gmail.com

import os.path
import sys

import dbus

_rcfile = os.path.expanduser('~/.pyjabrc')

if __name__ == '__main__':

    aliases = {}

    if os.path.exists(_rcfile):
        with open(_rcfile) as configuration:
            for line in configuration:
                if not line.strip().startswith('#'):
                    alias, username = line.strip().replace(' ', '').split('=')
                    if username not in aliases:
                        aliases[username] = [username]
                    aliases[username].append(alias)

    bus = dbus.SessionBus()

    client = dbus.Interface(
        bus.get_object(
            'im.pidgin.purple.PurpleService',
            '/im/pidgin/purple/PurpleObject'
        ),
        'im.pidgin.purple.PurpleInterface'
    )

    def name(login):
        return login.split('@')[0]

    if len(sys.argv) == 1:
        print 'Usage: pyjab <username[,username[…]]> <message to send>'
        print 'Available recipients:'
        for conversation in client.PurpleGetIms():
            print '\t', name(client.PurpleConversationGetName(conversation))

    elif sys.argv[1:] == ['*']:
        print ','.join([name(client.PurpleConversationGetName(conversation)) for conversation in client.PurpleGetIms()])

    else:
        recipients = set(sys.argv[1].split(','))

        for conversation in client.PurpleGetIms():
            username = name(client.PurpleConversationGetName(conversation))
            userAliases = aliases.get(username, [username])
            for recipient in recipients:
                if recipient in userAliases:
                    print 'sending "%s" to %s' % (' '.join(sys.argv[2:]), username)
                    client.PurpleConvImSend(
                        client.PurpleConvIm(conversation),
                        ' '.join(sys.argv[2:])
                    )
                    recipients.remove(recipient)
                    break
        for recipient in recipients:
            print 'Recipient "%s" not found' % recipient
