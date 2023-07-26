#!/usr/bin/python
# @lint-avoid-python-3-compatibility-imports
#
# ext4slower  Trace slow ext4 operations.
#             For Linux, uses BCC, eBPF.
#
# USAGE: ext4slower [-h] [-j] [-p PID] [min_ms]
#
# This script traces common ext4 file operations: reads, writes, opens, and
# syncs. It measures the time spent in these operations, and prints details
# for each that exceeded a threshold.
#
# WARNING: This adds low-overhead instrumentation to these ext4 operations,
# including reads and writes from the file system cache. Such reads and writes
# can be very frequent (depending on the workload; eg, 1M/sec), at which
# point the overhead of this tool (even if it prints no "slower" events) can
# begin to become significant.
#
# By default, a minimum millisecond threshold of 10 is used.
#
# Copyright 2016 Netflix, Inc.
# Licensed under the Apache License, Version 2.0 (the "License")
#
# 11-Feb-2016   Brendan Gregg   Created this.
# 15-Oct-2016   Dina Goldshtein -p to filter by process ID.

#latest: 2021-12-08

#WRITE tracepoint:
#total_latency : vfs_write-return - vfs_write-entry
#       vfs_latecny: ext4_file_write_iter-entry - vfs_write-entry
#       ext4_latecny:  ext4_file_write_iter-return - ext4_file_write_iter-entry
#             gen_latency: __generic_file_write_iter-return - __generic_file_write_iter-entry
#                     buffer_write_latecny: generic_perfom_write-return - generic_perforn_write-entry
#                     direct _write_latecnt: generic_file_direct_write-return -  generic_file_direct_write-entry
#READ tracepoints:
#total_latency: vfs_read-return - vfs_read-entry
#       vfs_latecny: ext4_file_read_iter-entry - vfs_read-entry
#       ext4_latency: ext4_file_read_iter-return - ext4_file_read_iter-entry
#             gen_latency: generic_file_read_iter-return - __generic_file_read_iter-entry
                        
#FSYNC tracepoints:
#total_latency: vfs_fsync_range-return - vfs_fsync_range-entry
#       vfs_latency: ext4_sync_file-entry - vfs_sync-entry
#       ext4_latency:ext4_sync_file-return - ext4_sync_file-entry
#                writeout_latency:file_write_and_wait_range-return - file_write_and_wait_range-entry
#                jbd2_latency:jbd2-complete-transaction-return - jbd2-complete-transaction-entry

from __future__ import print_function
from bcc import BPF
import argparse
from time import sleep, strftime

import ctypes as ct
import json
from collections import OrderedDict
from container_map_create import ContainerMapCreate

# symbols
kallsyms = "/proc/kallsyms"

# arguments
examples = """examples:
    ./ext4slower                # trace operations slower than 10 ms (default)
    ./ext4slower 1              # trace operations slower than 1 ms
    ./ext4slower 0              # trace all operations (warning: verbose)
    ./ext4slower -t 10          # set the execution duration to 10s
    ./ext4slower -p 185         # trace PID 185 only
    ./ext4slower -o /tmp/file   # dump the latency info to /tmp/file with json format
	./ext4slower -c $container_name  # only inspect the file r/w by $container_name
"""
parser = argparse.ArgumentParser(
    description="Trace common ext4 file operations slower than a threshold",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=examples)
parser.add_argument("-p", "--pid",
    help="trace this PID only")
parser.add_argument("min_ms", nargs="?", default='10',
    help="minimum I/O duration to trace, in ms (default 10)")
parser.add_argument("-t", "--time", default=99999999, type=int,
    help="set the excution duation in seconds")
parser.add_argument("-o", "--output", type=str,
    help="dump the latency info to the specified file with json format")
parser.add_argument("-c", "--container", type=str,
	help="set the container to be inspected")
parser.add_argument("--ebpf", action="store_true",
    help=argparse.SUPPRESS)
args = parser.parse_args()
min_ms = int(args.min_ms)
pid = args.pid
debug = 0

# define BPF program
bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/fs.h>
#include <linux/sched.h>
#include <linux/dcache.h>
#include <linux/uio.h>
#include <linux/genhd.h>
#include <linux/cgroup-defs.h>

#define VFS_LAT    0   //generic phase
#define EXT4_LAT   1   //generic phase

#define GEN_LAT    2   //for read/write
#define BIO_LAT    3   //for buffer write
#define DIO_LAT    4   //for direct write
 
#define WR_WAIT_LAT 2  //for fsync
#define JBD2_LAT   3  //for sync

#define LAT_MAX_ITERM  5

enum op {
   OP_IS_READ,   
   OP_IS_DIRECT,
   OP_IS_SYNC
};

struct val_t {
    u64 ts;
    u32 flags;
    u32 is_rw;
    u64 offset;
	u64 cgrp_id;
    struct file *fp;
    u64 detail_lat[LAT_MAX_ITERM];
    
};

struct data_t {
    // XXX: switch some to u32's when supported
    u64 flags;
    u64 size;
    u64 offset;
    u64 total_lat;
    u64 detail_lat[LAT_MAX_ITERM];
    u64 pid;
	u64 cgrp_id;
    char task[TASK_COMM_LEN];
    char file[DNAME_INLINE_LEN];
    char diskname[DISK_NAME_LEN];
};

BPF_HASH(entryinfo, u64, struct val_t);
BPF_PERF_OUTPUT(events);

//
// Store timestamp and size on entry
//

//vfs_read()/vfs_write()/vfs_fsync_range()
int trace_vfs_entry(struct pt_regs *ctx, struct file *file)
{
    u64 id =  bpf_get_current_pid_tgid();
    u32 pid = id >> 32; // PID is higher part
    

    if (FILTER_PID)
        return 0;


    //bpf_trace_printk("sync_range_entry\\n");
    // only trace ext4 file through checking file->f_op == ext4_file_operations
    if ((u64)file->f_op != EXT4_FILE_OPERATIONS)
        return 0;

    // store filep and timestamp by id
    struct val_t val = {};
    val.ts = bpf_ktime_get_ns();
    val.fp = file;

    FILTER_CONTAINER

    if (val.fp)
        entryinfo.update(&id, &val);

    return 0;
}

//ext4_file_read_iter()/ext4_file_write_iter()
int trace_ext4_file_readwrite_entry(struct pt_regs *ctx, struct kiocb *iocb, struct iov_iter *from)
{
    struct val_t *valp;
    u64 id = bpf_get_current_pid_tgid();
    u32 pid = id >> 32; // PID is higher part

    valp = entryinfo.lookup(&id);
    if (valp == 0) {
        // missed tracing issue or filtered
        return 0;
    }

    if (iocb->ki_flags & IOCB_DIRECT)
	valp->flags |= 1 << OP_IS_DIRECT; 	
    if (from->type == READ)
	valp->flags |= 1 << OP_IS_READ;
    
    valp->is_rw = 1;
    valp->offset = iocb->ki_pos;
    u64 ts = bpf_ktime_get_ns();
    valp->detail_lat[VFS_LAT] = ts - valp->ts; 

    return 0;
}

//ext4_sync_file()
int trace_ext4_file_sync_entry(struct pt_regs *ctx)
{
    struct val_t *valp;
    u64 id = bpf_get_current_pid_tgid();
    u32 pid = id >> 32; // PID is higher part

    valp = entryinfo.lookup(&id);
    if (valp == 0) {
        // missed tracing issue or filtered
        return 0;
    }

    /*if on the read/write route, don't trace*/   
    if (valp->is_rw)
	return 0;
 
    valp->offset = 0;
    valp->flags |= 1 << OP_IS_SYNC;
    u64 ts = bpf_ktime_get_ns();
    valp->detail_lat[VFS_LAT] = ts - valp->ts; 
   
    return 0;
}

#if 0
int trace_ext4_file_sync_entry(struct pt_regs *ctx, struct file *file)
{
    u64 id =  bpf_get_current_pid_tgid();
    u32 pid = id >> 32; // PID is higher part

    if (FILTER_PID)
        return 0;
    bpf_trace_printk("sync_entry\\n"); 
    // store filep and timestamp by id
    struct val_t val = {};
    val.ts = bpf_ktime_get_ns();
    val.fp = file;
    val.offset = 0;
    val.flags |= 1 << OP_IS_SYNC;
    if (val.fp)
        entryinfo.update(&id, &val);

    return 0;
}
#endif

//ext4_file_read_iter()/ext4_file_write_iter()/ext4_sync_file()
int trace_ext4_file_op_ret(struct pt_regs *ctx)
{
    struct val_t *valp;
    u64 id = bpf_get_current_pid_tgid();
    u32 pid = id >> 32; // PID is higher part

    valp = entryinfo.lookup(&id);
    if (valp == 0) {
        // missed tracing issue or filtered
        return 0;
    }

    u64 ts = bpf_ktime_get_ns();
    valp->detail_lat[EXT4_LAT] = (ts - valp->ts -
				valp->detail_lat[VFS_LAT]) / 1000;
   valp->detail_lat[VFS_LAT] /= 1000;

    return 0;
}

static int generic_file_op_entry(struct pt_regs *ctx, int iterm)
{
    struct val_t *valp;
    u64 id = bpf_get_current_pid_tgid();
    u32 pid = id >> 32; // PID is higher part

    valp = entryinfo.lookup(&id);
    if (valp == 0) {
        // missed tracing issue or filtered
        return 0;
    }
    
    //temporarily save the timestamp
    valp->detail_lat[iterm] =  bpf_ktime_get_ns();

    return 0;
}

//__generic_perform_writ_iter()/generic_file_read_iter()
int trace_generic_readwrite_entry(struct pt_regs *ctx)
{
    return generic_file_op_entry(ctx, GEN_LAT);
}

//generic_perform_write()
int trace_generic_perfrom_write_entry(struct pt_regs *ctx)
{
    return generic_file_op_entry(ctx, BIO_LAT);
}

//generic_file_direct_write()
int trace_generic_direct_write_entry(struct pt_regs *ctx)
{
    return generic_file_op_entry(ctx, DIO_LAT);
}

static int generic_file_op_ret(struct pt_regs *ctx, int iterm)
{
    struct val_t *valp;
    u64 id = bpf_get_current_pid_tgid();
    u32 pid = id >> 32; // PID is higher part

    valp = entryinfo.lookup(&id);
    if (valp == 0) {
        // missed tracing issue or filtered
        return 0;
    }

    u64 ts = bpf_ktime_get_ns();
    valp->detail_lat[iterm] = (ts - valp->detail_lat[iterm]) / 1000;

    return 0;
}

//__generic_perform_writ_iter()/generic_file_read_iter()
int trace_generic_readwrite_ret(struct pt_regs *ctx)
{
    return generic_file_op_ret(ctx, GEN_LAT);
}

//generic_perform_write()
int trace_generic_perfrom_write_ret(struct pt_regs *ctx)
{
    return generic_file_op_ret(ctx, BIO_LAT);
}

//generic_file_direct_write()
int trace_generic_direct_write_ret(struct pt_regs *ctx)
{	
    return generic_file_op_ret(ctx, DIO_LAT);
}

//file_write_and_wait_range()/jbd2_complete_transaction()
static int ext4_sync_op_entry(struct pt_regs *ctx, int iterm)
{
    struct val_t *valp;
    u64 id = bpf_get_current_pid_tgid();
    u32 pid = id >> 32; // PID is higher part

    valp = entryinfo.lookup(&id);
    if (valp == 0) {
        // missed tracing issue or filtered
        return 0;
    }

    if ((valp->flags & (1 << OP_IS_SYNC)) == 0)
	return 0;

    //temporarily save the timestamp
    valp->detail_lat[iterm] =  bpf_ktime_get_ns();
    
    return 0;
}

//file_write_and_wait_range()
int trace_ext4_sync_write_wait_entry(struct pt_regs *ctx)
{
    return ext4_sync_op_entry(ctx, WR_WAIT_LAT);
}

//jbd2_complete_transaction()
int trace_ext4_sync_jbd2_comp_entry(struct pt_regs *ctx)
{
    return ext4_sync_op_entry(ctx, JBD2_LAT);
}

static int ext4_sync_op_ret(struct pt_regs *ctx, int iterm)
{
    struct val_t *valp;
    u64 id = bpf_get_current_pid_tgid();
    u32 pid = id >> 32; // PID is higher part

    valp = entryinfo.lookup(&id);
    if (valp == 0) {
        // missed tracing issue or filtered
        return 0;
    }

    if ((valp->flags & (1 << OP_IS_SYNC)) == 0)
        return 0;
    
    u64 ts = bpf_ktime_get_ns();
    valp->detail_lat[iterm] = (ts - valp->detail_lat[iterm]) / 1000;

    return 0;
}

//file_write_and_wait_range()
int trace_ext4_sync_write_wait_ret(struct pt_regs *ctx)
{
    return ext4_sync_op_ret(ctx, WR_WAIT_LAT);
}

//jbd2_complete_transaction()
int trace_ext4_sync_jbd2_comp_ret(struct pt_regs *ctx)
{
    return ext4_sync_op_ret(ctx, JBD2_LAT);
}

//
// Output
//

int trace_vfs_return(struct pt_regs *ctx)
{
    struct val_t *valp;
    u64 id = bpf_get_current_pid_tgid();
    u32 pid = id >> 32; // PID is higher part

    valp = entryinfo.lookup(&id);
    if (valp == 0) {
        // missed tracing issue or filtered
        return 0;
    }

    // calculate delta
    u64 ts = bpf_ktime_get_ns();    u64 total_lat = (ts - valp->ts) / 1000;
    entryinfo.delete(&id);
    if (FILTER_US)
        return 0;

    // populate output struct
    u32 size = PT_REGS_RC(ctx);
    struct data_t data = {.size = size, .total_lat = total_lat, .pid = pid};
    data.offset = valp->offset;
    data.flags = valp->flags;
    data.cgrp_id = valp->cgrp_id;
    bpf_trace_printk("cgrp_id:%d\\n", data.cgrp_id);
    bpf_probe_read(data.detail_lat, sizeof(data.detail_lat), valp->detail_lat);
    bpf_get_current_comm(&data.task, sizeof(data.task));

    // workaround (rewriter should handle file to d_name in one step):
    struct dentry *de = NULL;
    struct qstr qs = {};
    de = valp->fp->f_path.dentry;
    qs = de->d_name;
    if (qs.len == 0)
        return 0;
    bpf_probe_read(&data.file, sizeof(data.file), (void *)qs.name);
    
    struct gendisk *gendisk = valp->fp->f_mapping->host->i_sb->s_bdev->bd_disk;
    bpf_probe_read(&data.diskname, sizeof(data.diskname), gendisk->disk_name);

    // output
    events.perf_submit(ctx, &data, sizeof(data));

    return 0;
}
"""

#find map between container_id and container_name
container_map = ContainerMapCreate()
cgid_dict = container_map._create_container_map()
#print(cgid_dict)


# code replacements
with open(kallsyms) as syms:
    ops = ''
    for line in syms:
        (addr, size, name) = line.rstrip().split(" ", 2)
        name = name.split("\t")[0]
        if name == "ext4_file_operations":
            ops = "0x" + addr
            break
    if ops == '':
        print("ERROR: no ext4_file_operations in /proc/kallsyms. Exiting.")
        print("HINT: the kernel should be built with CONFIG_KALLSYMS_ALL.")
        exit()
    bpf_text = bpf_text.replace('EXT4_FILE_OPERATIONS', ops)
if min_ms == 0:
    bpf_text = bpf_text.replace('FILTER_US', '0')
else:
    bpf_text = bpf_text.replace('FILTER_US',
        'total_lat <= %s' % str(min_ms * 1000))
if args.pid:
    bpf_text = bpf_text.replace('FILTER_PID', 'pid != %s' % pid)
else:
    bpf_text = bpf_text.replace('FILTER_PID', '0')

if args.container:
	cgid = -1
	for k,v in cgid_dict.items():
		if args.container == v:
			cgid = int(k)
			bpf_text = bpf_text.replace('FILTER_CONTAINER',
					'struct task_struct *task;' +
    					'struct cgroup_subsys_state * css;' +
    					'task = (struct task_struct *)bpf_get_current_task();' +
    					'css = (struct cgroup_subsys_state *)task->sched_task_group;' +
    					'u64 cgrp_id = css->cgroup->kn->id.id;' +
					'bpf_trace_printk("cgrp_id:%d,pid:%d\\n", cgrp_id, pid);' +
					'if (cgrp_id != %d)' %cgid +
					'{return 0;}' +
					'val.cgrp_id = cgrp_id;')
	if cgid == -1:
		bpf_text = bpf_text.replace('FILTER_CONTAINER', 'return 0; ')
else:
	bpf_text = bpf_text.replace('FILTER_CONTAINER',
				'struct task_struct *task;' +
    				'struct cgroup_subsys_state * css;' +
    				'task = (struct task_struct *)bpf_get_current_task();' +
    				'css = (struct cgroup_subsys_state *)task->sched_task_group;' +
    				'u64 cgrp_id = css->cgroup->kn->id.id;' +
				'val.cgrp_id = cgrp_id;')


if debug or args.ebpf:
    print(bpf_text)
    if args.ebpf:
        exit()

# kernel->user event data: struct data_t
DNAME_INLINE_LEN = 32   # linux/dcache.h
TASK_COMM_LEN = 16      # linux/sched.h
DISK_NAME_LEN = 32      # linux/genhd.h
LAT_MAX_ITERM = 5       # #define LAT_MAX_ITERM 5
OP_IS_READ = 0
OP_IS_DIRECT = 1
OP_IS_SYNC = 2
class Data(ct.Structure):
    _fields_ = [
        ("flags", ct.c_ulonglong),
        ("size", ct.c_ulonglong),
        ("offset", ct.c_ulonglong),
        ("total_lat", ct.c_ulonglong),
	("detail_lat", ct.c_ulonglong *  LAT_MAX_ITERM),
        ("pid", ct.c_ulonglong),
	("cgrp_id", ct.c_ulonglong),
        ("task", ct.c_char * TASK_COMM_LEN),
        ("file", ct.c_char * DNAME_INLINE_LEN),
	("diskname", ct.c_char * DISK_NAME_LEN)
    ]

# process event
def flags_print(flags):
    type = ''
    if flags & (1 << OP_IS_READ):
        type += 'R'
    else:
        type += 'W'
    if flags & (1 << OP_IS_DIRECT):
        type += 'D'
    else:
        type += 'B'

    if flags & (1 << OP_IS_SYNC):
        type = 'S'
    
    return type

def print_event(cpu, data, size):
    event = ct.cast(data, ct.POINTER(Data)).contents

    type = flags_print(event.flags)
	
    if cgid_dict.has_key(str(event.cgrp_id)):
        container = cgid_dict[str(event.cgrp_id)][0:12]
    else:
        container = event.cgrp_id
    print("%-8s %-12s %-14.14s %-6s %2s %-7s %-8d %-7.2f %-7.2f %-8.2f %-11.2f %-11.2f %-7.2f %-5s %s" 
	% (strftime("%H:%M:%S"),container, event.task.decode(), event.pid, type, event.size, event.offset / 1024,
        float(event.total_lat)/1000, float(event.detail_lat[0])/1000, float(event.detail_lat[1])/1000, 
        float(event.detail_lat[2])/1000, float(event.detail_lat[3])/1000, float(event.detail_lat[4])/1000, 
        event.diskname.decode(), event.file.decode()))

if args.output:
	w_f = open(args.output, 'a+')
def store_event_data(cpu,data, size):
        event = ct.cast(data, ct.POINTER(Data)).contents

	lat_info = OrderedDict()
        detail_lat= OrderedDict()
	ext4_detail_lat = OrderedDict()

        lat_info["checktime"] = strftime("%Y-%m-%d-%H:%M:%S")
        lat_info["diskname"] = event.diskname.decode() 
        lat_info["file"] = event.file.decode()
        lat_info["comm"] = event.task.decode()
        lat_info["pid"] = event.pid
        lat_info["type"] = flags_print(event.flags)
        lat_info["total_lat(us)"] = event.total_lat
       
	detail_lat["vfs"] = event.detail_lat[0]
	detail_lat["ext4"] = event.detail_lat[1]
	if lat_info["type"] == 'S':
		ext4_detail_lat["write_wait"] = event.detail_lat[2]
		ext4_detail_lat["jbd2_complete"] = event.detail_lat[3]
	else:
		ext4_detail_lat["generic"] = event.detail_lat[2]
	
	if lat_info["type"] == 'WB':
		ext4_detail_lat["perform_write"] = event.detail_lat[3]
	if lat_info["type"] ==  "WD":
		ext4_detail_lat["direct_write"] = event.detail_lat[3]
         
	detail_lat["ext4_detail_lat"] = ext4_detail_lat
        lat_info["detail_lat"] = detail_lat
        
	#with open(args.output, 'a+') as w_f:
        json.dump(lat_info, w_f, indent=4, separators=(',', ':'))
        w_f.write("\n")

# initialize bpf
b = BPF(text=bpf_text)

#trace read
b.attach_kprobe(event="vfs_read", fn_name="trace_vfs_entry")
b.attach_kprobe(event="ext4_file_read_iter", fn_name="trace_ext4_file_readwrite_entry")
b.attach_kprobe(event="generic_file_read_iter", fn_name="trace_generic_readwrite_entry")
b.attach_kretprobe(event="generic_file_read_iter", fn_name="trace_generic_readwrite_ret")
b.attach_kretprobe(event="ext4_file_read_iter", fn_name="trace_ext4_file_op_ret")
b.attach_kretprobe(event="vfs_read", fn_name="trace_vfs_return")

#trace write
b.attach_kprobe(event="vfs_write", fn_name="trace_vfs_entry")
b.attach_kprobe(event="ext4_file_write_iter", fn_name="trace_ext4_file_readwrite_entry")
b.attach_kprobe(event="__generic_file_write_iter", fn_name="trace_generic_readwrite_entry")
b.attach_kprobe(event="generic_perform_write", fn_name="trace_generic_perfrom_write_entry")
b.attach_kprobe(event="generic_file_direct_write", fn_name="trace_generic_direct_write_entry")
b.attach_kretprobe(event="generic_file_direct_write", fn_name="trace_generic_direct_write_ret")
b.attach_kretprobe(event="generic_perform_write", fn_name="trace_generic_perfrom_write_ret")
b.attach_kretprobe(event="__generic_file_write_iter", fn_name="trace_generic_readwrite_ret")
b.attach_kretprobe(event="ext4_file_write_iter", fn_name="trace_ext4_file_op_ret")
b.attach_kretprobe(event="vfs_write", fn_name="trace_vfs_return")

#trace fsync
b.attach_kprobe(event="vfs_fsync_range", fn_name="trace_vfs_entry")
b.attach_kprobe(event="ext4_sync_file", fn_name="trace_ext4_file_sync_entry")
b.attach_kprobe(event="file_write_and_wait_range", fn_name="trace_ext4_sync_write_wait_entry")
b.attach_kprobe(event="jbd2_complete_transaction", fn_name="trace_ext4_sync_jbd2_comp_entry")
b.attach_kretprobe(event="jbd2_complete_transaction", fn_name="trace_ext4_sync_jbd2_comp_ret")
b.attach_kretprobe(event="file_write_and_wait_range", fn_name="trace_ext4_sync_write_wait_ret")
b.attach_kretprobe(event="ext4_sync_file", fn_name="trace_ext4_file_op_ret")
b.attach_kretprobe(event="vfs_fsync_range", fn_name="trace_vfs_return")
#b.trace_print()

# header
if min_ms == 0:
	print("Tracing ext4 operations")
else:
        print("Tracing ext4 operations slower than %d ms" % min_ms)


# read events
if args.output:
        b["events"].open_perf_buffer(store_event_data, page_cnt=4096)
else:
	print("%-8s %-12s %-14s %-6s %2s %-7s %-8s %-7s %-7s %-8s %-11s %-11s %-7s %-5s %s" % ("TIME", "CONTAINER", "COMM", "PID", "T",
        "BYTES", "OFF_KB", "LAT(ms)", "VFS(ms)", "EXT4(ms)", "GEN/WR(ms)", "BIO/JBD2(ms)", "DIO(ms)", "DEV", "FILENAME"))

        b["events"].open_perf_buffer(print_event, page_cnt=512)

seconds = 0
exiting = 0
while (1):
	try:
       		sleep(1)
       		seconds += 1
	except KeyboardInterrupt:
        	exiting = 1
 
        b.perf_buffer_poll(timeout=1000)
	
        if args.time and seconds >= args.time:
                exiting = 1

        if exiting:
		if args.output:
			w_f.close()
                exit()
