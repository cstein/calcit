import logging
import multiprocessing
import multiprocessing.managers
import os
import socket
import subprocess
import time
from Queue import Queue

import numpy

from .util import substitute_file, create_scratch_directory, CalcItJobCreateError

# delays in seconds to different processes
MANAGER_SHUTDOWN_DELAY = 3

JOB_QUEUE_NAME = 'get_job_queue'
RES_QUEUE_NAME = 'get_result_queue'

logging.basicConfig(level=logging.INFO)


def process_jobs(port, authorization_key, jobs, nodes, jobs_per_node, work_dir, remote_shell, global_paths, do_execute):
    """ Parallel processing of jobs that are given in a script, the name of
        which is in the filenames list and located in a directory given in the
        list of directories.

        Arguments:
        port -- the port used for communation
        authorization_key -- program secret used to identify correct server
        jobs -- the jobs to execute
        nodes -- list of nodes to use during processing
        jobs_per_node -- number of jobs to start per node
        work_dir -- the work directory where the slave should be launched from
        remote_shell -- the remote shell to use when connecting to nodes
        global_paths -- directories used to find calcit and its data folders.
                        NB! This is different from work_dir and scratch directories
                            in that global_paths have nothing to do with computations
        do_execute -- whether or not to actually execute calculations
    """

    def send_jobs_to_queue(jobs, job_queue):
        """ Sends jobs to the job queue specified on input

            We wrap it like this so we can shutdown the server appropriately
            without causing hangups

            Raises:
            CalcItJobCreateError if there was an error creating the job

            Arguments:
            jobs -- the jobs to be processed
            job_queue -- the queue to submit the jobs to
        """
        total_job_count = len(jobs)
        logging.info("Submitting {0:3d} jobs to the queue.".format(total_job_count))
        for job_index, job in enumerate(jobs, start=1):
            job_str = repr(job)
            try:
                command = job.cmd(global_paths)
            except:
                raise
            else:
                cmd = (job_str, command)
                logging.info("Job '{0[0]:s}' added to queue. Command is '{0[1]:s}'".format(cmd))
                if do_execute:
                    job_queue.put(cmd)

        return total_job_count

    def retrieve_jobs_from_queue(total_job_count, result_queue):
        """ Retrieve jobs from the processing queue

            Arguments:
            total_job_count -- the number of jobs we expect
            result_queue -- the queue to retrieve jobs from
        """
        jobs_completed = 0
        while jobs_completed < total_job_count:
            if not do_execute:
                break
            job_name, time_to_complete, stdout, stderr = result_queue.get()
            jobs_completed += 1
            logging.info("Finished '{2:s}' ({0:d} of {1:3d}) in {3:9.2f}s.".format(jobs_completed, total_job_count, job_name, time_to_complete))
            if len(stdout[:-1]) > 0:
                logging.info("{0:s} STDOUT: {1:s}".format(job_name, stdout[:-1]))

    if not do_execute:
        return

    # get hostname of running script to pass to slaves
    host = socket.gethostname()

    # create manager and queues
    # logging.info("Creating manager".format())
    server, job_queue, result_queue = start_server(port, authorization_key)

    # start the slaves on the remote nodes
    start_slaves(host, port, authorization_key, nodes, jobs_per_node, work_dir, remote_shell, global_paths)

    try:
        # send jobs to job queue
        total_job_count = send_jobs_to_queue(jobs, job_queue)

        # retrieve results from slaves
        retrieve_jobs_from_queue(total_job_count, result_queue)
    finally:
        # shutdown server.
        stop_server(server)


def start_server(port, authorization_key):
    """ Starts the server on the master node

        Arguments:
        port -- Port to use for communication
        authorization_key -- program secret used to identify correct server
    """
    logging.info("Starting server on port {0:d} with authorization key '{1:s}'".format(port, authorization_key))

    manager = make_server_manager(port, authorization_key)
    manager.start()
    job_queue = manager.get_job_queue()
    result_queue = manager.get_result_queue()
    return manager, job_queue, result_queue


def stop_server(manager):
    """ Stops the server on the master node when all jobs have finished

        Arguments:
        manager -- the server to stop
    """
    logging.info("Shutting down server.")
    time.sleep(MANAGER_SHUTDOWN_DELAY)  # needed to prevent hanging
    manager.shutdown()


def make_server_manager(port, authorization_key):
    """ Create a manager for the server, listening on the given port.

        Return a manager object with get_job_q and get_result_q
        methods.

        Arguments:
        port -- Port to use for communication
        authorization_key -- program secret used to identify correct server

        Returns:
        Manager to process jobs
    """

    job_queue = Queue()
    result_queue = Queue()

    class JobQueueManager(multiprocessing.managers.SyncManager):
        pass

    JobQueueManager.register(JOB_QUEUE_NAME, callable=lambda: job_queue)
    JobQueueManager.register(RES_QUEUE_NAME, callable=lambda: result_queue)

    manager = JobQueueManager(address=('', port), authkey=authorization_key)

    return manager


def start_slaves(server, port, authorization_key, nodes, jobs_per_node, work_dir, remote_shell, global_paths):
    """ Start slave prcesses on remote computers.

        Arguments:
        server -- the master server that the slaves connect to
        port -- the port used for communation
        authorization_key -- program secret used to identify correct server
        nodes -- list of nodes to use during processing
        jobs_per_node -- number of jobs to start per node
        work_dir -- the work directory where the slaves should be launched from
        remote_shell -- the remote shell to use when connecting to nodes
        global_paths -- directories used to find calcit and its data folders.
                        NB! This is different from work_dir and scratch directories
                            in that global_paths have nothing to do with computations
    """

    share_path = global_paths['share']
    # write scripts to start slave nodes
    write_slave_python_script(server, port, authorization_key, jobs_per_node, share_path)
    slave_execute_script = write_slave_execute_script(work_dir, remote_shell, share_path)

    procs = []
    for node in nodes:
        command_to_execute = "./{0} {1}".format(slave_execute_script, node)
        logging.info("executing command '{0:s}' on node {1:s}".format(command_to_execute, node))
        process = multiprocessing.Process(target=execute, args=(command_to_execute,))
        procs.append(process)
        process.start()


def execute(command, is_slave=False):
    """ Executes command given an argument through a shell

        If is_slave is True there will be a delay added through
        the global constant CLIENT_RETURN_DELAY

        This command will also calculate the time it took for
        execution (sans CLIENT_RETURN_DELAY) and return it

        Arguments:
        command -- command line arguments to run a job
        is_slave -- if True then the execute process will be delayed before returning
    """
    t0 = numpy.asarray(time.time(),dtype=numpy.float64)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    t1 = numpy.asarray(time.time(),dtype=numpy.float64)

    return output, error, t1 - t0


def write_slave_execute_script(work_dir, remote_shell, share_path):
    """ Writes the slave shell script that launches worker slaves
        on remote nodes.

        Uses start_slaves.bash from the data directory.

        TODO: make it work for other shells too.

        Arguments:
        work_dir -- the work directory where the slaves should be launched from
        remote_shell -- the remote shell to use when connecting to nodes
        share_path -- the directory of common template files

        Returns:
        filename of slave python script
    """
    if remote_shell != 'ssh':
        raise NotImplementedError("You specified remote shell '{0}' which is not implemented.".format(remote_shell))

    filename_in = os.path.join(share_path, "start_slaves.bash")
    filename_out = "start_slaves.sh"

    substitutions = {'WORK_DIR': work_dir, 'REMOTE_SHELL': remote_shell}
    substitute_file(filename_in, filename_out, substitutions)

    os.chmod(filename_out, 0744)

    return filename_out


def write_slave_python_script(server, port, authorization_key, jobs_per_node, share_path):
    """ Writes the slave script that connects to the server.

        Uses slave.py from the share directory.

        Arguments:
        server -- adress of the master that the slaves connect to
        port -- the port used for communation
        authorization_key -- program secret used to identify correct server
        jobs_per_node -- the number of jobs each node can run
        share_path -- the directory of common template files

        Returns:
        filename of slave python script
    """

    filename_in = os.path.join(share_path, "slave.py")
    filename_out = "slave.py"

    substitutions = {'PORT': str(port),
                     'HOSTNAME': server,
                     'AUTHKEY': authorization_key,
                     'JOBS_PER_NODE': str(jobs_per_node)}
    substitute_file(filename_in, filename_out, substitutions)

    return filename_out
