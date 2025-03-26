# RabbitMQ-learn

## RabbitMQ

### Standard RabbitMQ message flow

1. The producer publishes a message to the exchange.

1. The exchange receives the message and is now responsible for the routing of the message.

1. Binding must be set up between the queue and the exchange. In this case, we have bindings to two different queues from the exchange. The exchange routes the message into the queues.

1. The messages stay in the queue until they are handled by a consumer.

1. The consumer handles the message.

![alt text](assets/image.png)

### [Exchange Types](https://www.cloudamqp.com/blog/part4-rabbitmq-for-beginners-exchanges-routing-keys-bindings.html)

- RabbitMQ supports several built-in exchange types, each designed to handle specific messaging patterns.

1. **Direct Exchanges**

    - **Purpose**: Direct exchanges route messages based on an exact match between routing keys.
    - **Routing Key**: The message is delivered to a queue if the routing key matches exactly with one of the bindings attached to that queue.
    - **Use Case**: Simple scenarios where each message needs to be delivered to exactly one consumer.

    ![alt text](assets/image%20copy.png)

    - **Scenario 1**

      - Exchange: `pdf_events`
      - Queue A: `create_pdf_queue`
      - Binding key between exchange (`pdf_events`) and Queue A (`create_pdf_queue`): pdf_create

    - **Scenario 2**

      - Exchange: `pdf_events`
      - Queue B: `pdf_log_queue`
      - Binding key between exchange (`pdf_events`) and Queue B (`pdf_log_queue`): pdf_log

    - **Example**

      - Example: A message with routing key `pdf_log` is sent to the exchange `pdf_events`. The messages is routed to `pdf_log_queue` because the routing key `pdf_log` matches the binding key `pdf_log`.
      - If the message routing key does not match any binding key, the message is discarded.

2. **Topic Exchanges**

    - **Purpose**: Topic exchanges are used for more flexible matching rules, based on regular expressions and wildcards.
    - **Routing Key**: The routing key can contain special characters like `*` (matches a single word) or `#` (matches zero or more words).
    - **Use Case**: Scenarios where you need to route messages based on patterns rather than exact matches.

    ![alt text](assets/image%20copy%202.png)

    - **Scenario 1**
    
      - The image to the right shows an example where consumer A is interested in all the agreements in Berlin.
      - Exchange: `agreements`
      - Queue A: `berlin_agreements`
      - Routing pattern between exchange (`agreements`) and Queue A (`berlin_agreements`): `agreements.eu.berlin.#`
      - Example of message routing key that matches: `agreements.eu.berlin` and `agreements.eu.berlin.store`

    - **Scenario 2**

      - Consumer B is interested in all the agreements.
      - Exchange: `agreements`
      - Queue B: `all_agreements`
      - Routing pattern between exchange (`agreements`) and Queue B (`all_agreements`): `agreements.#`
      - Example of message routing key that matches: `agreements.eu.berlin` and `agreements.us`


    - **Scenario 3**
    
      - Consumer C is interested in all agreements for European head stores.
      - Exchange: `agreements`
      - Queue C: `store_agreements`
      - Routing pattern between exchange (`agreements`) and Queue C (`store_agreements`): `agreements.eu.*.store`
      - Example of message routing keys that will match: `agreements.eu.berlin.store` and `agreements.eu.stockholm.store`

    - **Example**
      
      - A message with routing key `agreements.eu.berlin` is sent to the exchange agreements. The messages are routed to the queue berlin_agreements because the routing pattern of `agreements.eu.berlin.#` matches the routing keys beginning with `agreements.eu.berlin`. The message is also routed to the queue `all_agreements` because the routing key `agreements.eu.berlin` matches the routing pattern `agreements.#`.

3. **Fanout Exchanges**

    - **Purpose**: Fanout exchanges broadcast messages to all queues bound to the exchange, regardless of routing keys.
    - **Routing Key**: The routing key is ignored; fanout exchanges deliver messages to every queue that has a binding with this exchange.
    - **Use Case**: Broadcasting messages to multiple consumers without concern for specific filtering or routing.

    ![alt text](assets/image%20copy%203.png)

    - **Scenario 1**

      - Exchange: `sport_news`
      - Queue A: Mobile client `queue A`
      - Binding: Binding between the exchange (`sport_news`) and Queue A (Mobile client queue A)

    - **Example**

      - A message is sent to the exchange `sport_news`. The message is routed to all queues (`Queue A`, `Queue B`, `Queue C`) because all queues are bound to the exchange. Provided routing keys are ignored.

4. **Headers Exchanges**

    - **Purpose**: Headers exchanges route messages based on message headers rather than the routing key.
    - **Routing Key**: The routing key is ignored; bindings are created using header values instead of a routing key.
    - **Use Case**: Routing messages where the decision criteria do not fit into traditional routing keys and rely more on message metadata.

    ![alt text](assets/image%20copy%204.png)

    - **Example**

      - Exchange: Binding to Queue A with arguments `(key = value)`: `format = pdf, type = report, x-match = all`
      - Exchange: Binding to Queue B with arguments `(key = value)`: `format = pdf, type = log, x-match = any`
      - Exchange: Binding to Queue C with arguments `(key = value)`: `format = zip, type = report, x-match = all`

    - **Scenario 1**

      - Message 1 is published to the exchange with header arguments (key = value): `format = pdf`, `type = report`.
      - Message 1 is delivered to Queue A because all key/value pairs match, and Queue B since `format = pdf` is a match (binding rule set to `x-match = any`).

    - **Scenario 2**

      - Message 2 is published to the exchange with header arguments of (key = value): `format = pdf`.
      - Message 2 is only delivered to Queue B. Because the binding of Queue A requires both `format = pdf` and `type = report` while Queue B is configured to match any key-value pair `(x-match = any)` as long as either `format = pdf` or `type = log` is present.

    - **Scenario 3**

      - Message 3 is published to the exchange with header arguments of (key = value): `format = zip`, `type = log`.
      - Message 3 is delivered to Queue B since its binding indicates that it accepts messages with the key-value pair `type = log`, it doesn't mind that `format = zip` since `x-match = any`.
      - Queue C doesn't receive any of the messages since its binding is configured to match all of the headers (`x-match = all`) with `format = zip`, `type = pdf`. No message in this example lives up to these criterias.
      - It's worth noting that in a header exchange, the actual order of the key-value pairs in the message is irrelevant.

### Summary

- **Direct Exchanges** route based on exact matches with routing keys, ideal for one-to-one message delivery.
- **Topic Exchanges** use wildcard patterns in routing keys to match multiple consumers.
- **Fanout Exchanges** broadcast messages to all queues bound to the exchange, suitable for scenarios where every consumer needs to receive a copy of the message.
- **Headers Exchanges** route based on headers rather than routing keys, allowing for more complex routing logic.

Understanding these exchange types is crucial when designing messaging systems in RabbitMQ. Each type serves different purposes and use cases, and choosing the right one can significantly impact system design and performance. For a detailed implementation guide and examples, refer to the full CloudAMQP blog post or official RabbitMQ documentation.

## [Naming Conventions in RabbitMQ](https://medium.com/@miralizoda.komron/naming-conventions-in-rabbitmq-84cc583e84f5#bypass)

The Medium post "Naming Conventions in RabbitMQ" by Miralizoda Komron discusses best practices and naming conventions for RabbitMQ components such as exchanges, queues, routing keys, and bindings. Here’s a summary of the key points:

### Exchanges

- **Use Descriptive Names**: Exchange names should be descriptive to indicate their purpose or type.
  - Example: `customer_event_exchange`, `user_data_exchange`.

- **Namespace Prefixes**: Include namespaces or prefixes for better organization.
  - Example: `myapp.customer_event_exchange` for an application-specific exchange.

### Queues

- **Descriptive Naming**: Similar to exchanges, queue names should be descriptive and indicate the purpose of the message queue.
  - Example: `customer_service_queue`, `user_management_queue`.

- **Avoid Hardcoded Names**: Use dynamic generation or configuration management tools to avoid hardcoding queue names in code.

### Routing Keys

- **Hierarchical Structure**: Use a hierarchical structure for routing keys, typically mimicking directory structures.
  - Example: `customer.create`, `customer.update`, `order.place`.

- **Consistency Across Applications**: Ensure consistency across applications to maintain uniformity and ease of understanding.

### Bindings

- **Documented Binding Relationships**: Clearly document the relationships between exchanges and queues via routing keys. This helps in maintaining the system and onboarding new team members.
  - Example: The `customer_event_exchange` is bound to `customer_service_queue` with a routing key `customer.create`.

- **Use of Headers and Topics**: For more complex scenarios, use headers or topics to define binding rules that are flexible and reusable.

### Common Mistakes

1. **Overly Generic Names**: Avoid overly generic names like `events`, `data`, etc.
2. **Hardcoding**: Hardcoding queue and exchange names can lead to maintenance issues.
3. **Lack of Documentation**: Not documenting bindings and routing keys leads to confusion in larger systems.

### Best Practices

- **Naming Conventions Documented**: Clearly document naming conventions for exchanges, queues, and routing keys.
- **Use Versioning or Timestamps**: For temporary queues or dynamic bindings, consider using version numbers or timestamps.
  - Example: `temp_queue_v1`, `queue_20231015`.

- **Namespace Consistency**: Maintain consistency in namespace usage across the system.
