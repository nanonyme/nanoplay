nanoplay
=========
This is a simplistic music playing server.
Music is netcatted into the payload port
and control messages can be sent to the
other port. Defaults are 5000 and 5001
for payload and control respectively.
nanoplay supports --payload and --control
for giving Twisted endpoints strings for
binding the server components to different
locations. 