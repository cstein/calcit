import subprocess
import multiprocessing as mp
import Queue
import multiprocessing.managers

try:
    import calcit.process
except ImportError:
    exit('Could not import CalcIt. Are you sure CalcIt is available in PYTHONPATH?')

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

    ServerQueueManager.register(calcit.process.JOB_QUEUE_NAME)
    ServerQueueManager.register(calcit.process.RES_QUEUE_NAME)

    manager = ServerQueueManager(address=(ip, port), authkey=authorization_key)
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
            out, err, time = calcit.process.execute(cmd, is_slave=True)
            result = (job, time, out, err)
            result_queue.put(result) # dump result in result queue
        except Queue.Empty:
            return

if __name__ == '__main__':
    manager = make_slave_manager("$HOSTNAME", $PORT, "$AUTHKEY")
    job_queue = manager.get_job_queue()
    result_queue = manager.get_result_queue()
    slave_node_driver(job_queue, result_queue, $JOBS_PER_NODE)
