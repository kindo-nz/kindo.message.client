# Kindo Message Client

A multi-language client library for sending structured messages to the Kindo Producer Lambda service.

## Overview

The Kindo Message Client provides a standardized way for applications to send messages to the Kindo messaging system. It supports multiple programming languages and ensures consistent message formatting through a shared JSON schema.

## Features

- **Multi-language Support**: Client implementations for various programming languages
- **Standardized Schema**: Consistent message format across all clients
- **AWS Authentication**: Secure message transmission using AWS SigV4 signing
- **Message Validation**: Built-in schema validation for message structure
- **Security Levels**: Configurable data protection for sensitive payloads
- **Multiple Behaviors**: Support for instant, scheduled, deferred, and long-term message delivery

## Message Schema

All clients use a standardized message format defined in `schemas/producer_payload.json`:

```json
{
  "event_type": "string",
  "message_channel": "string", 
  "behavior": "instant|scheduled|deferred|long_term",
  "security_level": "normal|sensitive",
  "payload": {}
}
```

### Security Levels

The `security_level` field controls how payload data is handled:

- **`"normal"`** (default): Payload stored as-is for full visibility in message tracking
- **`"sensitive"`**: Payload automatically hashed using SHA256 before storage to protect sensitive data

This feature ensures that sensitive information like credit card numbers, personal data, or confidential business information is not stored in plain text while still allowing normal message processing.

## Available Clients

### Python Client
- **Location**: `clients/kindo_message_python_client/`
- **Documentation**: [Python Client README](clients/kindo_message_python_client/README.md)
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
│   ├── kindo_message_python_client/  # Python client
│   └── [future clients]    # Other language implementations
└── README.md               # This file
```

## Contributing

### Git Workflow

We follow a strict Git workflow to ensure code quality and maintainability:

#### Branch Strategy
- **`main`**: Production-ready code
- **`staging`**: Pre-production testing
- **`development`**: Active development branch
- **`feature/*`**: Feature branches (must be created from `development`)

#### Pull Request Process

1. **Create Feature Branch**: Always create feature branches from `development`
   ```bash
   git checkout development
   git pull origin development
   git checkout -b feature/your-feature-name
   ```

2. **Development**: Make your changes and commit them to your feature branch

3. **Create PR**: Create a Pull Request targeting the `development` branch
   - **Important**: PRs targeting `staging` or `main` will be automatically declined
   - Include a clear description of your changes
   - Reference any related issues

4. **Code Review**: Wait for code owner approval
   - All PRs require at least one code owner approval
   - Address any review comments

5. **Merge Process**: 
   - After approval, PR will be merged to `development`
   - Code will then be promoted to `staging` for testing
   - Finally, changes will be merged to `main` for production

#### Adding New Language Clients

When adding new language clients:
1. Create a new directory under `clients/`
2. Implement the client following the established patterns
3. Include comprehensive documentation and tests
4. Ensure compatibility with the shared schema
5. Follow the Git workflow above

#### Code Standards

- Follow the established patterns in existing clients
- Include comprehensive tests for new functionality
- Update documentation for any API changes
- Ensure all code passes linting and tests
- Maintain backward compatibility when possible