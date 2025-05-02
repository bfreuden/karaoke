from abc import ABC, abstractmethod
from fastapi import WebSocket
from asyncio import Queue

class ProgressNotifier(ABC):

    def __init__(self, steps):
        self.step = 1
        self.steps = steps

    def progress(self):
        self.step += 1

    @abstractmethod
    def notify(self, message):
        pass  # This is an abstract method, no implementation here.

class PrintProgressNotifier(ProgressNotifier):

    def __init__(self, steps):
        super().__init__(steps)

    def notify(self, message):
        print(f"-- ({self.step}/{self.steps}) {message}")
        self.progress()


class WebSocketProgressNotifier(ProgressNotifier):

    def __init__(self, steps, websocket: WebSocket, queue: Queue):
        super().__init__(steps)
        self.websocket = websocket
        self.queue = queue
        self.print_notifier = PrintProgressNotifier(steps)

    def notify(self, message):
        self.print_notifier.notify(message)
        # self.websocket.send_json({
        #     'step': self.step,
        #     'steps': self.steps,
        #     'message': message,
        # })
        print(f"putting in queue {self.queue}")
        self.queue.put_nowait({
            'step': self.step,
            'steps': self.steps,
            'message': message,
        })
        print(f"put in queue {self.queue}")
        self.progress()
