import subprocess
import multiprocessing as mp
import multiprocessing.managers
import queue
import time

import numpy

SLAVE_RETURN_DELAY = 3
JOB_QUEUE_NAME = 'get_job_queue'
RES_QUEUE_NAME = 'get_result_queue'


""" Connects to a host from remote nodes and begins executing jobs.
"""

def make_slave_manager(ip, port, authorization_key):
    """ Sets up a SlaveManagThe slave manager is responsible for connecting to the
        server and obtain the queues needed to both run jobs
        and post results back.

        Arguments:
        ip -- the ip address (or fully qualified domain name)
              of master that slave connects to
        port -- the port over which a connection attempt is made
        authorization_key -- program secret used to identify correct server

        Returns:
        The slave manager
    """

    class ServerQueueManager(multiprocessing.managers.SyncManager):
        pass

    ServerQueueManager.register(JOB_QUEUE_NAME)
    ServerQueueManager.register(RES_QUEUE_NAME)

    manager = ServerQueueManager(address=(ip, port), authkey=authorization_key.encode("utf-8"))
    manager.connect()

    return manager

def slave_node_driver(shared_job_queue, shared_result_queue, n_jobs_per_node):
    """ Starts slave processes on a single node

        Arguments:
        shared_job_queue -- the job queue to obtain jobs from
        shared_result_queue -- the queue that results are sent to
        n_jobs_per_node -- the number of slave processes to start per node
    """
    procs = []
    for i in range(n_jobs_per_node):
        proc = mp.Process(target=slave, args=(shared_job_queue, shared_result_queue))
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()

def slave(job_queue, result_queue):
    """ Continously run commands from job queue and
        put results into result queue. The result queue
        is used for accounting when everything is done.

        This function is called from slave_node_driver

        Arguments:
        job_queue -- the queue from which to get jobs
        result_queue -- the queue to put results into
    """
    while True:
        try:
            job, cmd = job_queue.get_nowait() # get job from job queue
            out, err, time = execute(cmd)
            result = (job, time, out, err)
            result_queue.put(result) # dump result in result queue
        except queue.Empty:
            return

def execute(command):
    """ Executes command given an argument through a shell

        This command will also calculate the time it took for
        execution (sans SLAVE_RETURN_DELAY) and return it

        Arguments:
        command -- command line arguments to run a job
    """
    t0 = numpy.asarray(time.time(),dtype=numpy.float64)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    t1 = numpy.asarray(time.time(),dtype=numpy.float64)

    time.sleep(SLAVE_RETURN_DELAY)

    return output, error, t1 - t0

if __name__ == '__main__':
    manager = make_slave_manager("$HOSTNAME", $PORT, "$AUTHKEY")
    job_queue = manager.get_job_queue()
    result_queue = manager.get_result_queue()
    slave_node_driver(job_queue, result_queue, $JOBS_PER_NODE)
