# Kindo Message Client

A multi-language client library for sending structured messages to the Kindo Producer Lambda service.

## Overview

The Kindo Message Client provides a standardized way for applications to send messages to the Kindo messaging system. It supports multiple programming languages and ensures consistent message formatting through a shared JSON schema.

## Features

- **Multi-language Support**: Client implementations for various programming languages
- **Standardized Schema**: Consistent message format across all clients
- **AWS Authentication**: Secure message transmission using AWS SigV4 signing
- **Message Validation**: Built-in schema validation for message structure
- **Multiple Behaviors**: Support for instant, scheduled, deferred, and long-term message delivery

## Message Schema

All clients use a standardized message format defined in `schemas/producer_payload.json`:

```json
{
  "event_type": "string",
  "message_channel": "string", 
  "behavior": "instant|scheduled|deferred|long_term",
  "payload": {}
}
```

## Available Clients

### Python Client
- **Location**: `clients/python/`
- **Documentation**: [Python Client README](clients/python/README.md)
- **Features**: Full AWS SigV4 authentication, JSON schema validation, environment-based configuration

*More language implementations coming soon...*

## Getting Started

1. Choose your preferred language client from the `clients/` directory
2. Follow the specific installation and usage instructions in the client's README
3. Configure your environment variables (typically `KINDO_MESSAGE_PRODUCER_URL`)
4. Start sending messages!

## Architecture

```
kindo.message.client/
├── schemas/                 # Shared message schemas
│   └── producer_payload.json
├── clients/                 # Language-specific implementations
│   ├── python/             # Python client
│   └── [future clients]    # Other language implementations
└── README.md               # This file
```

## Contributing

When adding new language clients:
1. Create a new directory under `clients/`
2. Implement the client following the established patterns
3. Include comprehensive documentation and tests
4. Ensure compatibility with the shared schema

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
