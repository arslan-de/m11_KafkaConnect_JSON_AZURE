import sys
import getopt

from confluent_kafka import Consumer, KafkaException, KafkaError


def print_assignment(consumer, partitions):
    print('Assignment:', partitions)


if __name__ == "__main__":
    optlist, argv = getopt.getopt(sys.argv[1:], "T:")

    group = argv[0]
    topics = argv[1:]

    print(f"Group {group}; Topics {topics}")

    conf = {
        'bootstrap.servers': "kafka.confluent.svc.cluster.local:9092",
        'group.id': group,
        'client.id': 'python-consumer',
        'request.timeout.ms': 60000,
        'session.timeout.ms': 60000,
        'default.topic.config': {'auto.offset.reset': 'earliest'}
    }

    c = Consumer(conf)

    # Subscribe to topics
    c.subscribe(topics, on_assign=print_assignment)

    # Read messages from Kafka, print to stdout
    try:
        while True:
            msg = c.poll(timeout=100.0)
            if msg is None:
                continue
            if msg.error():
                # Error or event
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    print('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                else:
                    # Error
                    raise KafkaException(msg.error())
            else:
                # Proper message
                print(msg.value())

    except KeyboardInterrupt:
        print('%% Aborted by user\n')

    finally:
        # Close down consumer to commit final offsets.
        c.close()
