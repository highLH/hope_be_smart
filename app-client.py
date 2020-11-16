#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback

import libclient


if len(sys.argv) != 6:
    print("usage:", sys.argv[0], "<host> <port> <action> <dest> <payload>")
    sys.exit(1)

sel = selectors.DefaultSelector()

host, port = sys.argv[1], int(sys.argv[2])
action, addr, payload = sys.argv[3], sys.argv[4], sys.argv[5]

request = libclient.create_request(action, addr, payload)
libclient.start_connection(sel, host, port, request)

try:
    while True:
        events = sel.select(timeout=1)
        for key, mask in events:
            message = key.data
            try:
                message.process_events(mask)
            except Exception:
                print(
                    "main: error: exception for",
                    f"{message.addr}:\n{traceback.format_exc()}",
                )
                message.close()
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()