# envault

> Lightweight CLI for encrypting and syncing `.env` files across machines

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/):

```bash
pipx install envault
```

---

## Usage

**Encrypt and push your `.env` file:**

```bash
envault push --file .env --remote s3://my-bucket/project
```

**Pull and decrypt on another machine:**

```bash
envault pull --remote s3://my-bucket/project --out .env
```

**Initialize a new vault with a passphrase:**

```bash
envault init --passphrase "your-secret-passphrase"
```

Envault encrypts your `.env` file using AES-256 before syncing, ensuring secrets are never stored or transmitted in plaintext. The passphrase never leaves your machine.

---

## Supported Backends

- Amazon S3
- Local filesystem
- *(More coming soon)*

---

## Requirements

- Python 3.8+
- AWS credentials configured (for S3 backend)

---

## License

[MIT](LICENSE) © 2024 envault contributors