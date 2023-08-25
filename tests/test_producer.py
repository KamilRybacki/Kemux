import ast
import logging

import kafka

import conftest
import helpers

import lib.producer.start

NUMBER_OF_SAMPLES = 100

EXPECTED_ANIMALS_TOPIC_JSON_SCHEMA = {
    'timestamp': str,
    'value': int,
    'name': str,
    'labels': dict[str, str],
}


def test_for_consistency(tests_logger: logging.Logger, use_consumer: conftest.ConsumerFactory) -> None:
    consumer: kafka.KafkaConsumer = use_consumer(lib.producer.start.TEST_TOPIC)
    assert consumer.bootstrap_connected()
    tests_logger.info('Connected to Kafka broker successfully')

    average_difference: float = 0.0
    previous_value = 0
    sum_of_values = 0

    for _ in range(NUMBER_OF_SAMPLES):
        message = next(consumer)
        decoded_json = ast.literal_eval(message.value.decode('utf-8'))
        tests_logger.info(f'Received JSON: {decoded_json}')

        helpers.verify_schema(
            schema=EXPECTED_ANIMALS_TOPIC_JSON_SCHEMA,
            data=decoded_json
        )

        current_message_value = int(decoded_json.get('value', 0))
        sum_of_values += abs(current_message_value - previous_value)
        previous_value = current_message_value

    average_difference = sum_of_values / NUMBER_OF_SAMPLES
    tests_logger.info(f'Average difference: {average_difference}')
    assert average_difference == 1  # Value should be incremented by 1 each time
