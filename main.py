import threading
import random
import time
from queue import Queue, Full, Empty
task_queue = Queue(maxsize = 10)
reslock = threading.Lock()
res = []
flag = threading.Event()
print_lock = threading.Lock()

class TextTaski:
    def __init__(self, task_id,text,oper):
        self.task_id = task_id
        self.text = text
        self.oper = oper

    def __str__(self):
        return f'Task {self.task_id}: {self.oper}'

class TextRes:
    def __init__(self, task_id, oper, res_data):
        self.task_id = task_id
        self.oper = oper
        self.res_data = res_data
        self.times = time.strftime("%H:%M:%S")

    def __str__(self):
        return f'{self.times} Task {self.task_id} - {self.oper}: {self.res_data}'

class Producer(threading.Thread):
    def __init__(self,producer_id, counter):
        super().__init__()
        self.producer_id = producer_id
        self.counter = counter
        self.task_sozd = 0

    def run(self):
        with print_lock:
            print(f'Producer {self.producer_id} запущен, создаст {self.counter} задач')
        try:
            with open('texts.txt', 'r', encoding='utf-8') as file:
                texts = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            with print_lock:
                print("Файл texts.txt не найден")

        operations = ['cwords', 'cletters', 'reverse']
        for i in range(self.counter):
            if flag.is_set():
                with print_lock:
                    print(f'Producer {self.producer_id} получен сигнал завершения')
                break
            task_id = self.producer_id*1000 + i
            text = random.choice(texts)
            oper= random.choice(operations)
            task = TextTaski(task_id,text,oper)
            try:
                task_queue.put(task,timeout=1)
                self.task_sozd+=1
                with print_lock:
                    print(f'Producer {self.producer_id} создал {task}')
                time.sleep(random.uniform(0.3, 0.8))
            except Full:
                with print_lock:
                    print("Очередь переполнена")
                time.sleep(1)
        with print_lock:
            print(f'Producer {self.producer_id} завершил работу, создано {self.task_sozd} задач')

class Consumer(threading.Thread):
    def __init__(self,consumer_id):
        super().__init__()
        self.consumer_id = consumer_id
        self.obtask_count = 0

    def run(self):
        with print_lock:
            print(f'Consumer {self.consumer_id} запущен')
        while not flag.is_set() or not task_queue.empty():
            try:
                task = task_queue.get(timeout=1)
                result_data = self.ob_task(task)
                result = TextRes(task.task_id, task.oper, result_data)
                # with print_lock:
                #    print(f'Результат: {result}')
                with reslock:
                    res.append(result)
                self.obtask_count += 1
                with print_lock:
                    print(f'Consumer {self.consumer_id} завершил Task #{task.task_id}')
                time.sleep(random.uniform(0.5, 1.5))
            except Empty:
                if not flag.is_set():
                    continue
                else:
                    break
        with print_lock:
            print(f'Consumer {self.consumer_id} завершил работу, обработано {self.obtask_count} задач')

    def ob_task(self,task):
        text = task.text
        if task.oper == 'cwords':
            words = text.split()
            return f'Words: {len(words)}'
        elif task.oper == 'cletters':
            letters = [c for c in text if c.isalpha()]
            return f'Letters: {len(letters)}'
        elif task.oper == 'reverse':
            return f'Reversed: {text[::-1]}'
        else:
            return "Неизвестная операция"

# def statistic():
#     oper_count = {}
#     for result in res:
#         if result.oper not in oper_count:
#             oper_count[result.oper] = 1
#         else:
#             oper_count[result.oper] += 1
#     print(f'всего задач: {len(res)}')
#     for op, count in oper_count.items():
#         print(f"  {op}: {count} задач")

def main():
    start_time = time.time()
    num_producers = 2
    num_consumers = 3
    tasks_per_producer = 8
    producers = []
    consumers = []
    for i in range(num_consumers):
        consumer = Consumer(i + 1)
        consumers.append(consumer)
        consumer.start()
    for i in range(num_producers):
        producer = Producer(i + 1, tasks_per_producer)
        producers.append(producer)
        producer.start()
    try:
        for producer in producers:
            producer.join()
        flag.set()
        for consumer in consumers:
            consumer.join()
        print("Все потоки завершены")
        # statistic()
        end_time = time.time()
        total_time = end_time - start_time
        print(f'Время выполнения: {total_time:.2f}')
    except KeyboardInterrupt:
        flag.set()

if __name__ == "__main__":
    main()