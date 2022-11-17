__all__ = ('KafkaOperator',)

import json
import typing

import confluent_kafka as kafka
import confluent_kafka.admin as kafka_admin

from ..logger import LOG

LOG.debug('Version of confluent_kafka client = %s' % kafka.__version__)


class KafkaOperator:
    def __init__(self, kafka_config):
        """
        Parameter reference: https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md

        :param kafka_config:
        host = [
            {host: kafka_server_1, port: 9092}
        ]
        """
        self._config = json.loads(json.dumps(kafka_config, ensure_ascii=False))  # deep copy

        if 'host' in kafka_config:
            self._config = {
                'bootstrap.servers': ','.join(['{host}:{port}'.format(**i) for i in kafka_config.pop('host')]),
            }
        LOG.debug("Kafka connection info: " + str(self._config))

    def admin_client(self, *args, **kwargs):
        config_admin = {**self._config}
        a = kafka_admin.AdminClient(config_admin)
        return a

    def create_topic(self, topic: str, num_partitions=3, replication_factor=1, *args, **kwargs):
        """Note: In a multi-cluster production scenario, it is more typical to use a replication_factor of 3 for durability."""
        a = self.admin_client()
        new_topic = kafka_admin.NewTopic(topic, num_partitions=num_partitions, replication_factor=replication_factor)

        # Call create_topics to asynchronously create topics. A dict of <topic,future> is returned.
        fs = a.create_topics([new_topic])

        # Wait for each operation to finish.
        for topic, f in fs.items():
            try:
                f.result()  # The result itself is None
                LOG.info("Topic {} created".format(topic))
            except Exception as e:
                LOG.error("Failed to create topic {}: {}".format(topic, e))
                return False
            finally:
                a.close()

        return True

    def producer_deliver(self, topic: str, generator: typing.Iterator[str], func_callback: callable = None, *args, **kwargs):
        # func_callback should be a function that takes two arguments: err and msg
        config_producer = {**self._config}
        p = kafka.Producer(config_producer)

        def delivery_report(err, msg):
            """ Called once for each message produced to indicate delivery result. Triggered by poll() or flush(). """
            if err is not None:
                LOG.error('Kafka msg delivery failed: {}'.format(err))
            else:
                LOG.debug('Kafka msg delivered to {} [{}]'.format(msg.topic(), msg.partition()))

        if func_callback is None:
            func_callback = delivery_report

        for data in generator:  # some data from the generator
            # Trigger any available delivery report callbacks from previous produce() calls
            p.poll(0)

            # Asynchronously produce a message, the delivery report callback
            # will be triggered from poll() above, or flush() below, when the message has
            # been successfully delivered or failed permanently.
            p.produce(topic, data.encode('utf-8'), callback=func_callback)

        # Wait for any outstanding messages to be delivered and delivery report callbacks to be triggered.
        p.flush()

    def consumer_generator(self, topics_subscribe: list, group_id: str = None, poll_timeout: float = 1.0, *args, **kwargs) -> typing.Iterator[str]:
        config_consumer = {'auto.offset.reset': 'earliest', **self._config}
        if group_id is not None:
            config_consumer['group.id'] = group_id
        c = kafka.Consumer(config_consumer)

        c.subscribe(topics_subscribe)
        while True:
            msg = c.poll(poll_timeout)

            if msg is None:
                continue
            elif msg.error():
                code = msg.error().code()
                if code == kafka.KafkaError._PARTITION_EOF:
                    pass
                LOG.error("Kafka consumer: {}".format(msg.error()))
                continue

            data = msg.value().decode('utf-8')
            LOG.debug('Received message: {}'.format(data))
            yield data

        c.close()
