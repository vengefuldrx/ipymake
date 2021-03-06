from threading import Thread, enumerate, Condition
from select import poll, POLLIN
import time
import sys
import os
import mmap
import getopt
from pykusp import configfile
from datastreams import namespaces 
import dski_mod
import struct
import signal
import clksync_mod
import optparse
import socket
import pprint

# general purpose routines for interacting with DSKI
# see dskid, dskitrace
#
# author: andrew boie

respmap = {
	"ACCEPT" : 1,
	"REJECT" : 2,
	"PASS" : 3,
}
# where stuff is in debugfs
DSKI_DIR = "/debug/datastreams"
DSKI_DEVICE = "/dev/dski"
INPUT_FILE_BASE = "cpu"
OUTPUT_FILE_BASE = "cpu"
RELAY_DIR = None


class datastream:
	"""A datastream is an object that has a particular
	configuration of filters and enabled entities"""

	def __init__(self, context, name, channel):
		self.name = name
		self.channel = channel
		self.context = context
		self.dski_fd = context.dski_fd
		dski_mod.datastream_create(self.dski_fd, self.name)

	def debug(self, msg):
		print "dski [datastream "+`self.name`+"]:",msg


	def start_logging(self):
		"""Call this after all entities have been enabled
		and filtering is set up"""
		#FIXME.J - should move channel assignment to different routine, as it is no
		#          longer used to signify enabling of a datastream for loggin
		dski_mod.assign_channel(self.dski_fd, self.name, self.channel.get_id())
		dski_mod.datastream_enable(self.dski_fd, self.name)
		self.debug("Now logging events")

	def stop_logging(self):
		"""Stops event logging for this particular datastream"""
		dski_mod.datastream_disable(self.dski_fd, self.name)
		self.debug("Stopping logging events")

	def close(self):
		self.debug("closing")
		dski_mod.datastream_destroy(self.dski_fd, self.name)
		self.dski_fd = None

	def pid_filter(self, pids, default_response):
		"""Add a PID filter to the end of the datastream's filter
		chain. default_response represents the action the filter will
		take when an event generated by a thread not in the group of
		threads we are tracking is seen"""

		pid_lst = []
		for k, v in pids:
			self.debug("Set PID "+v["response"]+" for task "+`k`)
			pid_lst.append((k, respmap[v["response"]]))
		dfl = respmap[default_response]

		
		dski_mod.apply_pid_filter(self.dski_fd, self.name, pid_lst, dfl)

	def discovery_filter(self, ta_name):
		"""Add a discovery filter to the end of the datastream's
		filter chain"""
		print "name", self.name
		print "ta_name", ta_name
		dski_mod.apply_discovery_filter(self.dski_fd, self.name, ta_name)

	def strace_filter(self, ccsm_name):
		"""Add a strace filter to the end of the datastream's filter chain"""
		dski_mod.apply_strace_filter(self.dski_fd, self.name, ccsm_name)

	def task_filter(self, pid, ccsm_set_name, default_response):
		""" This is the python wrapper for the CCSM based task filter"""
		dski_mod.apply_task_filter(self.dski_fd,self.name, pid, ccsm_set_name, respmap[default_response])
	
	def systemMonitor_filter(self, list, sysCallList, procfile_name, userid):
		"""Add a System Monitor Tool to the end of the datastream's
		filter chain"""
		dski_mod.apply_systemMonitor_filter(self.dski_fd, self.name, procfile_name, list, sysCallList, userid)

	def enable_family(self, fname):
		self.debug("Enabling family "+fname)

		ents = self.context.ns.get_family(fname)
		if not ents:
			print "Warning: No events found in family: %s" % fname
		for ent in ents:
			dski_mod.entity_enable(self.dski_fd, self.name, 
				ent.get_id())

	def enable_entity(self, fname, ename):
		self.debug("Enabling entity "+fname+"/"+ename)

		espec = self.context.ns.get_entity(fname, ename)
		dski_mod.entity_enable(self.dski_fd, self.name, 
				espec.get_id())

	def enable_histogram(self, fname, ename, min, max, buckets, tune):
		self.debug("Enabling histogram "+fam+"/"+ename+"("+`min`+","+`max`+","+`buckets`+","+`tune`+")")

		espec = self.context.ns.get_entity(fname, ename)

		if espec.get_type() != namespaces.HISTOGRAMTYPE:
			raise Exception(`espec`+" is not a histogram")

		dski_mod.histogram_enable(self.dski_fd, self.name,
				espec.get_id(), min, max, buckets, tune)

	def process_enabled_dict(self, enabled):
		for fam, ents in enabled.items():
			if type(ents) is not list: 
				if ents:
					self.enable_family(fam)
				continue

			for ename in ents:
				try:
					if type(ename) is str:	
						self.enable_entity(fam, ename)
					else:
						ename, eparam = ename
						self.enable_histogram(fam, ename,
								eparam["lowerbound"],
								eparam["upperbound"],
								eparam["buckets"],
								eparam["tune"])
				except KeyError, ke:
					print "dski: Could not enable",fam+"/"+ename+": not found"


	def process_filter_list(self, filterlist):
		for fname, fparam in filterlist:
			if fname == "task":
				self.task_filter(fparam.get("pid", -1), 
						 fparam["ccsm_name"], 
						 fparam.get("default_response", "REJECT"))
			elif fname == "discover":
				for item in fparam.get("enabled", []):
					famAndEventName = item.partition("/")
					fam = famAndEventName[0] 
					ename = famAndEventName[2]
					self.enable_entity(fam, ename)
				self.discovery_filter(fparam.get("ta_name", []))
			else:
				# ADD ADDITIONAL FILTERS TO THIS IF BLOCK
				print "dski: Unknown filter: ",fname

class dski_context:
	def __init__(self, output_base):
		self.datastreams = {}
		self.channels = {}
		self.dski_fd = open(DSKI_DEVICE)
		self.output_base = output_base
#		taskalias.add_alias("dskid")
		
		# query the kernel for namespace information, and
		# construct a namespace data structure
		#
		# FIXME - be sure to update fam (family name) to
		# better represent the current language (category name)
		aips = dski_mod.ips_query(self.dski_fd)
		self.ns = namespaces.Namespace()
		for fam, ent, edf, type, id, desc in aips:
			if type == namespaces.EVENTTYPE:
				ent = namespaces.EventSpec(fam, ent, desc, edf, id)
			elif type == namespaces.HISTOGRAMTYPE:
				ent = namespaces.HistogramSpec(fam, ent, desc, edf, id)
			elif type == namespaces.COUNTERTYPE:
				ent = namespaces.CounterSpec(fam, ent, desc, id)
			elif type == namespaces.INTERVALTYPE:
				ent = namespaces.IntervalSpec(fam, ent, desc, id)
			elif type == namespaces.INTERNALEVENTTYPE:
				ent = namespaces.InternalEventSpec(fam, ent, desc, edf, id)
			self.ns.add_entity(ent)
		self.debug("context opened")

	def get_output_filenames(self):
		result = []
		for chan in self.channels.values():
			result.extend(chan.get_output_filenames())
		return result
	
	def debug(self, msg):
		print "dski ["+`self.output_base`+"]:",msg


	def close(self):
		for d in self.datastreams.values():
			self.debug("dski: closing datastream "+d.name)
			d.close()
		
		for chan in self.channels.values():
			self.debug("closing channel "+chan.name)
			chan.close()
		
		self.dski_fd.close()
		self.debug("closed")

	def create_channel(self, name, buf_size, num_bufs, timeout, 
			ringbuffer=False, mmap=True, threadless=False):
		c = dski_channel(self, name, buf_size, num_bufs,
				timeout, ringbuffer, mmap, threadless)
		self.channels[name] = c
		return c

	def create_datastream(self, name, channel_name):
		d = datastream(self, name, self.channels[channel_name])
		self.datastreams[name] = d
		return d

	def close_datastream(self, name):
		d = self.datastreams[name]
		del self.datastreams[name]
		d.close()


	def start_logging(self):
		for k,v in self.datastreams.items():
			v.start_logging()

	def get_namespace(self):
		return self.ns




def write_dski_header(fout, ns):
	"""The header for all datastream output files contains
	a struct with miscellaneous information, a CLKSYNC event,
	and an event for each entity in the namespace"""

	# <kusp-root>/datastreams/src/include/datastreams/header.h
	# defines this datastream header structure:
	#
	#struct dstream_header {
	#	uint32_t magic_number;
	#	uint32_t sz_int;
	#	uint32_t sz_long;
	#	uint32_t sz_short;
	#	uint32_t sz_long_long;
	#	uint32_t sz_ptr;
	#	char hostname[80];
	#} __attribute__ ((packed));

	header = struct.pack("IIIIII80s", 0x1abcdef1, 4, 4, 
		2, 8, 4, socket.gethostname())
	fout.write(header)

	# this gets clock synchronization module info and packs
	# it into a clock data structure which is then used as
	# extra data for a standard event
	clk_info = clksync_mod.get_info()

	clk_data = struct.pack("illQQiPIIi", 0,
			clk_info["tv_sec"], clk_info["tv_nsec"],
			clk_info["ts"], clk_info["tsckhz"],
			0, 0, clk_info["shift"], clk_info["mult"], 0)
		
	# This is packing into a standard datastreams event structure,
	# but its currently unclear where 12 (event id?) and 7331 (event tag?)
	# come from.
	# <kusp-root>/datastreams/src/include/datastreams/entity.h
	clk_event = struct.pack("QIIIIi", clk_info["ts"], 0, 12, 
			7331, 0, len(clk_data))
	fout.write(clk_event)
	fout.write(clk_data)

	# We iterate through the Python data structure returned when we asked
	# for the kernel's entity namespace and pack the dictionary entry into
	# an event format.
	for entity in ns.values():
		# We can pack into the ns_fragment format located in the same
		# entity.h header file mentioned above.
		ns_data = struct.pack("48s48s48s48sII", 
				entity.get_family(), 
				entity.get_name(),
				"foo",
				entity.get_info_field(),
				entity.get_type(), 
				entity.get_id())
		ns_event = struct.pack("QIIIIi", clk_info["ts"], 0, 16, 1337, 
			0, len(ns_data))
		fout.write(ns_event)
		fout.write(ns_data)

	fout.flush()
		
	
# FIXME: cleanup
class reader_thread_mmap:
	"""Each DSKI channel has a reader thread per CPU. The reader
	thread pulls data out of the Relay FS and writes it to the output
	file"""

	def __init__(self, outdir, rdir, cpu, ns, chan):
		"""open file descriptors, create a poll object to block
		on reads to the relay FS"""

		# input, output
		file = "%s%d" % (INPUT_FILE_BASE, cpu)
		fpath = os.path.join(DSKI_DIR, rdir, file)
		self.fin = open(fpath, 'r')

		file = "%s%d.consumed" % (INPUT_FILE_BASE, cpu)
		fpath = os.path.join(DSKI_DIR, rdir, file)
		self.consumein = open(fpath, 'w')

		file = "%s%d.produced" % (INPUT_FILE_BASE, cpu)
		fpath = os.path.join(DSKI_DIR, rdir, file)
		self.producein = open(fpath, 'r')

		file = "%s%d.bin" % (OUTPUT_FILE_BASE, cpu)
		self.filename = os.path.join(outdir, file)
		self.fout = open(self.filename, 'wb')

		write_dski_header(self.fout, ns)

		self.chan = chan
		self.cpu = cpu

		self.obj = dski_mod.reader_thread_create(self.fin, self.fout,
			self.producein, self.consumein, 
			self.chan.num_bufs, self.chan.buf_size, self.cpu)

		pass



	def get_output_filename(self):
		return self.fout.name

	def join(self):
		dski_mod.reader_thread_kill(self.obj)

		print "dski:", self.filename,"wrote",self.fout.tell(),"bytes"
		self.fin.close()
		self.fout.close()
		self.producein.close()
		self.consumein.close()

	def start(self):	
		print "dski: mmap-based reader thread starting"
		dski_mod.reader_thread_run(self.obj);




class reader_thread(Thread):
	"""Each DSKI channel has a reader thread per CPU. The reader
	thread pulls data out of the Relay FS and writes it to the output
	file"""

	def __init__(self, outdir, rdir, cpu, ns, chan):
		"""open file descriptors, create a poll object to block
		on reads to the relay FS"""
		Thread.__init__(self)

		# input, output
		file = "%s%d" % (INPUT_FILE_BASE, cpu)
		fpath = os.path.join(DSKI_DIR, rdir, file)
		self.fin = open(fpath, 'r')

		file = "%s%d.bin" % (OUTPUT_FILE_BASE, cpu)
		self.filename = os.path.join(outdir, file)
		
		
		self.fout = open(self.filename, 'wb')
		write_dski_header(self.fout, ns)

		self.chan = chan

		# poll object to block on
		self.pollobj = poll()
		self.pollobj.register(self.fin.fileno(), POLLIN)
		pass
	
	

	def get_output_filename(self):
		return self.fout.name

	def cleanup(self):
		print "dski:", self.filename,"wrote",self.fout.tell(),"bytes"
		self.fin.close()
		self.fout.close()

	def run(self):
		print "dski: read-based reader thread starting"
#		taskalias.add_alias("dskid")
		try:
			while not self.chan.thread_stop:
				self.pollobj.poll(1000)
				self.fout.write(self.fin.read())
		finally:
			self.cleanup()



class dski_channel:
	"""A DSKI channel is the logging interface for DSKI, analogous to the
	logging_thread datastructure in DSUI. It creates a RelayFS based out
	put channel for binary data. This class talks to the kernel and creates
	the channel, and also creates threads in userspace to read the per-CPU
	binary data and write it out to the output file(s)."""
	def __init__(self, context, name,buf_size, num_bufs, 
			timeout, ringbuffer = False, mmap = True, threadless = False):
	
		self.outfiles = []
		self.name = name

		self.thread_stop = False
	

		# member variables
		self.threads = []
		self.dski_fd = context.dski_fd
		self.output_base = os.path.join(context.output_base, name)
		self.buf_size = buf_size
		self.num_bufs = num_bufs
	
		if ringbuffer:
			flags = dski_mod.DS_CHAN_TRIG
		else:
			flags = dski_mod.DS_CHAN_CONT


		if mmap:
			flags = flags | dski_mod.DS_CHAN_MMAP


		self.id = dski_mod.channel_open(context.dski_fd, buf_size, 
			num_bufs, flags, timeout)
		try:
			os.makedirs(self.output_base)
		except Exception, e:
			print e
			pass
		rdir = dski_mod.relay_dir(self.dski_fd)
		RELAY_DIR = os.path.join(DSKI_DIR, rdir)
		chan_dir = os.path.join(RELAY_DIR, "chan"+`self.id`)

		# used by threadless channels (read directly by postprocessing)
		self.input_filenames = []

		for cpufile in os.listdir(chan_dir):
			nada, cpu = cpufile.split(INPUT_FILE_BASE)

			try:
				cpu = int(cpu)
			except ValueError:
				continue

			if threadless:
				file = "%s%d" % (INPUT_FILE_BASE, cpu)
				fpath = os.path.join(DSKI_DIR, chan_dir, file)

				self.input_filenames.append(fpath)
				continue

			if mmap:
				self.threads.append(reader_thread_mmap(self.output_base, 
					chan_dir, cpu, context.ns, self))
			else:
				self.threads.append(reader_thread(self.output_base, 
					chan_dir, cpu, context.ns, self))

		for thread in self.threads:
			self.outfiles.append(thread.get_output_filename())
			thread.start()

	def get_output_filenames(self):
		return self.outfiles

	def get_input_filenames(self):
		return self.input_filenames


	def get_id(self):
		return self.id

	def debug(self, msg):
		print "dski [channel "+`self.id`+"]:",msg

	def flush(self):
		self.debug("flushing channel")
		dski_mod.channel_flush(self.dski_fd, self.id)

	
	def close(self):
		self.debug("closing")
		self.thread_stop = True

		self.flush()
		time.sleep(0.5)

		self.debug("terminating threads")
		for thread in self.threads:
			self.debug("terminating " + thread.filename)
			thread.join()

		dski_mod.channel_close(self.dski_fd, self.id)

