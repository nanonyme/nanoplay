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
locations. Installing this installs a POSIX
script nanoplay which can be used for starting
the daemon. It currently saves pid and log to
current directory as twistd.log and twistd.pid
but these can be changed with --pidfile and
--logfile as usual. In other words, nanoplay
passes through parameters to twistd so most should
work although it strictly requires glib2 reactor.
Additional requirements that aren't available through
PyPI are gstreamer along with its Python integration
and glib2.
