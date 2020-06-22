import json
import time
import numpy as np
import h5py
import zmq

from experimentor.core.meta import ExperimentorProcess


class MovieSaver(ExperimentorProcess):
    def __init__(self, file, max_memory, frame_rate, saving_event, url, topic=''):
        super().__init__()
        print(url)
        self.file = file
        self.max_memory = max_memory
        self.saving_event = saving_event
        self.frame_rate = frame_rate
        self.topic = topic
        self.url = url

        self.start()

    def run(self) -> None:
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect(self.url)
        socket.setsockopt(zmq.SUBSCRIBE, self.topic.encode('utf-8'))

        with h5py.File(self.file, "a") as f:
            # now = str(datetime.now())
            g = f.create_group('data')
            i = 0
            j = 0
            first = True
            while not self.saving_event.is_set():
                event = socket.poll(0)
                if not event:
                    time.sleep(.005)
                    continue
                topic = socket.recv_string()
                metadata = socket.recv_json(flags=0)
                msg = socket.recv(flags=0, copy=True, track=False)
                buf = memoryview(msg)
                img = np.frombuffer(buf, dtype=metadata['dtype'])
                img = img.reshape(metadata['shape']).copy()

                if first:  # First time it runs, creates the dataset
                    x = img.shape[0]
                    y = img.shape[1]
                    allocate = int(self.max_memory / img.nbytes * 1024 * 1024)
                    d = np.zeros((x, y, allocate), dtype=img.dtype)
                    dset = g.create_dataset('timelapse', (x, y, allocate), maxshape=(x, y, None),
                                            compression='gzip', compression_opts=1,
                                            dtype=img.dtype)  # The images are going to be stacked along the z-axis.
                    first = False

                    meta = {
                        'fps': self.frame_rate,
                        'start': time.time()
                    }
                d[:, :, i] = img
                i += 1
                if i == allocate:
                    dset[:, :, j:j + allocate] = d
                    dset.resize((x, y, j + 2*allocate))
                    d = np.zeros((x, y, allocate), dtype=img.dtype)
                    i = 0
                    j += allocate
            if i != 0:
                dset[:, :, j:j + i] = d[:, :, :i]

            meta.update({
                'end': time.time(),
                'frames': j+i,
                'allocate': allocate,
            })
            meta = json.dumps(meta)
            g.create_dataset('metadata', data=meta.encode("ascii", "ignore"))
